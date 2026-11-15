import React, { useState } from 'react';
import type { Experiment, GameReplay } from '../types';
import { Download, FileText, Table, FileSpreadsheet, Copy, Check, Eye } from 'lucide-react';

interface ExportTabProps {
  experiments: Experiment[];
  currentReplay: GameReplay | null;
}

export const ExportTab: React.FC<ExportTabProps> = ({
  experiments,
  currentReplay
}) => {
  const [selectedExpId, setSelectedExpId] = useState<string>(
    experiments[0]?.id || ''
  );
  const [previewContent, setPreviewContent] = useState<string>('');
  const [loadingPreview, setLoadingPreview] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  const selectedExp = experiments.find((e) => e.id === selectedExpId) || experiments[0];

  const handleDownloadTrainingCsv = () => {
    window.open('/api/export/training-csv', '_blank');
  };

  const handleDownloadBenchmarkCsv = () => {
    window.open('/api/export/benchmark-csv', '_blank');
  };

  const handleDownloadReplayCsv = () => {
    const replayId = currentReplay?.replay_id || 'sample';
    window.open(`/api/export/replay-csv/${replayId}`, '_blank');
  };

  const handleDownloadReport = () => {
    if (!selectedExp) return;
    window.open(`/api/export/report/${selectedExp.id}`, '_blank');
  };

  const handleFetchReportPreview = async () => {
    if (!selectedExp) return;
    setLoadingPreview(true);
    try {
      const res = await fetch(`/api/export/report/${selectedExp.id}`);
      if (res.ok) {
        const text = await res.text();
        setPreviewContent(text);
      }
    } catch (err) {
      console.error('Failed to fetch preview:', err);
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleCopyReport = () => {
    if (!previewContent) return;
    navigator.clipboard.writeText(previewContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  React.useEffect(() => {
    if (selectedExp) {
      handleFetchReportPreview();
    }
  }, [selectedExpId]);

  return (
    <div className="export-tab">
      <div className="card export-hub-card">
        <div className="card-header">
          <div className="card-title-group">
            <Download size={20} className="text-cyan" />
            <div>
              <h3 className="card-title">Data Export & Academic Reports</h3>
              <p className="card-subtitle">
                Export empirical training datasets, benchmark evaluations, and project evaluation summaries.
              </p>
            </div>
          </div>
        </div>

        {/* 4 Export Action Cards Grid */}
        <div className="export-cards-grid">
          {/* Card 1: Training History CSV */}
          <div className="export-item-card">
            <div className="item-icon-box bg-blue-subtle">
              <FileSpreadsheet size={22} className="text-blue" />
            </div>
            <div className="item-content">
              <h4 className="item-title">Training Run History (CSV)</h4>
              <p className="item-desc">
                Complete table of all experiments with episodes, α, γ, ε, train time, Q-states, and final win/loss/draw rates.
              </p>
            </div>
            <button onClick={handleDownloadTrainingCsv} className="btn btn-primary btn-sm">
              <Download size={14} />
              <span>Download CSV</span>
            </button>
          </div>

          {/* Card 2: Benchmark Results CSV */}
          <div className="export-item-card">
            <div className="item-icon-box bg-green-subtle">
              <Table size={22} className="text-green" />
            </div>
            <div className="item-content">
              <h4 className="item-title">Benchmark Evaluations (CSV)</h4>
              <p className="item-desc">
                Summary of competitive benchmark matches against Minimax (optimal) and Random opponents with exact non-loss rates.
              </p>
            </div>
            <button onClick={handleDownloadBenchmarkCsv} className="btn btn-secondary btn-sm">
              <Download size={14} />
              <span>Download CSV</span>
            </button>
          </div>

          {/* Card 3: Game Replay CSV */}
          <div className="export-item-card">
            <div className="item-icon-box bg-cyan-subtle">
              <FileText size={22} className="text-cyan" />
            </div>
            <div className="item-content">
              <h4 className="item-title">Step-by-Step Game Replay (CSV)</h4>
              <p className="item-desc">
                Detailed move-by-move diagnostic log including board states, Q-value vectors, selected action, and strategic explanations.
              </p>
            </div>
            <button onClick={handleDownloadReplayCsv} className="btn btn-secondary btn-sm">
              <Download size={14} />
              <span>Download CSV</span>
            </button>
          </div>

          {/* Card 4: Academic Report */}
          <div className="export-item-card">
            <div className="item-icon-box bg-amber-subtle">
              <FileText size={22} className="text-amber" />
            </div>
            <div className="item-content">
              <h4 className="item-title">Academic Experiment Report (.md)</h4>
              <p className="item-desc">
                Comprehensive academic project report containing mathematical Negamax derivations, hyperparameter table, and analysis.
              </p>
            </div>
            <button onClick={handleDownloadReport} className="btn btn-secondary btn-sm">
              <Download size={14} />
              <span>Download Markdown</span>
            </button>
          </div>
        </div>
      </div>

      {/* Live Academic Report Preview Section */}
      <div className="card report-preview-card">
        <div className="report-preview-header">
          <div className="preview-left">
            <Eye size={18} className="text-cyan" />
            <h4 className="card-title">Live Academic Experiment Report Preview</h4>
          </div>

          <div className="preview-controls">
            <label className="select-label">Select Run:</label>
            <select
              className="form-select"
              value={selectedExpId}
              onChange={(e) => setSelectedExpId(e.target.value)}
            >
              {experiments.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name || e.id} ({e.episodes_trained.toLocaleString()} eps)
                </option>
              ))}
            </select>

            <button onClick={handleCopyReport} className="btn btn-secondary btn-sm">
              {copied ? <Check size={14} className="text-green" /> : <Copy size={14} />}
              <span>{copied ? 'Copied!' : 'Copy to Clipboard'}</span>
            </button>

            <button onClick={handleDownloadReport} className="btn btn-primary btn-sm">
              <Download size={14} />
              <span>Download Report</span>
            </button>
          </div>
        </div>

        <div className="report-content-body">
          {loadingPreview ? (
            <div className="loading-preview">Generating comprehensive academic report...</div>
          ) : previewContent ? (
            <pre className="markdown-pre">{previewContent}</pre>
          ) : (
            <div className="empty-preview">Select an experiment above to view its generated report.</div>
          )}
        </div>
      </div>
    </div>
  );
};
