import React from 'react';

export default function Topbar({ title, onRunDemo, isDemoLoading }) {
  return (
    <header className="topbar">
      <div className="topbar-title">{title}</div>
      <div className="topbar-actions">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', color: '#9ca3af' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></span>
          <span>FastAPI Engine</span>
        </div>
        <button
          className="btn btn-primary btn-sm"
          onClick={onRunDemo}
          disabled={isDemoLoading}
        >
          {isDemoLoading ? 'Running Agent...' : '⚡ Quick Demo Run'}
        </button>
      </div>
    </header>
  );
}
