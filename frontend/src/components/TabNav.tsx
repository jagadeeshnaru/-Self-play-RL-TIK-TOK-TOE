import React from 'react';
import { PlayCircle, UserCheck, Cpu, Repeat, GitCompare, Download } from 'lucide-react';

export type TabId = 'train' | 'play' | 'benchmark' | 'replay' | 'compare' | 'export';

interface TabNavProps {
  activeTab: TabId;
  onSelectTab: (tab: TabId) => void;
  replayCount?: number;
  experimentCount?: number;
}

export const TabNav: React.FC<TabNavProps> = ({
  activeTab,
  onSelectTab,
  experimentCount = 0
}) => {
  const tabs = [
    { id: 'train' as TabId, label: '1 · Train (self-play)', icon: PlayCircle },
    { id: 'play' as TabId, label: '2 · Human vs Agent', icon: UserCheck },
    { id: 'benchmark' as TabId, label: '3 · Minimax vs RL', icon: Cpu },
    { id: 'replay' as TabId, label: '4 · Step-by-Step Replay', icon: Repeat },
    { id: 'compare' as TabId, label: '5 · Experiment Comparison', icon: GitCompare, badge: experimentCount > 0 ? experimentCount : undefined },
    { id: 'export' as TabId, label: '6 · Export & Reports', icon: Download }
  ];

  return (
    <nav className="tab-nav">
      <div className="tab-list">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              className={`tab-btn ${isActive ? 'active' : ''}`}
              onClick={() => onSelectTab(tab.id)}
            >
              <Icon size={16} className="tab-icon" />
              <span>{tab.label}</span>
              {tab.badge !== undefined && (
                <span className="tab-badge">{tab.badge}</span>
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};
