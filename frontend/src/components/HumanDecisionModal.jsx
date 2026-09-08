import React, { useState } from 'react';

export default function HumanDecisionModal({ evaluation, onClose, onSubmitted }) {
  const [decision, setDecision] = useState('APPROVED');
  const [modifiedRec, setModifiedRec] = useState(evaluation.recommendation);
  const [notes, setNotes] = useState('');
  const [reviewerName, setReviewerName] = useState('Recruiter');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmitted({
        evaluation_id: evaluation.id,
        decision,
        modified_recommendation: decision === 'MODIFIED' ? modifiedRec : null,
        recruiter_notes: notes,
        reviewer_name: reviewerName
      });
      onClose();
    } catch (err) {
      alert('Failed to save decision: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
          <h2 style={{ fontSize: '1.25rem' }}>Human-in-the-Loop Review</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        <div style={{ background: 'rgba(99, 102, 241, 0.08)', padding: '14px', borderRadius: '8px', marginBottom: '20px', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
          <div style={{ fontSize: '0.8rem', color: '#a5b4fc', textTransform: 'uppercase', fontWeight: 700 }}>
            AI Assistant Recommendation:
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '4px' }}>
            <span style={{ fontSize: '1.1rem', fontWeight: 700 }}>{evaluation.recommendation}</span>
            <span style={{ color: '#9ca3af' }}>({evaluation.overall_score}/100 Match Score)</span>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Reviewer / Recruiter Name</label>
            <input
              type="text"
              className="form-input"
              value={reviewerName}
              onChange={(e) => setReviewerName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Recruiter Decision</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
              <button
                type="button"
                className={`btn ${decision === 'APPROVED' ? 'btn-success' : 'btn-secondary'}`}
                onClick={() => setDecision('APPROVED')}
              >
                ✓ Approve AI
              </button>
              <button
                type="button"
                className={`btn ${decision === 'REJECTED' ? 'btn-danger' : 'btn-secondary'}`}
                onClick={() => setDecision('REJECTED')}
              >
                ✕ Reject AI
              </button>
              <button
                type="button"
                className={`btn ${decision === 'MODIFIED' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setDecision('MODIFIED')}
              >
                ✎ Override / Edit
              </button>
            </div>
          </div>

          {decision === 'MODIFIED' && (
            <div className="form-group">
              <label className="form-label">Modified Final Recommendation</label>
              <select
                className="form-select"
                value={modifiedRec}
                onChange={(e) => setModifiedRec(e.target.value)}
              >
                <option value="Strong Match">Strong Match</option>
                <option value="Match">Match</option>
                <option value="Potential Match">Potential Match</option>
                <option value="Weak Match">Weak Match</option>
              </select>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Recruiter Evaluation Notes & Rationale</label>
            <textarea
              className="form-textarea"
              placeholder="Provide context, interview observations, or reasons for override..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              required
            ></textarea>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Saving Decision...' : 'Finalize Recruiter Decision'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
