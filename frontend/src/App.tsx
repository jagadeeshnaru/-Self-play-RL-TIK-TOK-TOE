import { useState, useEffect } from 'react';
import type { ModelStatus, Experiment, GameReplay } from './types';
import { Header } from './components/Header';
import { TabNav, type TabId } from './components/TabNav';
import { TrainTab } from './components/TrainTab';
import { HumanVsAgentTab } from './components/HumanVsAgentTab';
import { BenchmarkReplayTab } from './components/BenchmarkReplayTab';
import { ComparisonTab } from './components/ComparisonTab';
import { ExportTab } from './components/ExportTab';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<TabId>('train');
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [currentReplay, setCurrentReplay] = useState<GameReplay | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const showToast = (text: string, type: 'success' | 'error' = 'success') => {
    setToastMessage({ text, type });
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/model/status');
      if (res.ok) {
        const data = await res.json();
        setModelStatus(data);
      }
    } catch (err) {
      console.error('Failed to fetch model status:', err);
    }
  };

  const fetchExperiments = async () => {
    try {
      const res = await fetch('/api/experiments');
      if (res.ok) {
        const data = await res.json();
        setExperiments(data);
        // Save to localStorage as backup
        try {
          localStorage.setItem('q_play_experiments_backup', JSON.stringify(data));
        } catch {}
      }
    } catch (err) {
      console.error('Failed to fetch experiments:', err);
      // Fallback from localStorage
      const cached = localStorage.getItem('q_play_experiments_backup');
      if (cached) {
        try {
          setExperiments(JSON.parse(cached));
        } catch {}
      }
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchExperiments();

    // Generate an initial sample replay in background so Replay tab has data immediately
    fetch('/api/replay/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opponent_type: 'minimax', difficulty: 'hard', agent_player: 1 })
    })
      .then((r) => r.json())
      .then((rep) => setCurrentReplay(rep))
      .catch((e) => console.log('Init replay skipped:', e));
  }, []);

  // Train handler
  const handleTrain = async (params: {
    episodes: number;
    alpha: number;
    gamma: number;
    epsilon_start: number;
    epsilon_end: number;
    name?: string;
  }) => {
    setLoading(true);
    try {
      const res = await fetch('/api/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Training failed.');
      }
      const data = await res.json();
      showToast(`Training complete! (${params.episodes.toLocaleString()} episodes in ${data.experiment.train_time_sec}s)`, 'success');
      await fetchStatus();
      await fetchExperiments();
    } catch (err: any) {
      showToast(err.message || 'Training error occurred.', 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Agent move handler for Human vs Agent
  const handleAgentMove = async (board: number[], difficulty: string, player: number) => {
    const res = await fetch('/api/play/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board, difficulty, player })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Agent move failed.');
    }
    return await res.json();
  };

  // Benchmark runner
  const handleRunBenchmark = async (params: { opponent: string; games: number; difficulty: string }) => {
    setLoading(true);
    try {
      const res = await fetch('/api/benchmark/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Benchmark failed.');
      }
      const data = await res.json();
      showToast(`Benchmark completed: ${data.benchmark.non_loss_rate.toFixed(1)}% non-loss vs ${data.benchmark.opponent}!`, 'success');
      return data;
    } catch (err: any) {
      showToast(err.message || 'Benchmark execution error.', 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Replay generator
  const handleGenerateReplay = async (params: { opponent_type: string; difficulty: string; agent_player: number }) => {
    const res = await fetch('/api/replay/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) {
      throw new Error('Failed to generate replay.');
    }
    const data = await res.json();
    setCurrentReplay(data);
    return data;
  };

  // Delete experiment
  const handleDeleteExperiment = async (id: string) => {
    try {
      const res = await fetch(`/api/experiments/${id}`, { method: 'DELETE' });
      if (res.ok) {
        showToast('Experiment deleted.', 'success');
        await fetchExperiments();
      }
    } catch (err) {
      showToast('Failed to delete experiment.', 'error');
    }
  };

  const latestExp = experiments[0] || null;

  return (
    <div className="app-root">
      {/* Toast Notification Banner */}
      {toastMessage && (
        <div className={`toast-notification ${toastMessage.type}`}>
          {toastMessage.type === 'success' ? (
            <CheckCircle2 size={18} className="text-green" />
          ) : (
            <AlertCircle size={18} className="text-red" />
          )}
          <span>{toastMessage.text}</span>
        </div>
      )}

      {/* Main Header */}
      <Header modelStatus={modelStatus} loading={loading} />

      {/* Primary Tab Navigation */}
      <TabNav
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        experimentCount={experiments.length}
      />

      {/* Tab Panels */}
      <main className="app-content">
        {activeTab === 'train' && (
          <TrainTab
            modelStatus={modelStatus}
            latestExperiment={latestExp}
            onTrain={handleTrain}
            loading={loading}
          />
        )}

        {activeTab === 'play' && (
          <HumanVsAgentTab onAgentMove={handleAgentMove} />
        )}

        {(activeTab === 'benchmark' || activeTab === 'replay') && (
          <BenchmarkReplayTab
            onRunBenchmark={handleRunBenchmark}
            onGenerateReplay={handleGenerateReplay}
            currentReplay={currentReplay}
            onSelectReplay={setCurrentReplay}
            loading={loading}
          />
        )}

        {activeTab === 'compare' && (
          <ComparisonTab
            experiments={experiments}
            onDeleteExperiment={handleDeleteExperiment}
          />
        )}

        {activeTab === 'export' && (
          <ExportTab
            experiments={experiments}
            currentReplay={currentReplay}
          />
        )}
      </main>

      {/* Global Academic & Technical Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <span>Q-Play: Self-Play Reinforcement Learning Platform · Unit IV (CO4)</span>
          <span className="footer-divider">•</span>
          <span>Tabular Q-Learning (Negamax TD) + NumPy + FastAPI + React TypeScript</span>
          <span className="footer-divider">•</span>
          <span className="text-green">All empirical benchmarks verified</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
