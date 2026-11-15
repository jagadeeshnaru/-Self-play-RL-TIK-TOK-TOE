import React from 'react';
import type { ModelStatus } from '../types';
import { Activity, Clock, Database, CheckCircle2 } from 'lucide-react';

interface HeaderProps {
  modelStatus: ModelStatus | null;
  loading: boolean;
}

export const Header: React.FC<HeaderProps> = ({ modelStatus, loading }) => {
  const isTrained = modelStatus?.status === 'Trained';
  const episodes = modelStatus?.episodes_trained ?? 0;
  const qStates = modelStatus?.q_states ?? 0;
  const trainTime = modelStatus?.train_time_sec ?? 0;

  return (
    <header className="app-header">
      <div className="header-top">
        <div className="header-info">
          <div className="badge-group">
            <span className="badge badge-green">Unit IV · Reinforcement Learning</span>
            <span className="badge badge-slate">CO4 · Python + numpy</span>
            <span className="badge badge-blue">Tabular Q-Learning</span>
          </div>
          <h1 className="header-title">
            Q-Play. Self-play RL vs Minimax
          </h1>
          <p className="header-subtitle">
            Train a tabular Q-learning agent by letting it play thousands of Tic-Tac-Toe games against itself,
            watch it converge, challenge it yourself, then benchmark it against a perfect Minimax opponent.
          </p>
        </div>

        <div className="header-metrics">
          <div className="metric-pill">
            <div className="metric-label">
              <CheckCircle2 size={13} className="metric-icon text-green" />
              <span>MODEL</span>
            </div>
            <div className={`metric-value ${isTrained ? 'text-green' : 'text-slate'}`}>
              {loading ? 'Training...' : isTrained ? 'Trained' : 'Untrained'}
            </div>
          </div>

          <div className="metric-pill">
            <div className="metric-label">
              <Activity size={13} className="metric-icon text-blue" />
              <span>EPISODES</span>
            </div>
            <div className="metric-value text-white">
              {episodes.toLocaleString()}
            </div>
          </div>

          <div className="metric-pill">
            <div className="metric-label">
              <Database size={13} className="metric-icon text-cyan" />
              <span>Q-STATES</span>
            </div>
            <div className="metric-value text-cyan">
              {qStates.toLocaleString()}
            </div>
          </div>

          <div className="metric-pill">
            <div className="metric-label">
              <Clock size={13} className="metric-icon text-amber" />
              <span>TRAIN TIME</span>
            </div>
            <div className="metric-value text-white">
              {trainTime.toFixed(1)}s
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
