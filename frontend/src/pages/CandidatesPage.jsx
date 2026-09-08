import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function CandidatesPage({ onSelectCandidateForEvaluation }) {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const loadCandidates = async () => {
    try {
      setLoading(true);
      const data = await api.getCandidates();
      setCandidates(data);
    } catch (err) {
      console.error('Failed to load candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      await api.uploadResume(formData);
      await loadCandidates();
      alert(`Resume '${file.name}' successfully parsed and de-biased!`);
    } catch (err) {
      alert('Upload failed: ' + err.message);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (candidateId) => {
    if (!window.confirm('Delete this candidate profile?')) return;
    try {
      await api.deleteCandidate(candidateId);
      await loadCandidates();
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem' }}>Candidate Profiles</h2>
          <p style={{ color: '#9ca3af', fontSize: '0.88rem' }}>
            Parsed resumes with normalized skills, verified work history, and de-biasing
          </p>
        </div>

        <div style={{ position: 'relative' }}>
          <input
            type="file"
            id="resumeUploadInput"
            style={{ display: 'none' }}
            accept=".pdf,.docx,.txt"
            onChange={handleFileUpload}
            disabled={uploading}
          />
          <button
            className="btn btn-primary"
            onClick={() => document.getElementById('resumeUploadInput').click()}
            disabled={uploading}
          >
            {uploading ? 'Parsing & De-biasing...' : '+ Upload Resume (PDF/DOCX/TXT)'}
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px 0', color: '#9ca3af' }}>Loading candidates...</div>
      ) : candidates.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '48px 0' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>📄</div>
          <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>No candidates uploaded yet</h3>
          <p style={{ color: '#9ca3af', marginBottom: '18px' }}>
            Upload a PDF, DOCX, or TXT resume to experience automatic parsing and skill normalization.
          </p>
          <button
            className="btn btn-primary"
            onClick={() => document.getElementById('resumeUploadInput').click()}
          >
            Upload First Resume
          </button>
        </div>
      ) : (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Experience</th>
                <th>Normalized Skills</th>
                <th>Source File</th>
                <th>Uploaded</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((cand) => (
                <tr key={cand.id}>
                  <td>
                    <div style={{ fontWeight: 600, color: '#f9fafb', fontSize: '0.96rem' }}>{cand.name}</div>
                    <div style={{ fontSize: '0.78rem', color: '#9ca3af' }}>{cand.email || 'No email provided'}</div>
                  </td>
                  <td>
                    <span style={{ fontWeight: 600 }}>{cand.years_of_experience} yrs</span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', maxWidth: '380px' }}>
                      {cand.skills?.slice(0, 5).map((s, idx) => (
                        <span key={idx} className="badge badge-skill" style={{ fontSize: '0.74rem' }}>
                          {s}
                        </span>
                      ))}
                      {cand.skills?.length > 5 && (
                        <span style={{ fontSize: '0.75rem', color: '#9ca3af', alignSelf: 'center' }}>
                          +{cand.skills.length - 5} more
                        </span>
                      )}
                    </div>
                  </td>
                  <td>
                    <span style={{ color: '#9ca3af', fontSize: '0.82rem' }}>{cand.file_name || 'raw_text'}</span>
                  </td>
                  <td style={{ color: '#9ca3af', fontSize: '0.82rem' }}>
                    {new Date(cand.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => onSelectCandidateForEvaluation(cand.id)}
                      >
                        Evaluate
                      </button>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => setSelectedCandidate(cand)}
                      >
                        Profile
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(cand.id)}
                      >
                        ✕
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Candidate Detailed Profile Modal */}
      {selectedCandidate && (
        <div className="modal-overlay" onClick={() => setSelectedCandidate(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h2 style={{ fontSize: '1.3rem' }}>{selectedCandidate.name}</h2>
                <span style={{ color: '#9ca3af', fontSize: '0.85rem' }}>{selectedCandidate.email} • {selectedCandidate.phone || 'N/A'}</span>
              </div>
              <button className="btn btn-secondary btn-sm" onClick={() => setSelectedCandidate(null)}>✕</button>
            </div>

            {selectedCandidate.summary && (
              <div style={{ marginBottom: '18px', background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#a5b4fc', fontWeight: 700, marginBottom: '4px' }}>
                  Professional Summary:
                </div>
                <p style={{ fontSize: '0.88rem', color: '#d1d5db' }}>{selectedCandidate.summary}</p>
              </div>
            )}

            <div style={{ marginBottom: '18px' }}>
              <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#818cf8', fontWeight: 700, marginBottom: '8px' }}>
                Normalized Skills ({selectedCandidate.skills?.length || 0}):
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {selectedCandidate.skills?.map((s, idx) => (
                  <span key={idx} className="badge badge-skill">{s}</span>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '18px' }}>
              <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#34d399', fontWeight: 700, marginBottom: '8px' }}>
                Work Experience ({selectedCandidate.years_of_experience} yrs total):
              </div>
              {selectedCandidate.experience?.map((exp, idx) => (
                <div key={idx} style={{ background: 'rgba(31, 41, 55, 0.5)', padding: '12px', borderRadius: '8px', marginBottom: '8px' }}>
                  <div style={{ fontWeight: 600, color: '#f3f4f6' }}>{exp.role} — {exp.company}</div>
                  <div style={{ fontSize: '0.8rem', color: '#9ca3af', marginBottom: '6px' }}>{exp.duration}</div>
                  <p style={{ fontSize: '0.85rem', color: '#d1d5db' }}>{exp.description}</p>
                </div>
              ))}
            </div>

            {selectedCandidate.projects?.length > 0 && (
              <div style={{ marginBottom: '18px' }}>
                <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#fbbf24', fontWeight: 700, marginBottom: '8px' }}>
                  Key Projects:
                </div>
                {selectedCandidate.projects.map((proj, idx) => (
                  <div key={idx} style={{ background: 'rgba(31, 41, 55, 0.5)', padding: '12px', borderRadius: '8px', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 600, color: '#f3f4f6' }}>{proj.name}</div>
                    <p style={{ fontSize: '0.85rem', color: '#d1d5db' }}>{proj.description}</p>
                  </div>
                ))}
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button className="btn btn-secondary" onClick={() => setSelectedCandidate(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
