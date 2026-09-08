import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import ScoreBadge from '../components/ScoreBadge';
import ScoreBreakdown from '../components/ScoreBreakdown';
import HumanDecisionModal from '../components/HumanDecisionModal';

export default function EvaluationPage({ evaluationId, preselectedJobId, preselectedCandidateId }) {
  const [evaluation, setEvaluation] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(preselectedJobId || '');
  const [selectedCandidateId, setSelectedCandidateId] = useState(preselectedCandidateId || '');
  const [loading, setLoading] = useState(false);
  const [showDecisionModal, setShowDecisionModal] = useState(false);

  useEffect(() => {
    const fetchSelectables = async () => {
      try {
        const [jList, cList] = await Promise.all([api.getJobs(), api.getCandidates()]);
        setJobs(jList);
        setCandidates(cList);
        if (!selectedJobId && jList.length > 0) setSelectedJobId(jList[0].id);
        if (!selectedCandidateId && cList.length > 0) setSelectedCandidateId(cList[0].id);
      } catch (err) {
        console.error('Failed to load jobs/candidates:', err);
      }
    };
    fetchSelectables();
  }, []);

  useEffect(() => {
    if (evaluationId) {
      loadEvaluation(evaluationId);
    }
  }, [evaluationId]);

  const loadEvaluation = async (id) => {
    try {
      setLoading(true);
      const data = await api.getEvaluation(id);
      setEvaluation(data);
    } catch (err) {
      alert('Error fetching evaluation: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvaluation = async () => {
    if (!selectedJobId || !selectedCandidateId) {
      alert('Please select both a job requisition and a candidate.');
      return;
    }

    try {
      setLoading(true);
      const res = await api.evaluateCandidate(selectedJobId, selectedCandidateId);
      setEvaluation(res);
    } catch (err) {
      alert('Evaluation failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDecisionSubmitted = async (decisionPayload) => {
    await api.submitDecision(decisionPayload);
    // Reload evaluation to reflect updated human decision
    if (evaluation?.id) {
      await loadEvaluation(evaluation.id);
    }
  };

  return (
    <div>
      {/* Selector Card */}
      <div className="card" style={{ marginBottom: '28px' }}>
        <div className="card-header">
          <h3 className="card-title">Run AI Candidate Evaluation</h3>
          <span style={{ fontSize: '0.84rem', color: '#9ca3af' }}>Multi-step Autonomous Agent Orchestration</span>
        </div>

        <div className="grid-2">
          <div className="form-group">
            <label className="form-label">Select Job Requisition</label>
            <select
              className="form-select"
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
            >
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>{j.title} ({j.experience_required} yrs)</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Select Candidate Profile</label>
            <select
              className="form-select"
              value={selectedCandidateId}
              onChange={(e) => setSelectedCandidateId(e.target.value)}
            >
              {candidates.map((c) => (
                <option key={c.id} value={c.id}>{c.name} ({c.years_of_experience} yrs exp)</option>
              ))}
            </select>
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleRunEvaluation}
          disabled={loading}
          style={{ width: '100%', padding: '12px' }}
        >
          {loading ? 'Agent Orchestrating Multi-Tool Evaluation...' : '⚡ Execute Autonomous Candidate Evaluation'}
        </button>
      </div>

      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: '50px 0', color: '#818cf8' }}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>🤖</div>
          <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>Recruitment Agent Executing Workflow...</div>
          <div style={{ color: '#9ca3af', fontSize: '0.85rem', marginTop: '6px' }}>
            Extracting requirements → Matching skills → Classifying gaps → Computing transparent score → Generating interview questions → Validating report
          </div>
        </div>
      )}

      {evaluation && !loading && (
        <div>
          {/* Executive Header Card */}
          <div className="card" style={{ marginBottom: '24px', background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.9) 0%, rgba(31, 41, 55, 0.7) 100%)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <div style={{ fontSize: '0.8rem', color: '#818cf8', fontWeight: 700, textTransform: 'uppercase' }}>
                  Candidate Evaluation Report
                </div>
                <h2 style={{ fontSize: '1.7rem', margin: '4px 0' }}>
                  {evaluation.candidate?.name || 'Candidate Evaluation'}
                </h2>
                <div style={{ color: '#9ca3af', fontSize: '0.9rem' }}>
                  Target Role: <strong style={{ color: '#f3f4f6' }}>{evaluation.job?.title || 'Target Job'}</strong>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.8rem', color: '#9ca3af' }}>AI Recommendation</div>
                  <ScoreBadge score={evaluation.overall_score} recommendation={evaluation.recommendation} />
                </div>

                <button
                  className="btn btn-success"
                  onClick={() => setShowDecisionModal(true)}
                >
                  ✓ Recruiter Review
                </button>
              </div>
            </div>

            {/* Recruiter Decisions Banner */}
            {evaluation.decisions?.length > 0 && (
              <div style={{ marginTop: '20px', padding: '14px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                <div style={{ fontWeight: 700, color: '#34d399', fontSize: '0.86rem' }}>
                  Human Recruiter Decision: {evaluation.decisions[0].decision} by {evaluation.decisions[0].reviewer_name}
                </div>
                {evaluation.decisions[0].recruiter_notes && (
                  <div style={{ fontSize: '0.85rem', color: '#d1fae5', marginTop: '4px' }}>
                    "{evaluation.decisions[0].recruiter_notes}"
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Deterministic Score Breakdown */}
          <ScoreBreakdown
            breakdown={{
              skills_score: evaluation.skill_match_score,
              experience_score: evaluation.experience_score,
              education_score: evaluation.education_score,
              preferred_skills_score: evaluation.preferred_skills_score,
              projects_score: evaluation.projects_score,
              overall_score: evaluation.overall_score,
              recommendation: evaluation.recommendation,
            }}
          />

          {/* AI Executive Explanation */}
          {evaluation.ai_explanation && (
            <div className="card" style={{ marginBottom: '24px' }}>
              <div className="card-header">
                <h3 className="card-title">AI Executive Explanation</h3>
              </div>
              <p style={{ color: '#d1d5db', fontSize: '0.94rem', lineHeight: '1.6' }}>
                {evaluation.ai_explanation}
              </p>
            </div>
          )}

          {/* Skills Matching Grid */}
          <div className="grid-2" style={{ marginBottom: '24px' }}>
            <div className="card">
              <h3 className="card-title" style={{ marginBottom: '14px', color: '#34d399' }}>
                ✓ Matching Verified Skills ({evaluation.matching_skills?.length || 0})
              </h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {evaluation.matching_skills?.map((s, idx) => (
                  <span key={idx} className="badge badge-strong" style={{ padding: '6px 12px' }}>
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div className="card">
              <h3 className="card-title" style={{ marginBottom: '14px', color: '#f87171' }}>
                ✕ Missing Requirements ({evaluation.missing_skills?.length || 0})
              </h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {evaluation.missing_skills?.length > 0 ? (
                  evaluation.missing_skills.map((s, idx) => (
                    <span key={idx} className="badge badge-weak" style={{ padding: '6px 12px' }}>
                      {s}
                    </span>
                  ))
                ) : (
                  <span style={{ color: '#9ca3af', fontSize: '0.88rem' }}>None missing! Full coverage.</span>
                )}
              </div>
            </div>
          </div>

          {/* Skill Gaps with Severity & Rationale */}
          <div className="card" style={{ marginBottom: '24px' }}>
            <div className="card-header">
              <h3 className="card-title">Skill Gap Analysis & Recruiter Rationale</h3>
              <span style={{ fontSize: '0.82rem', color: '#9ca3af' }}>Classified by Critical, Moderate, and Minor severity</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {evaluation.skill_gaps?.map((gap, idx) => {
                const badgeClass =
                  gap.severity === 'Critical' ? 'badge-gap-critical' :
                  gap.severity === 'Moderate' ? 'badge-gap-moderate' : 'badge-gap-minor';
                return (
                  <div key={idx} style={{ background: 'rgba(31, 41, 55, 0.4)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.96rem' }}>{gap.skill}</span>
                      <span className={`badge ${badgeClass}`}>{gap.severity} Gap</span>
                    </div>
                    <p style={{ fontSize: '0.86rem', color: '#9ca3af' }}>{gap.rationale}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Evidence-Based Reasoning */}
          {evaluation.evidence_snippets?.length > 0 && (
            <div className="card" style={{ marginBottom: '24px' }}>
              <div className="card-header">
                <h3 className="card-title">Evidence-Based Reasoning</h3>
                <span style={{ fontSize: '0.82rem', color: '#9ca3af' }}>Verbatim Resume Proof</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {evaluation.evidence_snippets.map((ev, idx) => (
                  <div key={idx} style={{ background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.15)', padding: '14px', borderRadius: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontWeight: 700, color: '#c7d2fe' }}>Skill: {ev.skill}</span>
                      <span style={{ fontSize: '0.78rem', color: '#818cf8' }}>{ev.source_section}</span>
                    </div>
                    <div style={{ fontSize: '0.88rem', color: '#d1d5db', fontStyle: 'italic' }}>
                      "{ev.snippet}"
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Personalized Interview Questions */}
          {evaluation.interview_questions?.length > 0 && (
            <div className="card" style={{ marginBottom: '24px' }}>
              <div className="card-header">
                <h3 className="card-title">Personalized Interview Questions</h3>
                <span style={{ fontSize: '0.82rem', color: '#9ca3af' }}>Targeted by Candidate Claims & Gaps</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {evaluation.interview_questions.map((q, idx) => (
                  <div key={idx} style={{ background: 'rgba(31, 41, 55, 0.4)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span className="badge badge-skill" style={{ background: 'rgba(99, 102, 241, 0.18)', color: '#a5b4fc' }}>
                        {q.category}
                      </span>
                      {q.target_skill_or_gap && (
                        <span style={{ fontSize: '0.8rem', color: '#9ca3af' }}>Target: <strong>{q.target_skill_or_gap}</strong></span>
                      )}
                    </div>

                    <div style={{ fontWeight: 600, fontSize: '0.98rem', color: '#f9fafb', marginBottom: '8px' }}>
                      "{q.question}"
                    </div>

                    <div style={{ fontSize: '0.84rem', color: '#9ca3af', marginBottom: '10px' }}>
                      <strong>Rationale:</strong> {q.rationale}
                    </div>

                    {q.suggested_answer_points?.length > 0 && (
                      <div style={{ background: 'rgba(0,0,0,0.2)', padding: '10px 14px', borderRadius: '6px' }}>
                        <div style={{ fontSize: '0.76rem', color: '#34d399', fontWeight: 700, marginBottom: '4px' }}>
                          Key Points to Look For:
                        </div>
                        <ul style={{ paddingLeft: '18px', fontSize: '0.82rem', color: '#d1d5db' }}>
                          {q.suggested_answer_points.map((pt, pIdx) => (
                            <li key={pIdx}>{pt}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Strengths & Concerns Grid */}
          <div className="grid-2">
            <div className="card">
              <h3 className="card-title" style={{ marginBottom: '12px', color: '#34d399' }}>Key Strengths</h3>
              <ul style={{ paddingLeft: '20px', fontSize: '0.9rem', color: '#d1d5db', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {evaluation.strengths?.map((s, idx) => (
                  <li key={idx}>{s}</li>
                ))}
              </ul>
            </div>

            <div className="card">
              <h3 className="card-title" style={{ marginBottom: '12px', color: '#f59e0b' }}>Potential Concerns & Gaps</h3>
              <ul style={{ paddingLeft: '20px', fontSize: '0.9rem', color: '#d1d5db', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {evaluation.potential_concerns?.length > 0 ? (
                  evaluation.potential_concerns.map((c, idx) => (
                    <li key={idx}>{c}</li>
                  ))
                ) : (
                  <li>No significant concerns recorded.</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Human Decision Modal */}
      {showDecisionModal && evaluation && (
        <HumanDecisionModal
          evaluation={evaluation}
          onClose={() => setShowDecisionModal(false)}
          onSubmitted={handleDecisionSubmitted}
        />
      )}
    </div>
  );
}
