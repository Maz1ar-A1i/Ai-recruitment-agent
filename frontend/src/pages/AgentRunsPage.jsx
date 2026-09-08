import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import AgentTraceTimeline from '../components/AgentTraceTimeline';

export default function AgentRunsPage({ initialRunId }) {
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadRuns = async () => {
    try {
      setLoading(true);
      const data = await api.getAgentRuns();
      setRuns(data);
      if (initialRunId) {
        loadRunDetails(initialRunId);
      } else if (data.length > 0 && !selectedRun) {
        loadRunDetails(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load agent runs:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRunDetails = async (runId) => {
    try {
      const detailed = await api.getAgentRun(runId);
      setSelectedRun(detailed);
    } catch (err) {
      console.error('Failed to load run details:', err);
    }
  };

  useEffect(() => {
    loadRuns();
  }, [initialRunId]);

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.4rem' }}>Agent Execution Runs & Telemetry</h2>
        <p style={{ color: '#9ca3af', fontSize: '0.88rem' }}>
          Inspect step-by-step agent traces, tool inputs/outputs, thoughts, and execution timings
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '24px', alignItems: 'start' }}>
        {/* Runs List Sidebar */}
        <div className="card" style={{ padding: '16px' }}>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '14px', color: '#f3f4f6' }}>
            Historical Agent Runs ({runs.length})
          </div>

          {loading && !runs.length ? (
            <div style={{ color: '#9ca3af', fontSize: '0.85rem' }}>Loading runs...</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '600px', overflowY: 'auto' }}>
              {runs.map((r) => (
                <div
                  key={r.id}
                  onClick={() => loadRunDetails(r.id)}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    background: selectedRun?.id === r.id ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255,255,255,0.03)',
                    border: `1px solid ${selectedRun?.id === r.id ? 'rgba(99, 102, 241, 0.4)' : 'transparent'}`,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <code style={{ fontSize: '0.78rem', color: '#818cf8' }}>#{r.id.slice(0, 8)}</code>
                    <span className={`badge ${r.status === 'COMPLETED' ? 'badge-strong' : 'badge-weak'}`} style={{ fontSize: '0.7rem' }}>
                      {r.status}
                    </span>
                  </div>

                  <div style={{ fontWeight: 600, fontSize: '0.86rem', color: '#f3f4f6', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {r.task}
                  </div>

                  <div style={{ display: 'flex', gap: '10px', color: '#9ca3af', fontSize: '0.76rem', marginTop: '6px' }}>
                    <span>⏱️ {r.duration_seconds}s</span>
                    <span>🐾 {r.total_steps} Steps</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Selected Run Trace Detail */}
        <div>
          {selectedRun ? (
            <div>
              <div className="card" style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontSize: '0.76rem', color: '#818cf8', fontWeight: 700, textTransform: 'uppercase' }}>
                      Selected Agent Run Trace
                    </span>
                    <h3 style={{ fontSize: '1.25rem', marginTop: '2px' }}>{selectedRun.task}</h3>
                    <code style={{ fontSize: '0.8rem', color: '#9ca3af' }}>ID: {selectedRun.id}</code>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div className={`badge ${selectedRun.status === 'COMPLETED' ? 'badge-strong' : 'badge-weak'}`} style={{ fontSize: '0.85rem' }}>
                      {selectedRun.status}
                    </div>
                    <div style={{ fontSize: '0.82rem', color: '#9ca3af', marginTop: '4px' }}>
                      Duration: <strong>{selectedRun.duration_seconds}s</strong> • Steps: <strong>{selectedRun.total_steps}</strong>
                    </div>
                  </div>
                </div>
              </div>

              <AgentTraceTimeline steps={selectedRun.steps} />
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '60px 0', color: '#9ca3af' }}>
              Select an agent run from the list to inspect its tool calling execution trace.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
