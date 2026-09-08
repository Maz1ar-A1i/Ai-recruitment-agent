/**
 * Frontend REST API client for AI Recruitment Agent
 */

const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = options.headers || {};
  
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) errorMsg = errJson.detail;
    } catch (_) {}
    throw new Error(errorMsg);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  // Demo & Dashboard Telemetry
  getStats: () => request('/demo/stats'),
  seedDemo: () => request('/demo/seed', { method: 'POST' }),
  runDemo: () => request('/demo/run', { method: 'POST' }),

  // Jobs
  getJobs: () => request('/jobs'),
  getJob: (id) => request(`/jobs/${id}`),
  createJob: (payload) => request('/jobs', { method: 'POST', body: JSON.stringify(payload) }),
  analyzeJob: (id) => request(`/jobs/${id}/analyze`, { method: 'POST' }),
  deleteJob: (id) => request(`/jobs/${id}`, { method: 'DELETE' }),

  // Candidates
  getCandidates: () => request('/candidates'),
  getCandidate: (id) => request(`/candidates/${id}`),
  uploadResume: (formData) => request('/candidates/upload', { method: 'POST', body: formData }),
  deleteCandidate: (id) => request(`/candidates/${id}`, { method: 'DELETE' }),

  // Recruitment Evaluation & Decisions
  evaluateCandidate: (jobId, candidateId) =>
    request('/recruitment/evaluate', {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId, candidate_id: candidateId }),
    }),
  evaluateBatch: (jobId, candidateIds) =>
    request('/recruitment/evaluate-batch', {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId, candidate_ids: candidateIds }),
    }),
  getEvaluation: (id) => request(`/recruitment/results/${id}`),
  getJobEvaluations: (jobId) => request(`/recruitment/job/${jobId}/evaluations`),
  submitDecision: (payload) =>
    request('/recruitment/decide', { method: 'POST', body: JSON.stringify(payload) }),
  getDecisions: (evaluationId) => request(`/recruitment/decisions/${evaluationId}`),

  // Agent Execution & Tools
  getAgentRuns: () => request('/agent/runs'),
  getAgentRun: (id) => request(`/agent/runs/${id}`),
  getAgentStatus: () => request('/agent/status'),
  getTools: () => request('/tools'),

  // Knowledge Base & RAG
  getKnowledgeDocs: () => request('/knowledge'),
  getKnowledgeDoc: (id) => request(`/knowledge/${id}`),
  uploadKnowledge: (formData) => request('/knowledge/upload', { method: 'POST', body: formData }),
  queryKnowledge: (query) =>
    request('/knowledge/query', { method: 'POST', body: JSON.stringify({ query }) }),
  deleteKnowledgeDoc: (id) => request(`/knowledge/${id}`, { method: 'DELETE' }),

  // Evaluation Benchmark
  getMetrics: () => request('/evaluation/metrics'),
  runBenchmark: () => request('/evaluation/run-benchmark', { method: 'POST' }),
};
