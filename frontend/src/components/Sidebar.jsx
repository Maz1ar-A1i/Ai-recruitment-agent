import React from 'react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Executive Dashboard', icon: '📊' },
    { id: 'jobs', label: 'Job Requisitions', icon: '💼' },
    { id: 'candidates', label: 'Candidate Profiles', icon: '👥' },
    { id: 'evaluation', label: 'Candidate Evaluation', icon: '🎯' },
    { id: 'batch', label: 'Batch Ranking', icon: '⚡' },
    { id: 'agent-runs', label: 'Agent Activity Trace', icon: '🤖' },
    { id: 'knowledge', label: 'Hiring Guidelines (RAG)', icon: '📚' },
    { id: 'benchmark', label: 'AI Quality Metrics', icon: '📈' },
    { id: 'demo', label: '1-Click Demo Showcase', icon: '🚀' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-icon">🎯</div>
        <div>
          <div className="brand-title">RecruitAgent</div>
          <span className="brand-badge">Agentic AI Core</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <div
            key={item.id}
            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => setActiveTab(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', display: 'inline-block' }}></span>
          <span style={{ color: '#9ca3af', fontWeight: 600 }}>Decision Support Active</span>
        </div>
        <div>Fair hiring & de-biasing enabled</div>
      </div>
    </aside>
  );
}
