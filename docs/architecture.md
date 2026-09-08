# System Architecture Specification: AI Recruitment Agent

## 1. High-Level Architecture Overview

The **AI Recruitment Agent** is a multi-tier decision-support system designed to automate candidate evaluation while keeping a human recruiter in the loop.

```mermaid
flowchart TD
    subgraph UI[Client Layer - React / Vite]
        A[Recruiter Dashboard]
        B[Interactive Agent Trace]
        C[Batch Evaluation & Ranking]
        D[Human-in-the-Loop Review]
    end

    subgraph API[API Layer - FastAPI]
        E[Jobs API /api/jobs]
        F[Candidates API /api/candidates]
        G[Recruitment API /api/recruitment]
        H[Agent Telemetry /api/agent]
        I[RAG Knowledge Base /api/knowledge]
        J[Quality Benchmark /api/evaluation]
    end

    subgraph AgentCore[Agentic Orchestration Core]
        K[RecruitmentAgent]
        L[Typed State: RecruitmentState]
        M[Planner / Decision Layer]
        N[ToolRegistry]
    end

    subgraph ToolEngine[Autonomous Tool Engine]
        T1[extract_job_requirements]
        T2[parse_resume & de_bias]
        T3[extract_candidate_skills]
        T4[match_candidate_to_job]
        T5[identify_skill_gaps]
        T6[calculate_candidate_score]
        T7[generate_interview_questions]
        T8[generate_candidate_report]
        T9[validate_candidate_report]
        T10[compute_semantic_similarity]
    end

    subgraph LLMLayer[Resilient LLM Service]
        P[LLMService]
        Q1[GeminiProvider]
        Q2[OpenAIProvider]
        Q3[MockLLMProvider Offline]
    end

    subgraph Storage[Persistence & RAG]
        S1[(SQLite / SQLAlchemy)]
        S2[Lightweight TF-IDF / Cosine Vector Store]
    end

    UI --> API
    API --> AgentCore
    AgentCore --> N
    N --> ToolEngine
    ToolEngine --> LLMLayer
    ToolEngine --> Storage
    AgentCore --> S1
    API --> S2
```

---

## 2. Core Architectural Principles

### A. Agentic Tool Calling vs Prompt Chaining
Unlike conventional conversational chatbots that process input through a single giant prompt, this system implements a goal-driven loop:
1. **Perception**: Evaluates the current `RecruitmentState`.
2. **Planning**: Decides which tool is necessary based on missing or incomplete intermediate state variables.
3. **Action**: Executes the selected tool via the centralized `ToolRegistry`.
4. **Validation & Self-Healing**: Validates the output against rule-based constraints (e.g., verifying mathematical score consistency and evidence alignment). Discrepancies trigger a self-correction repair loop.
5. **Traceability**: Every step records its thought, input arguments, output payload, status, and duration in `AgentStep` database records.

### B. Transparent Deterministic Scoring
To prevent LLM score hallucinations, numerical evaluation scores are calculated mathematically by `calculate_candidate_score`:
- **Core Skills Match**: 50%
- **Experience Depth**: 20%
- **Education Alignment**: 10%
- **Preferred Skills**: 10%
- **Project Relevance**: 10%
- **Total**: 100%

### C. Bias Mitigation & Fairness
The system automatically sanitizes candidate resumes prior to skill extraction and matching by removing sensitive personal attributes:
- Gender / Sex
- Marital Status
- Religion / Faith
- Date of Birth / Age
- Nationality / Citizenship
- Race / Ethnicity
Evaluation is anchored strictly on verifiable code achievements, technical skills, and work history.

### D. Human-in-the-Loop Governance
The system distinguishes between an **AI Recommendation** and a **Recruiter Decision**. The recruiter can:
- `Approve`: Validate AI recommendation.
- `Reject`: Overturn recommendation.
- `Modify`: Adjust recommendation tier (e.g. from Potential Match to Match) and record explanatory notes.
