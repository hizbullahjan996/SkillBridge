"""Learning Resource Service.

Provides resource search, filtering, personalized recommendations,
and roadmap integration. Uses real resource data only.
"""
import logging
import math
from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.learning_resource import LearningResource, LearningResourceSkill
from app.models.skill import Skill
from app.models.student_skill import StudentSkill
from app.models.student_learning_resource import StudentLearningResource, ResourceProgressStatus

logger = logging.getLogger("skillbridge")


@dataclass
class ResourceResult:
    resource_id: int
    title: str
    provider: str
    description: str | None
    url: str | None
    resource_type: str
    difficulty: str | None
    is_free: bool
    skills: list[dict]
    created_at: object
    updated_at: object


@dataclass
class ResourceSearchResult:
    items: list[ResourceResult]
    total: int
    page: int
    page_size: int
    pages: int


def search_resources(
    db: Session,
    skill_name: str | None = None,
    resource_type: str | None = None,
    difficulty: str | None = None,
    is_free: bool | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> ResourceSearchResult:
    query = db.query(LearningResource)

    if skill_name:
        skill_name_lower = skill_name.lower()
        query = query.join(LearningResourceSkill).join(Skill).filter(
            Skill.normalized_name.ilike(f"%{skill_name_lower}%")
        )

    if resource_type:
        query = query.filter(LearningResource.resource_type == resource_type)

    if difficulty:
        query = query.filter(LearningResource.difficulty == difficulty)

    if is_free is not None:
        query = query.filter(LearningResource.is_free == is_free)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            LearningResource.title.ilike(search_pattern)
            | LearningResource.provider.ilike(search_pattern)
            | LearningResource.description.ilike(search_pattern)
        )

    total = query.count()
    pages = math.ceil(total / page_size) if page_size > 0 else 0
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    resource_results = [_resource_to_result(r) for r in items]

    return ResourceSearchResult(
        items=resource_results,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def get_resource_by_id(db: Session, resource_id: int) -> ResourceResult | None:
    resource = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if not resource:
        return None
    return _resource_to_result(resource)


def get_recommended_resources(
    db: Session,
    student_id: int,
    missing_skills: list[dict],
) -> list[dict]:
    if not missing_skills:
        return []

    skill_ids = [s["skill_id"] for s in missing_skills]
    skill_priority_map = {s["skill_id"]: s.get("priority", "Low") for s in missing_skills}
    skill_name_map = {s["skill_id"]: s.get("skill_name", "") for s in missing_skills}

    resources = (
        db.query(LearningResource)
        .join(LearningResourceSkill)
        .filter(LearningResourceSkill.skill_id.in_(skill_ids))
        .distinct()
        .all()
    )

    recommended = []
    for resource in resources:
        resource_skills = (
            db.query(LearningResourceSkill)
            .filter(LearningResourceSkill.resource_id == resource.id)
            .all()
        )

        matched_skill_ids = [rs.skill_id for rs in resource_skills]
        relevant_skill_ids = [sid for sid in matched_skill_ids if sid in skill_ids]

        if not relevant_skill_ids:
            continue

        score = _compute_resource_score(
            resource, relevant_skill_ids, skill_priority_map
        )

        best_skill_id = max(relevant_skill_ids, key=lambda sid: _skill_priority_value(skill_priority_map.get(sid, "Low")))
        matched_skill_name = skill_name_map.get(best_skill_id, "")
        skill_priority = skill_priority_map.get(best_skill_id, "Low")

        recommended.append({
            "resource": _resource_to_result(resource),
            "relevance_score": score,
            "matched_skill": matched_skill_name,
            "skill_priority": skill_priority,
        })

    recommended.sort(key=lambda x: x["relevance_score"], reverse=True)
    return recommended


def _compute_resource_score(
    resource: LearningResource,
    relevant_skill_ids: list[int],
    skill_priority_map: dict[int, str],
) -> float:
    priority_values = [_skill_priority_value(skill_priority_map.get(sid, "Low")) for sid in relevant_skill_ids]
    max_priority = max(priority_values) if priority_values else 0

    score = max_priority * 60
    if resource.is_free:
        score += 20
    if resource.difficulty == "beginner":
        score += 10
    elif resource.difficulty == "intermediate":
        score += 5

    return round(score, 1)


def _skill_priority_value(priority: str) -> float:
    return {"High": 100.0, "Medium": 60.0, "Low": 30.0}.get(priority, 30.0)


def _resource_to_result(resource: LearningResource) -> ResourceResult:
    skills = []
    for rs in resource.resource_skills:
        if rs.skill:
            skills.append({
                "id": rs.skill.id,
                "name": rs.skill.name,
                "normalized_name": rs.skill.normalized_name,
            })

    return ResourceResult(
        resource_id=resource.id,
        title=resource.title,
        provider=resource.provider,
        description=resource.description,
        url=resource.url,
        resource_type=resource.resource_type,
        difficulty=resource.difficulty,
        is_free=resource.is_free,
        skills=skills,
        created_at=resource.created_at,
        updated_at=resource.updated_at,
    )


def get_student_progress(db: Session, student_id: int) -> list[dict]:
    records = (
        db.query(StudentLearningResource)
        .filter(StudentLearningResource.student_id == student_id)
        .all()
    )
    return [
        {
            "id": r.id,
            "resource_id": r.resource_id,
            "status": r.status,
            "started_at": r.started_at,
            "completed_at": r.completed_at,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in records
    ]


def get_progress_summary(db: Session, student_id: int) -> dict:
    records = (
        db.query(StudentLearningResource.status, func.count(StudentLearningResource.id))
        .filter(StudentLearningResource.student_id == student_id)
        .group_by(StudentLearningResource.status)
        .all()
    )
    counts = {status: count for status, count in records}
    total = sum(counts.values())
    return {
        "total": total,
        "not_started": counts.get(ResourceProgressStatus.not_started, 0),
        "in_progress": counts.get(ResourceProgressStatus.in_progress, 0),
        "completed": counts.get(ResourceProgressStatus.completed, 0),
    }


def upsert_student_resource_progress(
    db: Session,
    student_id: int,
    resource_id: int,
    status: str,
) -> StudentLearningResource | None:
    from datetime import datetime, timezone

    existing = (
        db.query(StudentLearningResource)
        .filter(
            StudentLearningResource.student_id == student_id,
            StudentLearningResource.resource_id == resource_id,
        )
        .first()
    )

    now = datetime.now(timezone.utc)

    if existing:
        existing.status = status
        if status == "in_progress" and existing.started_at is None:
            existing.started_at = now
        elif status == "completed":
            existing.completed_at = now
        existing.updated_at = now
        db.commit()
        db.refresh(existing)
        return existing

    record = StudentLearningResource(
        student_id=student_id,
        resource_id=resource_id,
        status=status,
        started_at=now if status == "in_progress" else None,
        completed_at=now if status == "completed" else None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_resources_for_skills(db: Session, skill_ids: list[int]) -> dict[int, list[ResourceResult]]:
    if not skill_ids:
        return {}

    resource_skills = (
        db.query(LearningResourceSkill)
        .filter(LearningResourceSkill.skill_id.in_(skill_ids))
        .all()
    )

    resource_ids = list({rs.resource_id for rs in resource_skills})
    if not resource_ids:
        return {}

    resources = (
        db.query(LearningResource)
        .filter(LearningResource.id.in_(resource_ids))
        .all()
    )
    resource_map = {r.id: _resource_to_result(r) for r in resources}

    result: dict[int, list[ResourceResult]] = {sid: [] for sid in skill_ids}
    for rs in resource_skills:
        if rs.resource_id in resource_map:
            result[rs.skill_id].append(resource_map[rs.resource_id])

    return result
