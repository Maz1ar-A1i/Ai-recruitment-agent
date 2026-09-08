import React from 'react';

export default function ScoreBadge({ score, recommendation }) {
  let badgeClass = 'badge-potential';
  if (recommendation === 'Strong Match') badgeClass = 'badge-strong';
  else if (recommendation === 'Match') badgeClass = 'badge-match';
  else if (recommendation === 'Weak Match') badgeClass = 'badge-weak';

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
      <span className={`badge ${badgeClass}`} style={{ fontSize: '0.85rem', padding: '4px 12px' }}>
        {recommendation}
      </span>
      {score !== undefined && (
        <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#f3f4f6' }}>
          {score}/100
        </span>
      )}
    </div>
  );
}
