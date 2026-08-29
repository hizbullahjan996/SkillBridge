"""Skill Gap Analysis Service.

Computes the difference between a student's skills and the skills required
for a specific career or job. Uses actual database data.

Priority scoring formula:
  priority_score = (demand_weight * 40) + (relevance_weight * 35) + (importance_weight * 25)

  Where each weight is normalized 0-1:
    demand_weight = demand_count / max_demand_count
    relevance_weight = demand_count / max_demand_count (same as demand for career)
    importance_weight = avg_importance / 10

  Final score normalized to 0-100.

Priority thresholds:
    High:   priority_score >= 70
    Medium: priority_score >= 40
    Low:    priority_score < 40
"""
import logging
from dataclasses import dataclass, field

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.career_job_mapping import CareerJobMapping
from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.skill import Skill
from app.models.student_skill import StudentSkill

logger = logging.getLogger("skillbridge")

WEIGHT_DEMAND = 0.40
WEIGHT_CAREER_RELEVANCE = 0.35
WEIGHT_IMPORTANCE = 0.25

PRIORITY_HIGH_THRESHOLD = 70
PRIORITY_MEDIUM_THRESHOLD = 40


@dataclass
class SkillGapItemResult:
    skill_id: int
    skill_name: str
    normalized_name: str
    category: str
    priority_score: float
    priority: str
    demand_count: int
    career_relevance_count: int
    avg_importance: float


@dataclass
class SkillGapResult:
    matched_skills: list[dict] = field(default_factory=list)
    missing_skills: list[SkillGapItemResult] = field(default_factory=list)
    match_percentage: float = 0.0
    total_required: int = 0
    matched_count: int = 0
    missing_count: int = 0


def get_student_skill_ids(db: Session, student_id: int) -> set[int]:
    rows = (
        db.query(StudentSkill.skill_id)
        .filter(StudentSkill.student_id == student_id)
        .all()
    )
    return {row[0] for row in rows}


def get_career_required_skills(db: Session, career_id: int) -> dict[int, dict]:
    skill_data: dict[int, dict] = {}

    career_skill_rows = (
        db.query(JobSkill)
        .join(Job, Job.id == JobSkill.job_id)
        .join(CareerJobMapping, CareerJobMapping.job_title_clean == Job.job_title_clean)
        .filter(CareerJobMapping.career_id == career_id)
        .all()
    )

    for js in career_skill_rows:
        skill = js.skill
        if skill.id not in skill_data:
            skill_data[skill.id] = {
                "skill_id": skill.id,
                "skill_name": skill.name,
                "normalized_name": skill.normalized_name,
                "category": skill.category.value,
                "importances": [],
                "demand_count": 0,
            }
        skill_data[skill.id]["demand_count"] += 1
        if js.importance is not None:
            skill_data[skill.id]["importances"].append(js.importance)

    for sid in skill_data:
        imps = skill_data[sid]["importances"]
        skill_data[sid]["avg_importance"] = sum(imps) / len(imps) if imps else 0.0
        del skill_data[sid]["importances"]

    return skill_data


def get_job_required_skills(db: Session, job_id: int) -> dict[int, dict]:
    skill_data: dict[int, dict] = {}
    job_skill_rows = db.query(JobSkill).filter(JobSkill.job_id == job_id).all()

    for js in job_skill_rows:
        skill = js.skill
        skill_data[skill.id] = {
            "skill_id": skill.id,
            "skill_name": skill.name,
            "normalized_name": skill.normalized_name,
            "category": skill.category.value,
            "avg_importance": float(js.importance) if js.importance else 5.0,
            "demand_count": 1,
        }

    return skill_data


def compute_demand_stats(db: Session, career_id: int) -> dict[int, int]:
    job_titles_rows = (
        db.query(CareerJobMapping.job_title_clean)
        .filter(CareerJobMapping.career_id == career_id)
        .all()
    )
    job_titles = [row[0] for row in job_titles_rows]

    if not job_titles:
        return {}

    rows = (
        db.query(JobSkill.skill_id, func.count(JobSkill.job_id).label("cnt"))
        .join(Job, Job.id == JobSkill.job_id)
        .filter(Job.job_title_clean.in_(job_titles))
        .group_by(JobSkill.skill_id)
        .all()
    )

    return {row[0]: row[1] for row in rows}


def classify_priority(score: float) -> str:
    if score >= PRIORITY_HIGH_THRESHOLD:
        return "High"
    elif score >= PRIORITY_MEDIUM_THRESHOLD:
        return "Medium"
    return "Low"


def compute_priority_scores(
    missing_skills: dict[int, dict],
    demand_stats: dict[int, int],
) -> list[SkillGapItemResult]:
    if not missing_skills:
        return []

    max_demand = max(demand_stats.values()) if demand_stats else 1

    results = []
    for skill_id, info in missing_skills.items():
        demand = demand_stats.get(skill_id, 0)
        importance = info.get("avg_importance", 5.0)

        demand_weight = demand / max_demand if max_demand > 0 else 0
        relevance_weight = demand_weight
        importance_weight = importance / 10.0

        raw = (
            demand_weight * WEIGHT_DEMAND
            + relevance_weight * WEIGHT_CAREER_RELEVANCE
            + importance_weight * WEIGHT_IMPORTANCE
        ) * 100
        score = round(min(100.0, max(0.0, raw)), 1)

        results.append(SkillGapItemResult(
            skill_id=skill_id,
            skill_name=info["skill_name"],
            normalized_name=info["normalized_name"],
            category=info["category"],
            priority_score=score,
            priority=classify_priority(score),
            demand_count=demand,
            career_relevance_count=demand,
            avg_importance=info.get("avg_importance", 0.0),
        ))

    results.sort(key=lambda x: x.priority_score, reverse=True)
    return results


def compute_skill_gap(
    db: Session,
    student_id: int,
    required_skills: dict[int, dict],
    demand_stats: dict[int, int] | None = None,
) -> SkillGapResult:
    student_skill_ids = get_student_skill_ids(db, student_id)

    matched = []
    missing: dict[int, dict] = {}

    for skill_id, info in required_skills.items():
        if skill_id in student_skill_ids:
            matched.append({
                "id": skill_id,
                "name": info["skill_name"],
                "normalized_name": info["normalized_name"],
                "category": info["category"],
            })
        else:
            missing[skill_id] = info

    total = len(required_skills)
    matched_count = len(matched)
    missing_count = len(missing)
    match_pct = round((matched_count / total * 100) if total > 0 else 0.0, 1)

    if demand_stats is None:
        demand_stats = {}

    missing_items = compute_priority_scores(missing, demand_stats)

    return SkillGapResult(
        matched_skills=matched,
        missing_skills=missing_items,
        match_percentage=match_pct,
        total_required=total,
        matched_count=matched_count,
        missing_count=missing_count,
    )


def get_career_skill_gap(db: Session, student_id: int, career_id: int) -> SkillGapResult:
    required_skills = get_career_required_skills(db, career_id)
    demand_stats = compute_demand_stats(db, career_id)
    return compute_skill_gap(db, student_id, required_skills, demand_stats)


def get_job_skill_gap(db: Session, student_id: int, job_id: int) -> SkillGapResult:
    required_skills = get_job_required_skills(db, job_id)
    return compute_skill_gap(db, student_id, required_skills)
