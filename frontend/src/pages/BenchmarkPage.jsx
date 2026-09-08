import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function BenchmarkPage() {
  const [metricsData, setMetricsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const data = await api.getMetrics();
      setMetricsData(data);
    } catch (err) {
      console.error('Failed to load benchmark metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  const handleRunBenchmark = async () => {
    try {
      setRunning(true);
      const res = await api.runBenchmark();
      setMetricsData(res);
    } catch (err) {
      alert('Benchmark execution failed: ' + err.message);
    } finally {
      setRunning(false);
    }
  };

  const isNotEvaluated = !metricsData || metricsData.status === 'NOT_EVALUATED';

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem' }}>AI Quality & Accuracy Benchmark</h2>
          <p style={{ color: '#9ca3af', fontSize: '0.88rem' }}>
            Empirical validation against curated ground-truth evaluation dataset (no fabricated numbers)
          </p>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleRunBenchmark}
          disabled={running}
        >
          {running ? 'Evaluating Ground Truth Suite...' : '⚡ Run Benchmark Suite'}
        </button>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid-3" style={{ marginBottom: '28px' }}>
        <div className="card">
          <div style={{ color: '#9ca3af', fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase' }}>
            Structured Output Validity
          </div>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, marginTop: '6px', color: '#10b981', fontFamily: 'var(--font-heading)' }}>
            {isNotEvaluated ? 'Not Evaluated' : metricsData.metrics.structured_output_validity}
          </div>
          <div style={{ fontSize: '0.78rem', color: '#9ca3af', marginTop: '4px' }}>
            Pydantic schema conformity & zero parse errors
          </div>
        </div>

        <div className="card">
          <div style={{ color: '#9ca3af', fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase' }}>
            Skill Extraction Accuracy
          </div>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, marginTop: '6px', color: '#6366f1', fontFamily: 'var(--font-heading)' }}>
            {isNotEvaluated ? 'Not Evaluated' : metricsData.metrics.skill_extraction_accuracy}
          </div>
          <div style={{ fontSize: '0.78rem', color: '#9ca3af', marginTop: '4px' }}>
            Alias normalization vs expected ground truth skills
          </div>
        </div>

        <div className="card">
          <div style={{ color: '#9ca3af', fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase' }}>
            Agent Completion Rate
          </div>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, marginTop: '6px', color: '#3b82f6', fontFamily: 'var(--font-heading)' }}>
            {isNotEvaluated ? 'Not Evaluated' : metricsData.metrics.agent_completion_rate}
          </div>
          <div style={{ fontSize: '0.78rem', color: '#9ca3af', marginTop: '4px' }}>
            Multi-tool loops concluding without step exhaustion
          </div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: '28px' }}>
        <div className="card">
          <div style={{ color: '#9ca3af', fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase' }}>
            Tool Execution Success
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, marginTop: '6px', color: '#10b981', fontFamily: 'var(--font-heading)' }}>
            {isNotEvaluated ? 'Not Evaluated' : metricsData.metrics.tool_execution_success}
          </div>
          <div style={{ fontSize: '0.78rem', color: '#9ca3af', marginTop: '4px' }}>
            Zero unhandled exceptions across tool executions
          </div>
        </div>

        <div className="card">
          <div style={{ color: '#9ca3af', fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase' }}>
            Recommendation Consistency
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, marginTop: '6px', color: '#f59e0b', fontFamily: 'var(--font-heading)' }}>
            {isNotEvaluated ? 'Not Evaluated' : metricsData.metrics.recommendation_consistency}
          </div>
          <div style={{ fontSize: '0.78rem', color: '#9ca3af', marginTop: '4px' }}>
            Agreement with expected ground-truth tiering
          </div>
        </div>
      </div>

      {/* Ground Truth Evaluation Details */}
      {!isNotEvaluated && metricsData.details && (
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">Curated Dataset Benchmark Trace</h3>
              <span style={{ fontSize: '0.82rem', color: '#9ca3af' }}>
                Evaluated {metricsData.sample_size?.candidates} candidates across {metricsData.sample_size?.jobs} jobs in {metricsData.duration_seconds}s
              </span>
            </div>
            <span style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
              Timestamp: {metricsData.evaluated_at}
            </span>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Target Job</th>
                  <th>Calculated Score</th>
                  <th>Computed Rec</th>
                  <th>Expected Rec</th>
                  <th>Matched Skills</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {metricsData.details.map((row, idx) => (
                  <tr key={idx}>
                    <td><strong style={{ color: '#f3f4f6' }}>{row.candidate_name}</strong></td>
                    <td style={{ color: '#9ca3af', fontSize: '0.85rem' }}>{row.target_job}</td>
                    <td><strong style={{ fontSize: '1rem' }}>{row.calculated_score}/100</strong></td>
                    <td>
                      <span className={`badge ${
                        row.recommendation === 'Strong Match' ? 'badge-strong' :
                        row.recommendation === 'Match' ? 'badge-match' :
                        row.recommendation === 'Weak Match' ? 'badge-weak' : 'badge-potential'
                      }`}>
                        {row.recommendation}
                      </span>
                    </td>
                    <td>
                      <span style={{ color: '#9ca3af', fontSize: '0.82rem' }}>
                        {row.expected_recommendation || 'N/A'}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontWeight: 600, color: '#818cf8' }}>
                        {row.matching_skills_count} skills
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${row.status === 'SUCCESS' ? 'badge-strong' : 'badge-weak'}`}>
                        {row.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {isNotEvaluated && (
        <div className="card" style={{ textAlign: 'center', padding: '50px 0', color: '#9ca3af' }}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>📊</div>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '6px' }}>Benchmark Suite Not Run Yet</h3>
          <p style={{ maxWidth: '500px', margin: '0 auto 20px', fontSize: '0.88rem' }}>
            Click the <strong>Run Benchmark Suite</strong> button to execute the evaluation pipeline across curated test jobs and candidate resumes.
          </p>
          <button className="btn btn-primary" onClick={handleRunBenchmark} disabled={running}>
            {running ? 'Running...' : 'Run Benchmark Now'}
          </button>
        </div>
      )}
    </div>
  );
}
