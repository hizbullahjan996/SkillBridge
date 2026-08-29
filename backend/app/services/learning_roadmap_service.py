"""Personalized Learning Roadmap Service.

Generates a skill learning order based on:
1. Missing skills from skill gap analysis
2. Priority scores (demand + importance)
3. No fake courses or resources

The roadmap is deterministic and based entirely on real data.
"""
import logging
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.career import Career
from app.models.recommendation import CareerRecommendation
from app.models.student import StudentProfile
from app.services.skill_gap_service import (
    SkillGapItemResult,
    SkillGapResult,
    get_career_skill_gap,
    get_job_skill_gap,
)

logger = logging.getLogger("skillbridge")

SKILL_DEPENDENCIES: dict[str, list[str]] = {
    "machine_learning": ["python", "numpy", "pandas"],
    "deep_learning": ["python", "machine_learning"],
    "tensorflow": ["python", "machine_learning"],
    "pytorch": ["python", "machine_learning"],
    "data_analysis": ["python", "sql"],
    "pandas": ["python"],
    "numpy": ["python"],
    "django": ["python"],
    "fastapi": ["python"],
    "scikit-learn": ["python", "numpy", "pandas"],
    "docker": ["linux"],
    "kubernetes": ["docker"],
    "terraform": ["linux"],
    "ansible": ["linux"],
    "ci_cd": ["git", "docker"],
}


@dataclass
class RoadmapItem:
    step: int
    skill: str
    skill_id: int
    reason: str
    priority_score: float
    priority: str
    demand_count: int
    category: str


@dataclass
class LearningRoadmap:
    roadmap: list[RoadmapItem] = field(default_factory=list)
    total_missing: int = 0
    career_name: str = ""


def resolve_dependencies(
    missing_skills: list[SkillGapItemResult],
) -> list[SkillGapItemResult]:
    skill_map = {s.normalized_name: s for s in missing_skills}
    depended_on: set[str] = set()

    for missing in missing_skills:
        deps = SKILL_DEPENDENCIES.get(missing.normalized_name, [])
        for dep in deps:
            if dep in skill_map and dep != missing.normalized_name:
                depended_on.add(dep)

    def sort_key(item: SkillGapItemResult) -> tuple:
        is_dep = 0 if item.normalized_name in depended_on else 1
        return (is_dep, -item.priority_score)

    sorted_skills = sorted(missing_skills, key=sort_key)
    return sorted_skills


def generate_roadmap_from_gap(
    gap: SkillGapResult,
    career_name: str = "",
) -> LearningRoadmap:
    if not gap.missing_skills:
        return LearningRoadmap(
            roadmap=[],
            total_missing=0,
            career_name=career_name,
        )

    ordered = resolve_dependencies(gap.missing_skills)

    roadmap_items = []
    for idx, skill in enumerate(ordered, start=1):
        reason_parts = []
        if skill.demand_count > 0:
            reason_parts.append(f"Required by {skill.demand_count} relevant job(s)")
        if skill.priority == "High":
            reason_parts.append("high demand in target career")
        elif skill.priority == "Medium":
            reason_parts.append("moderate demand in target career")
        else:
            reason_parts.append("appears in relevant job postings")

        reason = "; ".join(reason_parts) if reason_parts else "Missing skill for target career"

        roadmap_items.append(RoadmapItem(
            step=idx,
            skill=skill.skill_name,
            skill_id=skill.skill_id,
            reason=reason,
            priority_score=skill.priority_score,
            priority=skill.priority,
            demand_count=skill.demand_count,
            category=skill.category,
        ))

    return LearningRoadmap(
        roadmap=roadmap_items,
        total_missing=len(roadmap_items),
        career_name=career_name,
    )


def get_career_roadmap(db: Session, student_id: int, career_id: int) -> LearningRoadmap:
    career = db.query(Career).filter(Career.id == career_id).first()
    career_name = career.name if career else ""

    gap = get_career_skill_gap(db, student_id, career_id)
    return generate_roadmap_from_gap(gap, career_name)


def get_job_roadmap(db: Session, student_id: int, job_id: int) -> LearningRoadmap:
    gap = get_job_skill_gap(db, student_id, job_id)
    return generate_roadmap_from_gap(gap, "")


def get_default_roadmap(db: Session, user_id: int) -> LearningRoadmap | None:
    from app.models.user import User

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.student_profile:
        return None

    profile = user.student_profile

    latest_rec = (
        db.query(CareerRecommendation)
        .filter(CareerRecommendation.student_id == profile.id)
        .order_by(CareerRecommendation.rank)
        .first()
    )

    if not latest_rec:
        return None

    return get_career_roadmap(db, profile.id, latest_rec.career_id)


def get_roadmap_with_resources(db: Session, user_id: int) -> dict | None:
    roadmap = get_default_roadmap(db, user_id)
    if not roadmap:
        return None

    from app.services.learning_resource_service import get_resources_for_skills

    skill_ids = [item.skill_id for item in roadmap.roadmap]
    resources_by_skill = get_resources_for_skills(db, skill_ids)

    roadmap_items = []
    for item in roadmap.roadmap:
        item_resources = resources_by_skill.get(item.skill_id, [])
        roadmap_items.append({
            "step": item.step,
            "skill": item.skill,
            "skill_id": item.skill_id,
            "reason": item.reason,
            "priority_score": item.priority_score,
            "priority": item.priority,
            "demand_count": item.demand_count,
            "category": item.category,
            "resources": item_resources,
        })

    return {
        "career_name": roadmap.career_name,
        "total_missing": roadmap.total_missing,
        "roadmap": roadmap_items,
    }
