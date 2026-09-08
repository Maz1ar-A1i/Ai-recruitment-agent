import React, { useState } from 'react';

export default function AgentTraceTimeline({ steps = [] }) {
  const [expandedStep, setExpandedStep] = useState(null);

  const toggleStep = (index) => {
    setExpandedStep(expandedStep === index ? null : index);
  };

  const getStepIcon = (toolName) => {
    switch (toolName) {
      case 'extract_job_requirements': return '📋';
      case 'parse_resume': return '📄';
      case 'extract_candidate_skills': return '⚡';
      case 'match_candidate_to_job': return '🔍';
      case 'identify_skill_gaps': return '⚠️';
      case 'calculate_candidate_score': return '🧮';
      case 'generate_interview_questions': return '💬';
      case 'generate_candidate_report': return '📊';
      case 'validate_candidate_report': return '🛡️';
      case 'compute_semantic_similarity': return '🧠';
      default: return '⚙️';
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h3 className="card-title">Agent Activity & Execution Trace</h3>
          <p style={{ fontSize: '0.82rem', color: '#9ca3af', marginTop: '2px' }}>
            Multi-step tool calling loop with granular telemetry and verification
          </p>
        </div>
        <span className="badge badge-skill">{steps.length} Steps Executed</span>
      </div>

      <div className="timeline">
        {steps.map((step, idx) => {
          const isExpanded = expandedStep === idx;
          return (
            <div key={step.id || idx} className="timeline-step">
              <div className={`timeline-dot ${step.status === 'SUCCESS' ? 'success' : ''}`}>
                {step.step_number || idx + 1}
              </div>

              <div
                className="timeline-content"
                onClick={() => toggleStep(idx)}
                style={{ cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '1.1rem' }}>{getStepIcon(step.tool_name)}</span>
                    <span style={{ fontWeight: 600, color: '#f3f4f6', fontSize: '0.94rem' }}>
                      Tool: <code style={{ color: '#818cf8', background: 'rgba(99,102,241,0.1)', padding: '2px 6px', borderRadius: '4px' }}>{step.tool_name}</code>
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
                      ⏱️ {step.execution_time_ms ? `${step.execution_time_ms} ms` : '< 10 ms'}
                    </span>
                    <span className={`badge ${step.status === 'SUCCESS' ? 'badge-strong' : 'badge-weak'}`} style={{ fontSize: '0.72rem' }}>
                      {step.status}
                    </span>
                    <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>
                      {isExpanded ? '▲' : '▼'}
                    </span>
                  </div>
                </div>

                {step.thought && (
                  <div style={{ marginTop: '8px', fontSize: '0.86rem', color: '#9ca3af', fontStyle: 'italic' }}>
                    "{step.thought}"
                  </div>
                )}

                {isExpanded && (
                  <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                    <div style={{ marginBottom: '12px' }}>
                      <div style={{ fontSize: '0.76rem', textTransform: 'uppercase', color: '#818cf8', fontWeight: 700, marginBottom: '4px' }}>
                        Tool Input:
                      </div>
                      <pre style={{ background: '#0b0f19', padding: '10px 12px', borderRadius: '6px', fontSize: '0.78rem', overflowX: 'auto', color: '#d1d5db' }}>
                        {JSON.stringify(step.tool_input, null, 2)}
                      </pre>
                    </div>

                    <div>
                      <div style={{ fontSize: '0.76rem', textTransform: 'uppercase', color: '#34d399', fontWeight: 700, marginBottom: '4px' }}>
                        Tool Output:
                      </div>
                      <pre style={{ background: '#0b0f19', padding: '10px 12px', borderRadius: '6px', fontSize: '0.78rem', overflowX: 'auto', color: '#d1d5db', maxHeight: '250px' }}>
                        {JSON.stringify(step.tool_output, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
