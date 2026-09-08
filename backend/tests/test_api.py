"""Integration tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["app"] == "AI Recruitment Agent"


def test_list_tools():
    response = client.get("/api/tools")
    assert response.status_code == 200
    tools = response.json()
    assert len(tools) >= 9
    tool_names = [t["name"] for t in tools]
    assert "extract_job_requirements" in tool_names
    assert "parse_resume" in tool_names
    assert "calculate_candidate_score" in tool_names


def test_create_and_list_job():
    payload = {
        "title": "FastAPI Backend Developer",
        "description": "Looking for a Python and FastAPI engineer with SQL experience. Docker is a plus.",
        "experience_required": 2.0
    }
    create_resp = client.post("/api/jobs", json=payload)
    assert create_resp.status_code == 201
    job = create_resp.json()
    assert job["title"] == "FastAPI Backend Developer"
    assert len(job["required_skills"]) > 0

    list_resp = client.get("/api/jobs")
    assert list_resp.status_code == 200
    jobs = list_resp.json()
    assert any(j["id"] == job["id"] for j in jobs)


def test_agent_status():
    response = client.get("/api/agent/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"
    assert len(data["registered_tools"]) >= 9


def test_demo_stats():
    response = client.get("/api/demo/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_jobs" in stats
    assert "distribution" in stats
