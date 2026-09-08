"""Evaluation and Quality Benchmark REST API endpoints."""
import logging
from fastapi import APIRouter
from app.evaluation.benchmark_runner import run_evaluation_benchmark, get_latest_benchmark_metrics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/evaluation", tags=["Evaluation Benchmark"])


@router.get("/metrics")
def get_evaluation_metrics():
    """Retrieve the latest measured AI quality metrics or NOT_EVALUATED if unrun."""
    metrics = get_latest_benchmark_metrics()
    if not metrics:
        return {
            "status": "NOT_EVALUATED",
            "message": "Evaluation benchmark has not been run yet. Trigger POST /api/evaluation/run-benchmark to evaluate against ground truth dataset.",
            "metrics": None
        }
    return metrics


@router.post("/run-benchmark")
def execute_benchmark():
    """Run evaluation benchmark across curated jobs and candidate resumes, returning empirical metrics."""
    logger.info("Starting execution of AI evaluation benchmark suite.")
    results = run_evaluation_benchmark()
    return results
