import React, { useState } from 'react';
import type { GameReplay, BenchmarkRunResult } from '../types';
import { Cpu, Play, Pause, SkipBack, RotateCcw, CheckCircle, BarChart3, Shuffle } from 'lucide-react';

interface BenchmarkReplayProps {
  onRunBenchmark: (params: { opponent: string; games: number; difficulty: string }) => Promise<{
    benchmark: BenchmarkRunResult;
    sample_replay: GameReplay;
  }>;
  onGenerateReplay: (params: { opponent_type: string; difficulty: string; agent_player: number }) => Promise<GameReplay>;
  currentReplay: GameReplay | null;
  onSelectReplay: (replay: GameReplay) => void;
  loading: boolean;
}

export const BenchmarkReplayTab: React.FC<BenchmarkReplayProps> = ({
  onRunBenchmark,
  onGenerateReplay,
  currentReplay,
  onSelectReplay,
  loading
}) => {
  const [opponent, setOpponent] = useState<string>('minimax');
  const [numGames, setNumGames] = useState<number>(50);
  const [difficulty, setDifficulty] = useState<string>('hard');
  const [benchmarkResult, setBenchmarkResult] = useState<BenchmarkRunResult | null>(null);

  // Replay playback states
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1000); // 1000ms

  const handleStartBenchmark = async () => {
    try {
      const resp = await onRunBenchmark({
        opponent,
        games: numGames,
        difficulty
      });
      setBenchmarkResult(resp.benchmark);
      onSelectReplay(resp.sample_replay);
      setCurrentStepIndex(0);
      setIsPlaying(false);
    } catch (err) {
      console.error('Benchmark execution failed:', err);
    }
  };

  const handleQuickNewReplay = async () => {
    try {
      const rep = await onGenerateReplay({
        opponent_type: opponent,
        difficulty,
        agent_player: 1
      });
      onSelectReplay(rep);
      setCurrentStepIndex(0);
      setIsPlaying(false);
    } catch (err) {
      console.error('Replay generation failed:', err);
    }
  };

  // Auto-play timer
  React.useEffect(() => {
    let timer: any = null;
    if (isPlaying && currentReplay) {
      timer = setInterval(() => {
        setCurrentStepIndex((prev) => {
          if (prev < currentReplay.moves.length - 1) {
            return prev + 1;
          } else {
            setIsPlaying(false);
            return prev;
          }
        });
      }, playbackSpeed);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isPlaying, currentReplay, playbackSpeed]);

  const activeMove = currentReplay && currentReplay.moves.length > 0
    ? currentReplay.moves[currentStepIndex]
    : null;

  const currentBoardState = activeMove
    ? activeMove.board_after
    : Array(9).fill(0);

  const totalMoves = currentReplay?.moves.length || 0;

  return (
    <div className="benchmark-replay-tab">
      {/* Top Controls & Runner */}
      <div className="benchmark-control-panel card">
        <div className="bm-grid">
          <div className="bm-col">
            <label className="form-label">Opponent Engine</label>
            <div className="pill-selector">
              <button
                className={`pill-btn ${opponent === 'minimax' ? 'active' : ''}`}
                onClick={() => setOpponent('minimax')}
              >
                Minimax (Optimal)
              </button>
              <button
                className={`pill-btn ${opponent === 'random' ? 'active' : ''}`}
                onClick={() => setOpponent('random')}
              >
                Random Opponent
              </button>
            </div>
          </div>

          <div className="bm-col">
            <label className="form-label">Agent Difficulty</label>
            <div className="pill-selector">
              <button
                className={`pill-btn ${difficulty === 'easy' ? 'active' : ''}`}
                onClick={() => setDifficulty('easy')}
              >
                Easy
              </button>
              <button
                className={`pill-btn ${difficulty === 'medium' ? 'active' : ''}`}
                onClick={() => setDifficulty('medium')}
              >
                Medium
              </button>
              <button
                className={`pill-btn ${difficulty === 'hard' ? 'active' : ''}`}
                onClick={() => setDifficulty('hard')}
              >
                Hard
              </button>
            </div>
          </div>

          <div className="bm-col">
            <label className="form-label">Games to Benchmark</label>
            <div className="pill-selector">
              {[20, 50, 100, 200].map((cnt) => (
                <button
                  key={cnt}
                  className={`pill-btn ${numGames === cnt ? 'active' : ''}`}
                  onClick={() => setNumGames(cnt)}
                >
                  {cnt}
                </button>
              ))}
            </div>
          </div>

          <div className="bm-col action-col">
            <button
              onClick={handleStartBenchmark}
              className="btn btn-primary btn-block"
              disabled={loading}
            >
              <Cpu size={16} />
              <span>{loading ? 'Evaluating Games...' : 'Execute Benchmark'}</span>
            </button>
          </div>
        </div>

        {/* Results summary bar if benchmark was run */}
        {benchmarkResult && (
          <div className="bm-results-card">
            <div className="bm-results-header">
              <span className="bm-title">
                Benchmark Results vs {benchmarkResult.opponent} ({benchmarkResult.games} games, {benchmarkResult.difficulty} Mode)
              </span>
              <span className="bm-timestamp text-slate">{benchmarkResult.timestamp}</span>
            </div>

            <div className="bm-metrics-grid">
              <div className="metric-box">
                <span className="box-val text-green">{benchmarkResult.non_loss_rate.toFixed(1)}%</span>
                <span className="box-lbl">Non-Loss Rate</span>
              </div>
              <div className="metric-box">
                <span className="box-val text-cyan">{benchmarkResult.win_rate.toFixed(1)}%</span>
                <span className="box-lbl">Win Rate ({benchmarkResult.wins})</span>
              </div>
              <div className="metric-box">
                <span className="box-val text-white">{benchmarkResult.draw_rate.toFixed(1)}%</span>
                <span className="box-lbl">Draw Rate ({benchmarkResult.draws})</span>
              </div>
              <div className="metric-box">
                <span className="box-val text-red">{benchmarkResult.loss_rate.toFixed(1)}%</span>
                <span className="box-lbl">Loss Rate ({benchmarkResult.losses})</span>
              </div>
            </div>

            {/* Proportion Bar */}
            <div className="multi-progress-bar">
              <div
                className="progress-segment seg-win"
                style={{ width: `${benchmarkResult.win_rate}%` }}
                title={`Wins: ${benchmarkResult.win_rate}%`}
              />
              <div
                className="progress-segment seg-draw"
                style={{ width: `${benchmarkResult.draw_rate}%` }}
                title={`Draws: ${benchmarkResult.draw_rate}%`}
              />
              <div
                className="progress-segment seg-loss"
                style={{ width: `${benchmarkResult.loss_rate}%` }}
                title={`Losses: ${benchmarkResult.loss_rate}%`}
              />
            </div>
          </div>
        )}
      </div>

      {/* Step-by-Step Game Replay Section */}
      <div className="replay-container card">
        <div className="card-header replay-header">
          <div className="card-title-group">
            <BarChart3 size={18} className="text-cyan" />
            <h3 className="card-title">Step-by-Step Game Replay</h3>
          </div>

          <div className="replay-header-actions">
            <button
              onClick={handleQuickNewReplay}
              className="btn btn-secondary btn-sm"
              title="Generate fresh sample game replay"
            >
              <Shuffle size={14} />
              <span>New Sample Replay</span>
            </button>
          </div>
        </div>

        {currentReplay ? (
          <div className="replay-main-grid">
            {/* Left: Replay Board */}
            <div className="replay-board-wrapper">
              <div className="replay-meta-bar">
                <span className="meta-badge">
                  {currentReplay.difficulty.toUpperCase()} AGENT ({currentReplay.agent_symbol}) vs {currentReplay.opponent_type.toUpperCase()}
                </span>
                <span className="step-counter">
                  Move {currentStepIndex + 1} of {totalMoves}
                </span>
              </div>

              <div className="tictactoe-grid replay-grid">
                {currentBoardState.map((cell, idx) => {
                  const isPlayedThisStep = activeMove?.action === idx;
                  const qVal = activeMove?.q_values?.[idx];

                  return (
                    <div
                      key={idx}
                      className={`grid-cell ${cell === 1 ? 'cell-x' : cell === 2 ? 'cell-o' : 'cell-empty'} ${
                        isPlayedThisStep ? 'cell-active-step' : ''
                      }`}
                    >
                      {cell === 1 && <span className="cell-symbol x-mark">X</span>}
                      {cell === 2 && <span className="cell-symbol o-mark">O</span>}

                      {/* Display Q-value if cell was evaluated on this move */}
                      {activeMove && activeMove.board_before[idx] === 0 && qVal !== undefined && (
                        <div
                          className={`cell-q-badge ${
                            qVal > 0 ? 'q-pos' : qVal < 0 ? 'q-neg' : 'q-zero'
                          }`}
                        >
                          Q: {qVal > 0 ? `+${qVal.toFixed(2)}` : qVal.toFixed(2)}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Playback Controls (Previous, Play, Pause, Next, Reset) */}
              <div className="playback-controls">
                <button
                  className="control-btn"
                  onClick={() => {
                    setCurrentStepIndex(0);
                    setIsPlaying(false);
                  }}
                  title="Reset to start"
                  disabled={currentStepIndex === 0}
                >
                  <SkipBack size={16} />
                </button>

                <button
                  className="control-btn"
                  onClick={() => {
                    setCurrentStepIndex((prev) => Math.max(0, prev - 1));
                    setIsPlaying(false);
                  }}
                  title="Previous move"
                  disabled={currentStepIndex === 0}
                >
                  &larr; Prev
                </button>

                <button
                  className="control-btn btn-play"
                  onClick={() => setIsPlaying(!isPlaying)}
                  title={isPlaying ? 'Pause' : 'Play'}
                >
                  {isPlaying ? <Pause size={18} /> : <Play size={18} fill="currentColor" />}
                </button>

                <button
                  className="control-btn"
                  onClick={() => {
                    setCurrentStepIndex((prev) => Math.min(totalMoves - 1, prev + 1));
                    setIsPlaying(false);
                  }}
                  title="Next move"
                  disabled={currentStepIndex >= totalMoves - 1}
                >
                  Next &rarr;
                </button>

                <button
                  className="control-btn"
                  onClick={() => {
                    setCurrentStepIndex(0);
                    setIsPlaying(false);
                  }}
                  title="Reset"
                >
                  <RotateCcw size={16} />
                </button>

                {/* Speed selector */}
                <div className="speed-selector">
                  <span className="speed-lbl">Speed:</span>
                  <select
                    className="speed-dropdown"
                    value={playbackSpeed}
                    onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                  >
                    <option value={1500}>0.7x (1.5s)</option>
                    <option value={1000}>1.0x (1.0s)</option>
                    <option value={500}>2.0x (0.5s)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Right: Step Rationale & Explanations */}
            <div className="replay-details-wrapper">
              {activeMove && (
                <div className="step-card">
                  <div className="step-card-header">
                    <span className="step-badge">
                      Move {activeMove.step + 1}: {activeMove.player_name} ({activeMove.symbol})
                    </span>
                    <span className="step-cell-target">
                      Target: Cell {activeMove.action} (Row {activeMove.row + 1}, Col {activeMove.col + 1})
                    </span>
                  </div>

                  <div className="step-explanation-box">
                    <h5 className="explanation-heading">RL Decision Rationale:</h5>
                    <p className="explanation-body">{activeMove.explanation}</p>
                  </div>

                  {/* Q-Value distribution for this state */}
                  <div className="q-distribution-table">
                    <h5 className="q-heading">Candidate Actions Evaluated:</h5>
                    <div className="q-candidates-grid">
                      {Object.entries(activeMove.q_values).map(([cellIdx, val]) => {
                        const isChosen = Number(cellIdx) === activeMove.action;
                        return (
                          <div
                            key={cellIdx}
                            className={`q-candidate-item ${isChosen ? 'chosen-action' : ''}`}
                          >
                            <span className="candidate-cell">Cell {cellIdx}</span>
                            <span
                              className={`candidate-val ${
                                val > 0 ? 'text-green' : val < 0 ? 'text-red' : 'text-slate'
                              }`}
                            >
                              {val > 0 ? `+${val.toFixed(2)}` : val.toFixed(2)}
                            </span>
                            {isChosen && <span className="chosen-pill">SELECTED</span>}
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Final Result Banner if at last move */}
                  {currentStepIndex === totalMoves - 1 && (
                    <div className="final-outcome-banner">
                      <CheckCircle size={18} className="text-green" />
                      <div>
                        <strong>Game Completed: </strong>
                        <span>{currentReplay.result_description}</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="empty-replay-state">
            <p>Run a benchmark above or generate a sample replay to inspect step-by-step game decisions.</p>
          </div>
        )}
      </div>
    </div>
  );
};
