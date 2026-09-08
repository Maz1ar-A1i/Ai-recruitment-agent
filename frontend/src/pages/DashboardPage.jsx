import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import ScoreBadge from '../components/ScoreBadge';

export default function DashboardPage({ onNavigate, onSelectEvaluation }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await api.getStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load dashboard telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  if (loading && !stats) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0', color: '#9ca3af' }}>
        <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⚡</div>
        Loading recruitment telemetry...
      </div>
    );
  }

  return (
    <div>
      <div className="disclaimer-banner">
        <span style={{ fontSize: '1.2rem' }}>⚖️</span>
        <div>
          <strong>Responsible Decision-Support Notice:</strong> AI recommendations are non-autonomous and serve strictly as structured guidance. Final selection decisions must be validated by human technical recruiters.
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid-4" style={{ marginBottom: '32px' }}>
        <div className="kpi-card">
          <div className="kpi-icon">💼</div>
          <div>
            <div className="kpi-value">{stats?.total_jobs || 0}</div>
            <div className="kpi-label">Active Job Requisitions</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>👥</div>
          <div>
            <div className="kpi-value">{stats?.total_candidates || 0}</div>
            <div className="kpi-label">Parsed Resumes</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>🎯</div>
          <div>
            <div className="kpi-value">{stats?.total_evaluations || 0}</div>
            <div className="kpi-label">Completed Evaluations</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'rgba(217, 70, 239, 0.15)', color: '#e879f9' }}>📊</div>
          <div>
            <div className="kpi-value">{stats?.average_score || 0}%</div>
            <div className="kpi-label">Average Match Score</div>
          </div>
        </div>
      </div>

      {/* Match Distribution */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <h3 className="card-title">Candidate Match Tier Distribution</h3>
          <span style={{ fontSize: '0.82rem', color: '#9ca3af' }}>Based on deterministic scoring thresholds</span>
        </div>
        <div className="grid-4">
          <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '16px', borderRadius: '10px' }}>
            <div style={{ color: '#34d399', fontWeight: 600, fontSize: '0.85rem' }}>Strong Matches (&ge; 85%)</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '4px' }}>
              {stats?.distribution?.strong_matches || 0}
            </div>
          </div>

          <div style={{ background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.25)', padding: '16px', borderRadius: '10px' }}>
            <div style={{ color: '#60a5fa', fontWeight: 600, fontSize: '0.85rem' }}>Good Matches (70 - 84%)</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '4px' }}>
              {stats?.distribution?.matches || 0}
            </div>
          </div>

          <div style={{ background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.25)', padding: '16px', borderRadius: '10px' }}>
            <div style={{ color: '#fbbf24', fontWeight: 600, fontSize: '0.85rem' }}>Potential Matches (50 - 69%)</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '4px' }}>
              {stats?.distribution?.potential_matches || 0}
            </div>
          </div>

          <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', padding: '16px', borderRadius: '10px' }}>
            <div style={{ color: '#f87171', fontWeight: 600, fontSize: '0.85rem' }}>Weak Matches (&lt; 50%)</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '4px' }}>
              {stats?.distribution?.weak_matches || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Action Bar */}
      <div className="grid-3" style={{ marginBottom: '32px' }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>💼</div>
            <h4 style={{ fontSize: '1.05rem', marginBottom: '6px' }}>New Job Requisition</h4>
            <p style={{ fontSize: '0.86rem', color: '#9ca3af' }}>
              Create a job or paste an unstructured description for automatic AI requirement extraction.
            </p>
          </div>
          <button className="btn btn-secondary" style={{ marginTop: '16px' }} onClick={() => onNavigate('jobs')}>
            Manage Jobs →
          </button>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>📄</div>
            <h4 style={{ fontSize: '1.05rem', marginBottom: '6px' }}>Upload Candidate Resumes</h4>
            <p style={{ fontSize: '0.86rem', color: '#9ca3af' }}>
              Upload resumes in PDF, DOCX, or TXT. Automatic de-biasing and skill normalization applied.
            </p>
          </div>
          <button className="btn btn-secondary" style={{ marginTop: '16px' }} onClick={() => onNavigate('candidates')}>
            Upload Resumes →
          </button>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderColor: 'rgba(99, 102, 241, 0.3)' }}>
          <div>
            <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>🚀</div>
            <h4 style={{ fontSize: '1.05rem', marginBottom: '6px' }}>1-Click Demo Showcase</h4>
            <p style={{ fontSize: '0.86rem', color: '#9ca3af' }}>
              Experience the complete multi-step tool calling loop with pre-loaded realistic scenarios.
            </p>
          </div>
          <button className="btn btn-primary" style={{ marginTop: '16px' }} onClick={() => onNavigate('demo')}>
            Launch Demo Showcase ⚡
          </button>
        </div>
      </div>

      {/* Recent Evaluations Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Candidate Evaluations</h3>
          <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('batch')}>
            Batch Ranking
          </button>
        </div>

        {stats?.recent_evaluations?.length > 0 ? (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Evaluation ID</th>
                  <th>Match Score</th>
                  <th>AI Recommendation</th>
                  <th>Evaluated Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_evaluations.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <code style={{ fontSize: '0.8rem', color: '#a5b4fc' }}>{item.id.slice(0, 8)}...</code>
                    </td>
                    <td>
                      <span style={{ fontWeight: 700, fontSize: '1.05rem' }}>{item.score}/100</span>
                    </td>
                    <td>
                      <ScoreBadge recommendation={item.recommendation} />
                    </td>
                    <td style={{ color: '#9ca3af', fontSize: '0.85rem' }}>
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => onSelectEvaluation(item.id)}
                      >
                        Inspect Report →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '36px 0', color: '#9ca3af' }}>
            No candidate evaluations recorded yet. Launch the <strong>1-Click Demo</strong> or evaluate candidates to populate telemetry!
          </div>
        )}
      </div>
    </div>
  );
}
