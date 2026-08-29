"""API routes for Skill Gap Analysis and Learning Roadmap."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.career import Career
from app.models.job import Job
from app.models.user import User
from app.schemas.skill_gap import (
    CareerSkillGapResponse,
    JobSkillGapResponse,
    LearningRoadmapResponse,
    NoRoadmapResponse,
    SkillGapMatchedSkill,
    SkillGapMissingSkill,
    SkillGapSummary,
)
from app.schemas.skill_gap import RoadmapItemResponse
from app.services.learning_roadmap_service import (
    get_career_roadmap,
    get_default_roadmap,
    get_job_roadmap,
    get_roadmap_with_resources,
)
from app.services.skill_gap_service import get_career_skill_gap, get_job_skill_gap

router = APIRouter(tags=["Skill Gaps"])


@router.get("/skill-gaps/career/{career_id}", response_model=CareerSkillGapResponse)
def career_skill_gap(
    career_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CareerSkillGapResponse:
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")

    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    gap = get_career_skill_gap(db, current_user.student_profile.id, career_id)

    return CareerSkillGapResponse(
        career={"id": career.id, "name": career.name},
        skill_gap=SkillGapSummary(
            matched_count=gap.matched_count,
            missing_count=gap.missing_count,
            match_percentage=gap.match_percentage,
            total_required=gap.total_required,
        ),
        matched_skills=[
            SkillGapMatchedSkill(**m) for m in gap.matched_skills
        ],
        missing_skills=[
            SkillGapMissingSkill(
                skill_id=s.skill_id,
                skill_name=s.skill_name,
                normalized_name=s.normalized_name,
                category=s.category,
                priority_score=s.priority_score,
                priority=s.priority,
                demand_count=s.demand_count,
                career_relevance_count=s.career_relevance_count,
                avg_importance=s.avg_importance,
            )
            for s in gap.missing_skills
        ],
    )


@router.get("/skill-gaps/job/{job_id}", response_model=JobSkillGapResponse)
def job_skill_gap(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> JobSkillGapResponse:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    gap = get_job_skill_gap(db, current_user.student_profile.id, job_id)

    return JobSkillGapResponse(
        job={"id": job.id, "title": job.job_title, "company": job.company},
        skill_gap=SkillGapSummary(
            matched_count=gap.matched_count,
            missing_count=gap.missing_count,
            match_percentage=gap.match_percentage,
            total_required=gap.total_required,
        ),
        matched_skills=[
            SkillGapMatchedSkill(**m) for m in gap.matched_skills
        ],
        missing_skills=[
            SkillGapMissingSkill(
                skill_id=s.skill_id,
                skill_name=s.skill_name,
                normalized_name=s.normalized_name,
                category=s.category,
                priority_score=s.priority_score,
                priority=s.priority,
                demand_count=s.demand_count,
                career_relevance_count=s.career_relevance_count,
                avg_importance=s.avg_importance,
            )
            for s in gap.missing_skills
        ],
    )


@router.get("/learning-roadmap")
def learning_roadmap_default(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> LearningRoadmapResponse | NoRoadmapResponse:
    roadmap = get_default_roadmap(db, current_user.id)
    if not roadmap:
        return NoRoadmapResponse(
            message="No career recommendations found",
            detail="Please complete your profile and generate career recommendations first.",
        )

    return LearningRoadmapResponse(
        career_name=roadmap.career_name,
        total_missing=roadmap.total_missing,
        roadmap=[
            RoadmapItemResponse(
                step=item.step,
                skill=item.skill,
                skill_id=item.skill_id,
                reason=item.reason,
                priority_score=item.priority_score,
                priority=item.priority,
                demand_count=item.demand_count,
                category=item.category,
            )
            for item in roadmap.roadmap
        ],
    )


@router.get("/learning-roadmap/career/{career_id}")
def learning_roadmap_career(
    career_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> LearningRoadmapResponse:
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")

    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    roadmap = get_career_roadmap(db, current_user.student_profile.id, career_id)

    return LearningRoadmapResponse(
        career_name=roadmap.career_name,
        total_missing=roadmap.total_missing,
        roadmap=[
            RoadmapItemResponse(
                step=item.step,
                skill=item.skill,
                skill_id=item.skill_id,
                reason=item.reason,
                priority_score=item.priority_score,
                priority=item.priority,
                demand_count=item.demand_count,
                category=item.category,
            )
            for item in roadmap.roadmap
        ],
    )


@router.get("/learning-roadmap/job/{job_id}")
def learning_roadmap_job(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> LearningRoadmapResponse:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    roadmap = get_job_roadmap(db, current_user.student_profile.id, job_id)

    return LearningRoadmapResponse(
        career_name=roadmap.career_name,
        total_missing=roadmap.total_missing,
        roadmap=[
            RoadmapItemResponse(
                step=item.step,
                skill=item.skill,
                skill_id=item.skill_id,
                reason=item.reason,
                priority_score=item.priority_score,
                priority=item.priority,
                demand_count=item.demand_count,
                category=item.category,
            )
            for item in roadmap.roadmap
        ],
    )


@router.get("/learning-roadmap/with-resources")
def learning_roadmap_with_resources(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    result = get_roadmap_with_resources(db, current_user.id)
    if not result:
        return NoRoadmapResponse(
            message="No career recommendations found",
            detail="Please complete your profile and generate career recommendations first.",
        )

    return result
