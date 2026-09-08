"""Benchmark Runner evaluating system against ground truth dataset."""
import time
import logging
from typing import Optional
from app.evaluation.test_dataset import BENCHMARK_JOBS, BENCHMARK_CANDIDATES
from app.tools.job_analyzer import extract_job_requirements
from app.tools.resume_parser import parse_resume
from app.tools.skill_extractor import extract_candidate_skills, normalize_skill_name
from app.tools.candidate_matcher import match_candidate_to_job
from app.tools.skill_gap_analyzer import identify_skill_gaps
from app.tools.score_calculator import calculate_candidate_score
from app.tools.interview_generator import generate_interview_questions
from app.tools.report_generator import generate_candidate_report
from app.tools.report_validator import validate_candidate_report

logger = logging.getLogger(__name__)

# In-memory storage for benchmark execution results
_LAST_BENCHMARK_RESULTS: Optional[dict] = None


def run_evaluation_benchmark() -> dict:
    """Run evaluation benchmark across curated dataset and compute real quality metrics."""
    global _LAST_BENCHMARK_RESULTS

    total_candidates = len(BENCHMARK_CANDIDATES)
    valid_structured_outputs = 0
    total_expected_skills = 0
    correctly_extracted_skills = 0
    recommendation_matches = 0
    successful_tool_executions = 0
    total_tool_executions = 0
    completed_evaluations = 0

    eval_details = []
    start_time = time.time()

    jobs_by_id = {j["id"]: j for j in BENCHMARK_JOBS}

    for cand_data in BENCHMARK_CANDIDATES:
        job_data = jobs_by_id.get(cand_data["job_id"], BENCHMARK_JOBS[0])
        try:
            # Tool 1: Job requirements
            total_tool_executions += 1
            job_reqs = extract_job_requirements(job_data["description"])
            successful_tool_executions += 1
            if job_reqs and job_reqs.job_title:
                valid_structured_outputs += 1

            # Tool 2: Resume parsing
            total_tool_executions += 1
            cand_profile = parse_resume(cand_data["resume_text"])
            successful_tool_executions += 1
            if cand_profile and cand_profile.name:
                valid_structured_outputs += 1

            # Tool 3: Skill extraction & normalization
            total_tool_executions += 1
            extracted_skills = extract_candidate_skills(cand_profile, cand_data["resume_text"])
            successful_tool_executions += 1

            # Measure skill extraction accuracy
            norm_extracted = {s.lower() for s in extracted_skills}
            expected_set = {normalize_skill_name(s).lower() for s in cand_data["expected_skills"]}
            total_expected_skills += len(expected_set)
            matches = sum(1 for s in expected_set if s in norm_extracted)
            correctly_extracted_skills += matches

            # Tool 4: Matching
            total_tool_executions += 1
            match_res = match_candidate_to_job(job_reqs, cand_profile, extracted_skills, cand_data["resume_text"])
            successful_tool_executions += 1

            # Tool 5: Gaps
            total_tool_executions += 1
            gap_res = identify_skill_gaps(job_reqs, match_res)
            successful_tool_executions += 1

            # Tool 6: Score
            total_tool_executions += 1
            score_res = calculate_candidate_score(job_reqs, cand_profile, match_res)
            successful_tool_executions += 1

            # Tool 7: Interview
            total_tool_executions += 1
            interview_res = generate_interview_questions(job_reqs, cand_profile, match_res, gap_res)
            successful_tool_executions += 1

            # Tool 8: Report
            total_tool_executions += 1
            report_res = generate_candidate_report(job_reqs, cand_profile, match_res, gap_res, score_res, interview_res)
            successful_tool_executions += 1

            # Tool 9: Validator
            total_tool_executions += 1
            valid_res = validate_candidate_report(report_res, job_reqs, cand_profile)
            successful_tool_executions += 1

            if valid_res.is_valid:
                valid_structured_outputs += 1

            # Check recommendation consistency against ground truth expectation
            expected_rec = cand_data.get("expected_recommendation")
            if score_res.recommendation == expected_rec:
                recommendation_matches += 1

            completed_evaluations += 1
            eval_details.append({
                "candidate_name": cand_data["name"],
                "target_job": job_data["title"],
                "calculated_score": score_res.overall_score,
                "recommendation": score_res.recommendation,
                "expected_recommendation": expected_rec,
                "matching_skills_count": len(match_res.matching_skills),
                "skill_gaps_count": len(gap_res.gaps),
                "status": "SUCCESS"
            })

        except Exception as e:
            logger.error("Benchmark error for %s: %s", cand_data['name'], e)
            eval_details.append({
                "candidate_name": cand_data["name"],
                "target_job": job_data["title"],
                "status": "FAILED",
                "error": str(e)
            })

    duration = round(time.time() - start_time, 2)

    # Compute percentages
    structured_validity = round((valid_structured_outputs / max(total_candidates * 3, 1)) * 100, 1)
    skill_accuracy = round((correctly_extracted_skills / max(total_expected_skills, 1)) * 100, 1)
    rec_consistency = round((recommendation_matches / max(total_candidates, 1)) * 100, 1)
    tool_success_rate = round((successful_tool_executions / max(total_tool_executions, 1)) * 100, 1)
    completion_rate = round((completed_evaluations / max(total_candidates, 1)) * 100, 1)

    _LAST_BENCHMARK_RESULTS = {
        "status": "COMPLETED",
        "evaluated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "duration_seconds": duration,
        "sample_size": {
            "jobs": len(BENCHMARK_JOBS),
            "candidates": total_candidates,
            "tool_calls": total_tool_executions
        },
        "metrics": {
            "structured_output_validity": f"{structured_validity}%",
            "skill_extraction_accuracy": f"{skill_accuracy}%",
            "recommendation_consistency": f"{rec_consistency}%",
            "tool_execution_success": f"{tool_success_rate}%",
            "agent_completion_rate": f"{completion_rate}%"
        },
        "raw_scores": {
            "structured_output_validity": structured_validity,
            "skill_extraction_accuracy": skill_accuracy,
            "recommendation_consistency": rec_consistency,
            "tool_execution_success": tool_success_rate,
            "agent_completion_rate": completion_rate
        },
        "details": eval_details
    }
    return _LAST_BENCHMARK_RESULTS


def get_latest_benchmark_metrics() -> Optional[dict]:
    """Return the cached benchmark results or None if not evaluated yet."""
    return _LAST_BENCHMARK_RESULTS
