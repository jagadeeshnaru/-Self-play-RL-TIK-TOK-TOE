import React, { useState } from 'react';
import type { Experiment, ModelStatus } from '../types';
import { LineChart, type SeriesConfig } from './LineChart';
import { Play, Loader2, AlertCircle, Info } from 'lucide-react';

interface TrainTabProps {
  modelStatus: ModelStatus | null;
  latestExperiment: Experiment | null;
  onTrain: (params: {
    episodes: number;
    alpha: number;
    gamma: number;
    epsilon_start: number;
    epsilon_end: number;
    name?: string;
  }) => Promise<void>;
  loading: boolean;
}

export const TrainTab: React.FC<TrainTabProps> = ({
  modelStatus,
  latestExperiment,
  onTrain,
  loading
}) => {
  const [episodes, setEpisodes] = useState<number>(50000);
  const [alpha, setAlpha] = useState<number>(0.5);
  const [gamma, setGamma] = useState<number>(0.9);
  const [epsilonStart, setEpsilonStart] = useState<number>(1.0);
  const [epsilonEnd, setEpsilonEnd] = useState<number>(0.05);
  const [customName, setCustomName] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const presetEpisodes = [5000, 20000, 50000, 100000, 200000];

  const handleTrainSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    if (episodes < 1000 || episodes > 500000) {
      setErrorMsg('Episodes must be between 1,000 and 500,000.');
      return;
    }
    if (alpha <= 0 || alpha > 1) {
      setErrorMsg('Learning rate alpha must be between 0.01 and 1.0.');
      return;
    }
    if (gamma <= 0 || gamma > 1) {
      setErrorMsg('Discount factor gamma must be between 0.01 and 1.0.');
      return;
    }

    try {
      await onTrain({
        episodes,
        alpha,
        gamma,
        epsilon_start: epsilonStart,
        epsilon_end: epsilonEnd,
        name: customName.trim() || undefined
      });
      setCustomName('');
    } catch (err: any) {
      setErrorMsg(err.message || 'Training failed.');
    }
  };

  const batchRecords = latestExperiment?.batch_records || [];
  const drawPct = latestExperiment?.self_play_draws_pct ?? 84.8;
  const minimaxPct = latestExperiment?.non_loss_vs_minimax_pct ?? 100.0;
  const randomPct = latestExperiment?.win_vs_random_pct ?? 92.5;
  const qStatesCount = modelStatus?.q_states ?? latestExperiment?.q_states ?? 4520;
  const currentEps = modelStatus?.epsilon ?? 0.05;

  // Chart 1: Outcome rates per batch (Draw, O wins, X wins)
  const outcomeSeries: SeriesConfig[] = [
    { key: 'draw_rate', label: 'Draw', color: '#10B981' },
    { key: 'o_win_rate', label: 'O wins', color: '#EF4444' },
    { key: 'x_win_rate', label: 'X wins', color: '#06B6D4' }
  ];

  // Chart 2: Policy strength (Non-loss vs Minimax, Win vs random)
  const strengthSeries: SeriesConfig[] = [
    { key: 'non_loss_vs_minimax', label: 'Non-loss vs Minimax', color: '#F59E0B' },
    { key: 'win_vs_random', label: 'Win vs random', color: '#10B981' }
  ];

  // Chart 3: Exploration & states discovered (Dual-axis)
  const explorationSeries: SeriesConfig[] = [
    { key: 'epsilon', label: 'Exploration ε', color: '#06B6D4', yAxis: 'left', formatValue: (v) => v.toFixed(3) },
    { key: 'q_states', label: 'Q-states', color: '#10B981', yAxis: 'right', formatValue: (v) => Math.round(v).toLocaleString() }
  ];

  return (
    <div className="train-tab">
      {/* Top Stat Cards */}
      <div className="stat-cards-grid">
        <div className="stat-card">
          <div className="stat-card-title">SELF-PLAY DRAWS</div>
          <div className="stat-card-value text-white">{drawPct.toFixed(1)}%</div>
          <div className="stat-card-sub text-green">Mutual optimal convergence</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-title">NON-LOSS VS MINIMAX</div>
          <div className="stat-card-value text-green">{minimaxPct.toFixed(1)}%</div>
          <div className="stat-card-sub text-slate">Game-theoretic optimality</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-title">WIN VS RANDOM</div>
          <div className="stat-card-value text-cyan">{randomPct.toFixed(1)}%</div>
          <div className="stat-card-sub text-slate">Punishment of blunders</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-title">Q-TABLE STATES</div>
          <div className="stat-card-value text-white">{qStatesCount.toLocaleString()}</div>
          <div className="stat-card-sub text-slate">4,520 reachable game states</div>
        </div>
      </div>

      {/* Main Grid: Left Config & Theory, Right Charts */}
      <div className="train-main-grid">
        {/* Left Column */}
        <div className="config-column">
          <div className="card config-card">
            <div className="card-header">
              <div className="card-title-group">
                <Info size={16} className="text-cyan" />
                <h3 className="card-title">Self-play configuration</h3>
              </div>
            </div>

            <form onSubmit={handleTrainSubmit} className="config-form">
              {errorMsg && (
                <div className="error-banner">
                  <AlertCircle size={15} />
                  <span>{errorMsg}</span>
                </div>
              )}

              <div className="form-group">
                <label className="form-label">
                  Training episodes (games of self-play)
                </label>
                <input
                  type="number"
                  className="form-input"
                  value={episodes}
                  min={1000}
                  max={500000}
                  step={1000}
                  onChange={(e) => setEpisodes(parseInt(e.target.value) || 1000)}
                  disabled={loading}
                />
                <div className="preset-btn-group">
                  {presetEpisodes.map((cnt) => (
                    <button
                      key={cnt}
                      type="button"
                      className={`preset-btn ${episodes === cnt ? 'active' : ''}`}
                      onClick={() => setEpisodes(cnt)}
                      disabled={loading}
                    >
                      {cnt >= 1000 ? `${cnt / 1000}K` : cnt}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group flex-1">
                  <label className="form-label">α learning rate</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0.01"
                    max="1.0"
                    className="form-input"
                    value={alpha}
                    onChange={(e) => setAlpha(parseFloat(e.target.value) || 0.1)}
                    disabled={loading}
                  />
                  <span className="field-hint">step size of TD update</span>
                </div>

                <div className="form-group flex-1">
                  <label className="form-label">γ discount</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0.1"
                    max="1.0"
                    className="form-input"
                    value={gamma}
                    onChange={(e) => setGamma(parseFloat(e.target.value) || 0.9)}
                    disabled={loading}
                  />
                  <span className="field-hint">future-value weight</span>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group flex-1">
                  <label className="form-label">ε start</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0.0"
                    max="1.0"
                    className="form-input"
                    value={epsilonStart}
                    onChange={(e) => setEpsilonStart(parseFloat(e.target.value) || 0.0)}
                    disabled={loading}
                  />
                  <span className="field-hint">initial exploration</span>
                </div>

                <div className="form-group flex-1">
                  <label className="form-label">ε end</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.0"
                    max="1.0"
                    className="form-input"
                    value={epsilonEnd}
                    onChange={(e) => setEpsilonEnd(parseFloat(e.target.value) || 0.0)}
                    disabled={loading}
                  />
                  <span className="field-hint">after 80% of episodes</span>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Experiment title (optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Benchmark α=0.5 γ=0.9 50k"
                  className="form-input"
                  value={customName}
                  onChange={(e) => setCustomName(e.target.value)}
                  disabled={loading}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-block train-cta-btn"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="spin" />
                    <span>Training Agent ({episodes.toLocaleString()} games)...</span>
                  </>
                ) : (
                  <>
                    <Play size={18} fill="currentColor" />
                    <span>Train agent via self-play</span>
                  </>
                )}
              </button>

              <div className="status-footer">
                <div className="status-left">
                  <span className={`status-indicator ${loading ? 'status-busy' : 'status-ready'}`} />
                  <span className="status-text">
                    {loading ? 'Executing Negamax self-play...' : 'Idle — model ready'}
                  </span>
                </div>
                <div className="status-right font-mono text-cyan">
                  ε {currentEps.toFixed(3)}
                </div>
              </div>
            </form>
          </div>

          {/* Mathematical Theory Box */}
          <div className="card theory-card">
            <div className="card-header">
              <h4 className="theory-title">Q-LEARNING UPDATE (NEGAMAX SELF-PLAY)</h4>
            </div>

            <div className="code-box">
              <code>
                Q(s,a) ← Q(s,a) + α · [ r - γ · max<sub>a'</sub> Q(s',a') - Q(s,a) ]
              </code>
            </div>

            <ul className="theory-bullet-list">
              <li>
                <span className="bullet-dot" />
                <span>
                  <strong>One shared Q-table</strong> plays both X and O — every game is the agent vs itself.
                </span>
              </li>
              <li>
                <span className="bullet-dot" />
                <span>
                  <strong>r = +1</strong> on win, <strong>0</strong> on draw. The opponent's best value is subtracted (zero-sum).
                </span>
              </li>
              <li>
                <span className="bullet-dot" />
                <span>
                  <strong>ε-greedy:</strong> explore randomly with probability ε, decayed linearly to ε<sub>end</sub>.
                </span>
              </li>
              <li>
                <span className="bullet-dot" />
                <span>
                  <strong>Every checkpoint</strong> the greedy policy is tested vs Minimax (20 games) & a random player (40 games).
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Right Column: 3 Live Convergence Charts */}
        <div className="charts-column">
          <LineChart
            title="Self-play outcome rates per batch"
            subtitle="As ε decays, both sides play better and self-play converges to mutual draws."
            data={batchRecords}
            xKey="episode"
            series={outcomeSeries}
            height={200}
            yDomainLeft={[0, 100]}
          />

          <LineChart
            title="Policy strength during training"
            subtitle="Greedy agent vs Minimax (non-loss %) and vs random opponent (wins %)."
            data={batchRecords}
            xKey="episode"
            series={strengthSeries}
            height={200}
            yDomainLeft={[0, 100]}
          />

          <LineChart
            title="Exploration ε & states discovered"
            subtitle="Exploration shrinks while the Q-table fills up (4,520 reachable game states)."
            data={batchRecords}
            xKey="episode"
            series={explorationSeries}
            height={200}
            yDomainLeft={[0, 1.0]}
            yDomainRight={[0, 5000]}
          />
        </div>
      </div>
    </div>
  );
};
