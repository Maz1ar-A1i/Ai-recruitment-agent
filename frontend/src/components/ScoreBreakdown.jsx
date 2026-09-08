import React from 'react';

export default function ScoreBreakdown({ breakdown }) {
  if (!breakdown) return null;

  const items = [
    { label: 'Core Skills Match', score: breakdown.skills_score, max: 50, color: '#6366f1' },
    { label: 'Experience Depth', score: breakdown.experience_score, max: 20, color: '#3b82f6' },
    { label: 'Education Alignment', score: breakdown.education_score, max: 10, color: '#10b981' },
    { label: 'Preferred Nice-to-Haves', score: breakdown.preferred_skills_score, max: 10, color: '#8b5cf6' },
    { label: 'Relevant Project Portfolio', score: breakdown.projects_score, max: 10, color: '#f59e0b' },
  ];

  return (
    <div className="card" style={{ marginBottom: '24px' }}>
      <div className="card-header">
        <h3 className="card-title">Transparent Deterministic Scoring</h3>
        <span style={{ fontSize: '0.82rem', color: '#9ca3af' }}>Weighted Formula (No LLM Score Hallucination)</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {items.map((item) => {
          const pct = Math.min(Math.round((item.score / item.max) * 100), 100);
          return (
            <div key={item.label}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.86rem' }}>
                <span style={{ color: '#d1d5db', fontWeight: 500 }}>{item.label}</span>
                <span style={{ fontWeight: 700, color: '#f9fafb' }}>
                  {item.score} / {item.max} pts ({pct}%)
                </span>
              </div>
              <div className="progress-bar-container">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${pct}%`, backgroundColor: item.color }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>Total Calculated Match Score</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f9fafb', fontFamily: 'var(--font-heading)' }}>
            {breakdown.overall_score} / 100
          </span>
          <span className={`badge ${
            breakdown.recommendation === 'Strong Match' ? 'badge-strong' :
            breakdown.recommendation === 'Match' ? 'badge-match' :
            breakdown.recommendation === 'Weak Match' ? 'badge-weak' : 'badge-potential'
          }`}>
            {breakdown.recommendation}
          </span>
        </div>
      </div>
    </div>
  );
}
