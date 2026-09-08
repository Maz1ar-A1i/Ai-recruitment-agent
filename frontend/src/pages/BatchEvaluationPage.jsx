import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import ScoreBadge from '../components/ScoreBadge';

export default function BatchEvaluationPage({ onSelectEvaluation }) {
  const [jobs, setJobs] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState('');
  const [selectedCandidateIds, setSelectedCandidateIds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [batchResults, setBatchResults] = useState(null);
  const [sortBy, setSortBy] = useState('score');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [jList, cList] = await Promise.all([api.getJobs(), api.getCandidates()]);
        setJobs(jList);
        setCandidates(cList);
        if (jList.length > 0) setSelectedJobId(jList[0].id);
        if (cList.length > 0) setSelectedCandidateIds(cList.map(c => c.id));
      } catch (err) {
        console.error('Failed to load initial data:', err);
      }
    };
    fetchData();
  }, []);

  const handleToggleCandidate = (id) => {
    if (selectedCandidateIds.includes(id)) {
      setSelectedCandidateIds(selectedCandidateIds.filter(cId => cId !== id));
    } else {
      setSelectedCandidateIds([...selectedCandidateIds, id]);
    }
  };

  const handleSelectAll = () => {
    if (selectedCandidateIds.length === candidates.length) {
      setSelectedCandidateIds([]);
    } else {
      setSelectedCandidateIds(candidates.map(c => c.id));
    }
  };

  const handleRunBatch = async () => {
    if (!selectedJobId || selectedCandidateIds.length === 0) {
      alert('Please select a job and at least one candidate.');
      return;
    }

    try {
      setLoading(true);
      const res = await api.evaluateBatch(selectedJobId, selectedCandidateIds);
      setBatchResults(res);
    } catch (err) {
      alert('Batch evaluation failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSortedResults = () => {
    if (!batchResults?.results) return [];
    const list = [...batchResults.results];
    if (sortBy === 'score') {
      list.sort((a, b) => (b.score || 0) - (a.score || 0));
    } else if (sortBy === 'name') {
      list.sort((a, b) => a.candidate_name.localeCompare(b.candidate_name));
    }
    return list;
  };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.4rem' }}>Batch Evaluation & Candidate Ranking</h2>
        <p style={{ color: '#9ca3af', fontSize: '0.88rem' }}>
          Evaluate multiple candidates simultaneously with failure resilience and deterministic ranking
        </p>
      </div>

      {/* Control Card */}
      <div className="card" style={{ marginBottom: '28px' }}>
        <div className="form-group">
          <label className="form-label">Target Job Requisition</label>
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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <label className="form-label" style={{ margin: 0 }}>Select Candidates for Batch Pipeline</label>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={handleSelectAll}
            >
              {selectedCandidateIds.length === candidates.length ? 'Deselect All' : 'Select All'}
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '10px', maxHeight: '180px', overflowY: 'auto', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px' }}>
            {candidates.map((c) => (
              <label
                key={c.id}
                style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.86rem', color: '#e5e7eb' }}
              >
                <input
                  type="checkbox"
                  checked={selectedCandidateIds.includes(c.id)}
                  onChange={() => handleToggleCandidate(c.id)}
                />
                <span>{c.name} ({c.years_of_experience} yrs)</span>
              </label>
            ))}
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleRunBatch}
          disabled={loading || selectedCandidateIds.length === 0}
          style={{ width: '100%', padding: '12px' }}
        >
          {loading ? 'Batch Pipeline Evaluating Candidates...' : `⚡ Run Batch Evaluation (${selectedCandidateIds.length} Candidates)`}
        </button>
      </div>

      {/* Results Section */}
      {batchResults && (
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">Candidate Rankings & Leaderboard</h3>
              <span style={{ fontSize: '0.82rem', color: '#9ca3af' }}>
                Evaluated {batchResults.total} candidates: {batchResults.successful} Successful, {batchResults.failed} Failed
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '0.84rem', color: '#9ca3af' }}>Sort by:</span>
              <select
                className="form-select"
                style={{ padding: '6px 12px', fontSize: '0.82rem', width: 'auto' }}
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="score">Highest Match Score</option>
                <option value="name">Candidate Name</option>
              </select>
            </div>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Candidate</th>
                  <th>Match Score</th>
                  <th>Recommendation</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {getSortedResults().map((item, idx) => (
                  <tr key={item.candidate_id}>
                    <td>
                      <div style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        background: idx === 0 ? 'rgba(245, 158, 11, 0.2)' : 'rgba(255,255,255,0.06)',
                        color: idx === 0 ? '#fbbf24' : '#9ca3af',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 700,
                        fontSize: '0.85rem'
                      }}>
                        #{idx + 1}
                      </div>
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, color: '#f9fafb' }}>{item.candidate_name}</div>
                      {item.error && (
                        <div style={{ color: '#f87171', fontSize: '0.78rem' }}>{item.error}</div>
                      )}
                    </td>
                    <td>
                      {item.score !== undefined && item.score !== null ? (
                        <span style={{ fontWeight: 800, fontSize: '1.1rem', color: '#f3f4f6' }}>
                          {item.score}/100
                        </span>
                      ) : (
                        <span style={{ color: '#9ca3af' }}>—</span>
                      )}
                    </td>
                    <td>
                      {item.recommendation ? (
                        <ScoreBadge recommendation={item.recommendation} />
                      ) : (
                        <span style={{ color: '#9ca3af' }}>—</span>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${item.status === 'SUCCESS' ? 'badge-strong' : 'badge-weak'}`}>
                        {item.status}
                      </span>
                    </td>
                    <td>
                      {item.evaluation_id && (
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => onSelectEvaluation(item.evaluation_id)}
                        >
                          View Report →
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
