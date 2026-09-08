import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function JobsPage({ onSelectJobForEvaluation }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    department: 'Engineering',
    location: 'Remote',
    experience_required: 2,
    education_required: "Bachelor's Degree",
  });

  const loadJobs = async () => {
    try {
      setLoading(true);
      const data = await api.getJobs();
      setJobs(data);
    } catch (err) {
      console.error('Failed to load jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const handleCreateJob = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.createJob(formData);
      setFormData({
        title: '',
        description: '',
        department: 'Engineering',
        location: 'Remote',
        experience_required: 2,
        education_required: "Bachelor's Degree",
      });
      setShowForm(false);
      await loadJobs();
    } catch (err) {
      alert('Error creating job: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleReanalyze = async (jobId) => {
    try {
      await api.analyzeJob(jobId);
      await loadJobs();
      alert('Job requirements re-analyzed with AI successfully!');
    } catch (err) {
      alert('Re-analysis failed: ' + err.message);
    }
  };

  const handleDelete = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job posting?')) return;
    try {
      await api.deleteJob(jobId);
      await loadJobs();
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem' }}>Job Requisitions</h2>
          <p style={{ color: '#9ca3af', fontSize: '0.88rem' }}>
            Manage active roles with AI-extracted required and preferred skills
          </p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? '✕ Close Form' : '+ New Job Requisition'}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '32px', borderColor: 'rgba(99, 102, 241, 0.4)' }}>
          <h3 className="card-title" style={{ marginBottom: '16px' }}>Create Job Requisition</h3>
          <form onSubmit={handleCreateJob}>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Job Title *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Senior Python Backend Engineer"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Department</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Core Platform / AI"
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                />
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Location</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Remote / San Francisco, CA"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Min Experience (Years)</label>
                <input
                  type="number"
                  step="0.5"
                  className="form-input"
                  value={formData.experience_required}
                  onChange={(e) => setFormData({ ...formData, experience_required: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">
                Job Description * (Paste text for automatic AI skill & requirement extraction)
              </label>
              <textarea
                className="form-textarea"
                rows={6}
                placeholder="Paste the full job description here. The AI Recruitment Agent will automatically extract required skills, preferred technologies, education criteria, and responsibilities."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                required
              ></textarea>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? 'Extracting & Saving...' : 'Save & Extract Requirements with AI'}
              </button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px 0', color: '#9ca3af' }}>Loading jobs...</div>
      ) : jobs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px 0' }}>
          <p style={{ color: '#9ca3af', marginBottom: '16px' }}>No job requisitions created yet.</p>
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            Create First Job
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {jobs.map((job) => (
            <div key={job.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', marginBottom: '4px' }}>{job.title}</h3>
                  <div style={{ display: 'flex', gap: '14px', color: '#9ca3af', fontSize: '0.84rem' }}>
                    <span>🏢 {job.department || 'Engineering'}</span>
                    <span>📍 {job.location || 'Remote'}</span>
                    <span>⏱️ {job.experience_required} Years Required</span>
                    <span>🎓 {job.education_required || 'Degree specified'}</span>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => onSelectJobForEvaluation(job.id)}
                  >
                    🎯 Evaluate Candidates
                  </button>
                  <button
                    className="btn btn-secondary btn-sm"
                    title="Re-run AI requirements extraction"
                    onClick={() => handleReanalyze(job.id)}
                  >
                    ⚡ Re-Analyze
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(job.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#818cf8', fontWeight: 700, marginBottom: '8px' }}>
                  Mandatory Required Skills (AI-Extracted):
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {job.required_skills?.map((s, idx) => (
                    <span key={idx} className="badge badge-skill" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#c7d2fe', borderColor: 'rgba(99, 102, 241, 0.3)' }}>
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {job.preferred_skills?.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#9ca3af', fontWeight: 700, marginBottom: '8px' }}>
                    Preferred Skills:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {job.preferred_skills.map((s, idx) => (
                      <span key={idx} className="badge badge-skill">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
