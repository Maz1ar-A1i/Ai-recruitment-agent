import React, { useState } from 'react';
import { api } from '../api/client';
import ScoreBreakdown from '../components/ScoreBreakdown';
import ScoreBadge from '../components/ScoreBadge';
import AgentTraceTimeline from '../components/AgentTraceTimeline';

export default function DemoPage({ onSelectEvaluation, onInspectRun }) {
  const [running, setRunning] = useState(false);
  const [demoData, setDemoData] = useState(null);
  const [runSteps, setRunSteps] = useState([]);

  const handleLaunchDemo = async () => {
    try {
      setRunning(true);
      const res = await api.runDemo();
      setDemoData(res);

      // Fetch the detailed step trace
      if (res.agent_run_id) {
        const runDetails = await api.getAgentRun(res.agent_run_id);
        setRunSteps(runDetails.steps || []);
      }
    } catch (err) {
      alert('Demo execution failed: ' + err.message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      {/* Hero Showcase Card */}
      <div className="card" style={{ marginBottom: '32px', background: 'radial-gradient(circle at 90% 10%, rgba(99, 102, 241, 0.25) 0%, rgba(17, 24, 39, 0.95) 70%)', borderColor: 'rgba(99, 102, 241, 0.4)' }}>
        <div style={{ maxWidth: '800px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(99, 102, 241, 0.2)', color: '#c7d2fe', padding: '4px 12px', borderRadius: '9999px', fontSize: '0.8rem', fontWeight: 700, marginBottom: '14px' }}>
            <span>⚡</span> PORTFOLIO SHOWCASE: AUTONOMOUS AGENTIC AI
          </div>
          <h1 style={{ fontSize: '2.1rem', lineHeight: '1.2', marginBottom: '14px' }}>
            Autonomous Multi-Step AI Recruitment Agent
          </h1>
          <p style={{ color: '#d1d5db', fontSize: '1rem', lineHeight: '1.6', marginBottom: '22px' }}>
            Experience an end-to-end recruitment evaluation without hardcoded shortcuts. Watch the agent dynamically select tools from the centralized registry, parse raw resumes, normalize skills, cross-reference experience evidence, detect gaps, compute deterministic scores, formulate personalized interview questions, and enforce mathematical verification.
          </p>

          <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
            <button
              className="btn btn-primary"
              onClick={handleLaunchDemo}
              disabled={running}
              style={{ padding: '12px 28px', fontSize: '1rem' }}
            >
              {running ? 'Agent Orchestrating Multi-Tool Workflow...' : '🚀 Run Live 1-Click Agent Demo'}
            </button>
            <span style={{ color: '#9ca3af', fontSize: '0.86rem' }}>
              Evaluates Alice Chen for Junior Python AI Engineer
            </span>
          </div>
        </div>
      </div>

      {running && (
        <div className="card" style={{ textAlign: 'center', padding: '60px 0', color: '#818cf8', marginBottom: '32px' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '14px', animation: 'spin 2s linear infinite' }}>⚙️</div>
          <h3 style={{ fontSize: '1.25rem', color: '#f9fafb', marginBottom: '8px' }}>
            Agent Loop in Progress...
          </h3>
          <p style={{ color: '#9ca3af', maxWidth: '600px', margin: '0 auto', fontSize: '0.9rem' }}>
            Planner inspecting state → Executing tools sequentially → Logging trace to SQLite → Self-correcting validation discrepancies
          </p>
        </div>
      )}

      {demoData && !running && (
        <div>
          {/* Executive Results Banner */}
          <div className="card" style={{ marginBottom: '28px', background: 'rgba(16, 185, 129, 0.06)', borderColor: 'rgba(16, 185, 129, 0.3)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <span className="badge badge-strong" style={{ marginBottom: '8px' }}>
                  ✓ Demo Run Completed Successfully
                </span>
                <h2 style={{ fontSize: '1.6rem', marginTop: '4px' }}>
                  {demoData.demo_summary.candidate_name}
                </h2>
                <div style={{ color: '#9ca3af', fontSize: '0.9rem' }}>
                  Role: <strong style={{ color: '#f3f4f6' }}>{demoData.demo_summary.job_title}</strong>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.8rem', color: '#9ca3af' }}>AI Recommendation</div>
                  <ScoreBadge
                    score={demoData.demo_summary.overall_score}
                    recommendation={demoData.demo_summary.recommendation}
                  />
                </div>

                {demoData.evaluation_id && (
                  <button
                    className="btn btn-secondary"
                    onClick={() => onSelectEvaluation(demoData.evaluation_id)}
                  >
                    Open Full Evaluation Report →
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Deterministic Score Breakdown */}
          {demoData.report?.score_breakdown && (
            <ScoreBreakdown breakdown={demoData.report.score_breakdown} />
          )}

          {/* Agent Activity Trace (Interactive Inspector) */}
          <div style={{ marginBottom: '28px' }}>
            <AgentTraceTimeline steps={runSteps} />
          </div>

          {/* Evidence Snippets & Personalized Questions */}
          <div className="grid-2" style={{ marginBottom: '28px' }}>
            {demoData.report?.evidence_snippets?.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Evidence-Based Citations</h3>
                  <span style={{ fontSize: '0.82rem', color: '#9ca3af' }}>Verbatim Resume Proof</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {demoData.report.evidence_snippets.slice(0, 3).map((ev, idx) => (
                    <div key={idx} style={{ background: 'rgba(0,0,0,0.25)', padding: '12px', borderRadius: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span style={{ fontWeight: 700, color: '#c7d2fe', fontSize: '0.86rem' }}>{ev.skill}</span>
                        <span style={{ fontSize: '0.74rem', color: '#818cf8' }}>{ev.source_section}</span>
                      </div>
                      <div style={{ fontSize: '0.82rem', color: '#d1d5db', fontStyle: 'italic' }}>
                        "{ev.snippet}"
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {demoData.report?.interview_questions?.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Personalized Interview Questions</h3>
                  <span style={{ fontSize: '0.82rem', color: '#9ca3af' }}>Tailored to Claims & Gaps</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {demoData.report.interview_questions.slice(0, 2).map((q, idx) => (
                    <div key={idx} style={{ background: 'rgba(0,0,0,0.25)', padding: '14px', borderRadius: '8px' }}>
                      <span className="badge badge-skill" style={{ marginBottom: '6px' }}>{q.category}</span>
                      <div style={{ fontWeight: 600, fontSize: '0.88rem', color: '#f9fafb', marginBottom: '4px' }}>
                        "{q.question}"
                      </div>
                      <div style={{ fontSize: '0.78rem', color: '#9ca3af' }}>
                        {q.rationale}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
