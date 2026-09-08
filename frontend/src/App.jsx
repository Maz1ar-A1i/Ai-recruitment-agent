import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import DashboardPage from './pages/DashboardPage';
import JobsPage from './pages/JobsPage';
import CandidatesPage from './pages/CandidatesPage';
import EvaluationPage from './pages/EvaluationPage';
import BatchEvaluationPage from './pages/BatchEvaluationPage';
import AgentRunsPage from './pages/AgentRunsPage';
import KnowledgeBasePage from './pages/KnowledgeBasePage';
import BenchmarkPage from './pages/BenchmarkPage';
import DemoPage from './pages/DemoPage';
import { api } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedEvaluationId, setSelectedEvaluationId] = useState(null);
  const [preselectedJobId, setPreselectedJobId] = useState(null);
  const [preselectedCandidateId, setPreselectedCandidateId] = useState(null);
  const [selectedRunId, setSelectedRunId] = useState(null);
  const [isDemoRunning, setIsDemoRunning] = useState(false);

  const getPageTitle = () => {
    switch (activeTab) {
      case 'dashboard': return 'Executive Talent Dashboard';
      case 'jobs': return 'Job Requisitions & Requirements';
      case 'candidates': return 'Candidate Resume Directory';
      case 'evaluation': return 'Candidate Match & Evaluation Report';
      case 'batch': return 'Batch Evaluation & Candidate Ranking';
      case 'agent-runs': return 'Agent Execution Trace & Telemetry';
      case 'knowledge': return 'Hiring Guidelines & Competency (RAG)';
      case 'benchmark': return 'AI Quality & Accuracy Metrics';
      case 'demo': return '1-Click Interactive Agent Demo';
      default: return 'RecruitAgent';
    }
  };

  const handleGlobalQuickDemo = async () => {
    try {
      setIsDemoRunning(true);
      await api.runDemo();
      setActiveTab('demo');
    } catch (err) {
      alert('Quick demo failed: ' + err.message);
    } finally {
      setIsDemoRunning(false);
    }
  };

  const handleSelectJobForEvaluation = (jobId) => {
    setPreselectedJobId(jobId);
    setActiveTab('evaluation');
  };

  const handleSelectCandidateForEvaluation = (candId) => {
    setPreselectedCandidateId(candId);
    setActiveTab('evaluation');
  };

  const handleSelectEvaluation = (evalId) => {
    setSelectedEvaluationId(evalId);
    setActiveTab('evaluation');
  };

  const handleInspectRun = (runId) => {
    setSelectedRunId(runId);
    setActiveTab('agent-runs');
  };

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <div className="main-content">
        <Topbar
          title={getPageTitle()}
          onRunDemo={handleGlobalQuickDemo}
          isDemoLoading={isDemoRunning}
        />

        <main className="page-body">
          {activeTab === 'dashboard' && (
            <DashboardPage
              onNavigate={setActiveTab}
              onSelectEvaluation={handleSelectEvaluation}
            />
          )}

          {activeTab === 'jobs' && (
            <JobsPage
              onSelectJobForEvaluation={handleSelectJobForEvaluation}
            />
          )}

          {activeTab === 'candidates' && (
            <CandidatesPage
              onSelectCandidateForEvaluation={handleSelectCandidateForEvaluation}
            />
          )}

          {activeTab === 'evaluation' && (
            <EvaluationPage
              evaluationId={selectedEvaluationId}
              preselectedJobId={preselectedJobId}
              preselectedCandidateId={preselectedCandidateId}
            />
          )}

          {activeTab === 'batch' && (
            <BatchEvaluationPage
              onSelectEvaluation={handleSelectEvaluation}
            />
          )}

          {activeTab === 'agent-runs' && (
            <AgentRunsPage
              initialRunId={selectedRunId}
            />
          )}

          {activeTab === 'knowledge' && (
            <KnowledgeBasePage />
          )}

          {activeTab === 'benchmark' && (
            <BenchmarkPage />
          )}

          {activeTab === 'demo' && (
            <DemoPage
              onSelectEvaluation={handleSelectEvaluation}
              onInspectRun={handleInspectRun}
            />
          )}
        </main>
      </div>
    </div>
  );
}
