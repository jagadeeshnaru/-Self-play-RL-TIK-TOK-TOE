import React, { useState } from 'react';
import type { Experiment } from '../types';
import { LineChart, type SeriesConfig } from './LineChart';
import { GitCompare, Trash2, CheckSquare, Square, Layers } from 'lucide-react';

interface ComparisonTabProps {
  experiments: Experiment[];
  onDeleteExperiment: (id: string) => Promise<void>;
}

export const ComparisonTab: React.FC<ComparisonTabProps> = ({
  experiments,
  onDeleteExperiment
}) => {
  // Store selected experiment IDs for comparison
  const [selectedIds, setSelectedIds] = useState<string[]>(() => {
    // Default select first 2-3 experiments
    return experiments.slice(0, 3).map((e) => e.id);
  });

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    setSelectedIds(experiments.map((e) => e.id));
  };

  const deselectAll = () => {
    setSelectedIds([]);
  };

  const selectedExperiments = experiments.filter((e) => selectedIds.includes(e.id));

  // Build comparative series for charts
  const colors = ['#10B981', '#06B6D4', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

  // Normalized data table for comparative charts
  // Find maximum checkpoints across selected experiments
  const maxCheckpoints = Math.max(
    ...selectedExperiments.map((e) => e.batch_records?.length || 0),
    0
  );

  const drawComparisonData: Array<Record<string, number>> = [];
  const minimaxComparisonData: Array<Record<string, number>> = [];

  for (let i = 0; i < maxCheckpoints; i++) {
    const drawRow: Record<string, number> = { step: i + 1 };
    const minimaxRow: Record<string, number> = { step: i + 1 };

    selectedExperiments.forEach((exp) => {
      const rec = exp.batch_records?.[i];
      if (rec) {
        drawRow[exp.id] = rec.draw_rate;
        minimaxRow[exp.id] = rec.non_loss_vs_minimax;
      }
    });

    drawComparisonData.push(drawRow);
    minimaxComparisonData.push(minimaxRow);
  }

  const comparativeDrawSeries: SeriesConfig[] = selectedExperiments.map((exp, idx) => ({
    key: exp.id,
    label: `${exp.name || exp.id.slice(0, 8)} (${(exp.episodes_trained / 1000).toFixed(0)}k)`,
    color: colors[idx % colors.length]
  }));

  const comparativeMinimaxSeries: SeriesConfig[] = selectedExperiments.map((exp, idx) => ({
    key: exp.id,
    label: `${exp.name || exp.id.slice(0, 8)}`,
    color: colors[idx % colors.length]
  }));

  return (
    <div className="comparison-tab">
      {/* Top Banner & Multi-Select Bar */}
      <div className="card comparison-header-card">
        <div className="comp-header-top">
          <div className="card-title-group">
            <GitCompare size={20} className="text-cyan" />
            <div>
              <h3 className="card-title">Training Run Comparison</h3>
              <p className="card-subtitle">
                Select and evaluate multiple reinforcement learning runs side by side.
              </p>
            </div>
          </div>

          <div className="comp-actions">
            <button onClick={selectAll} className="btn btn-secondary btn-sm">
              <CheckSquare size={14} />
              <span>Select All</span>
            </button>
            <button onClick={deselectAll} className="btn btn-secondary btn-sm">
              <Square size={14} />
              <span>Clear Selection</span>
            </button>
          </div>
        </div>

        {/* Experiment Selector List */}
        <div className="experiment-chips-grid">
          {experiments.map((exp) => {
            const isSelected = selectedIds.includes(exp.id);
            const color = colors[selectedExperiments.findIndex((e) => e.id === exp.id) % colors.length];

            return (
              <div
                key={exp.id}
                className={`exp-chip ${isSelected ? 'selected' : ''}`}
                onClick={() => toggleSelect(exp.id)}
              >
                <div className="chip-indicator" style={{ backgroundColor: isSelected ? color : '#334155' }} />
                <div className="chip-content">
                  <div className="chip-name">{exp.name || `Run ${exp.id}`}</div>
                  <div className="chip-meta">
                    {exp.episodes_trained.toLocaleString()} eps · α={exp.alpha} · γ={exp.gamma} · Q-States: {exp.q_states}
                  </div>
                </div>
                <button
                  className="chip-delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm(`Delete experiment "${exp.name || exp.id}"?`)) {
                      onDeleteExperiment(exp.id);
                    }
                  }}
                  title="Delete experiment"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {selectedExperiments.length > 0 ? (
        <>
          {/* Comparative Metrics Table */}
          <div className="card comparison-table-card">
            <div className="card-header">
              <h4 className="card-title">Hyperparameter & Performance Matrix</h4>
            </div>

            <div className="table-responsive">
              <table className="comp-table">
                <thead>
                  <tr>
                    <th>Experiment Run</th>
                    <th>Episodes Trained</th>
                    <th>Learning Rate (α)</th>
                    <th>Discount (γ)</th>
                    <th>Exploration (ε)</th>
                    <th>Train Time</th>
                    <th>Q-Table States</th>
                    <th>Self-Play Draw %</th>
                    <th>Non-Loss vs Minimax</th>
                    <th>Win vs Random</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedExperiments.map((exp, idx) => (
                    <tr key={exp.id}>
                      <td className="font-semibold text-white">
                        <span
                          className="table-legend-dot"
                          style={{ backgroundColor: colors[idx % colors.length] }}
                        />
                        {exp.name || exp.id}
                      </td>
                      <td>{exp.episodes_trained.toLocaleString()}</td>
                      <td className="font-mono text-cyan">{exp.alpha}</td>
                      <td className="font-mono text-cyan">{exp.gamma}</td>
                      <td className="font-mono">{exp.epsilon_start} &rarr; {exp.epsilon_end}</td>
                      <td>{exp.train_time_sec.toFixed(2)}s</td>
                      <td className="font-mono">{exp.q_states.toLocaleString()}</td>
                      <td className="text-green font-semibold">{exp.self_play_draws_pct.toFixed(1)}%</td>
                      <td className="text-amber font-semibold">{exp.non_loss_vs_minimax_pct.toFixed(1)}%</td>
                      <td className="text-cyan font-semibold">{exp.win_vs_random_pct.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Overlaid Comparative Charts */}
          <div className="comparative-charts-grid">
            <LineChart
              title="Comparative Convergence: Self-Play Draw Rate"
              subtitle="Comparison of mutual draw convergence across selected training runs."
              data={drawComparisonData}
              xKey="step"
              series={comparativeDrawSeries}
              height={220}
              yDomainLeft={[0, 100]}
              xFormat={(v) => `Checkpt ${v}`}
            />

            <LineChart
              title="Comparative Policy Strength: Non-Loss vs Minimax"
              subtitle="Comparison of game-theoretic optimality vs Minimax over checkpoint iterations."
              data={minimaxComparisonData}
              xKey="step"
              series={comparativeMinimaxSeries}
              height={220}
              yDomainLeft={[0, 100]}
              xFormat={(v) => `Checkpt ${v}`}
            />
          </div>
        </>
      ) : (
        <div className="card empty-comparison-state">
          <Layers size={36} className="text-slate" />
          <h4>No Experiments Selected</h4>
          <p>Check one or more experiments above to compare their learning trajectories side by side.</p>
        </div>
      )}
    </div>
  );
};
