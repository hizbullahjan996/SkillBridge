"""API routes for Learning Resources."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.learning_resource import (
    LearningResourceListResponse,
    LearningResourceResponse,
    RecommendedResourcesResponse,
    RecommendedResourceItem,
    ResourceSkillResponse,
    StudentLearningResourceResponse,
    StudentLearningResourceUpdate,
    LearningProgressSummary,
)
from app.services import learning_resource_service as resource_svc
from app.services import skill_gap_service
from app.services import learning_roadmap_service

router = APIRouter(tags=["Learning Resources"])


@router.get("/learning-resources", response_model=LearningResourceListResponse)
def list_learning_resources(
    db: Annotated[Session, Depends(get_db)],
    skill: str | None = None,
    resource_type: str | None = None,
    difficulty: str | None = None,
    is_free: bool | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> LearningResourceListResponse:
    result = resource_svc.search_resources(
        db,
        skill_name=skill,
        resource_type=resource_type,
        difficulty=difficulty,
        is_free=is_free,
        search=search,
        page=page,
        page_size=page_size,
    )

    items = []
    for r in result.items:
        items.append(LearningResourceResponse(
            id=r.resource_id,
            title=r.title,
            provider=r.provider,
            description=r.description,
            url=r.url,
            resource_type=r.resource_type,
            difficulty=r.difficulty,
            is_free=r.is_free,
            skills=[ResourceSkillResponse(**s) for s in r.skills],
            created_at=r.created_at,
            updated_at=r.updated_at,
        ))

    return LearningResourceListResponse(
        items=items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/learning-resources/recommended", response_model=RecommendedResourcesResponse)
def get_recommended_resources(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> RecommendedResourcesResponse:
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    roadmap = learning_roadmap_service.get_default_roadmap(db, current_user.id)
    if not roadmap:
        return RecommendedResourcesResponse(resources=[], total=0, career_name="")

    missing_skills = []
    for item in roadmap.roadmap:
        missing_skills.append({
            "skill_id": item.skill_id,
            "skill_name": item.skill,
            "priority": item.priority,
            "priority_score": item.priority_score,
        })

    recommended = resource_svc.get_recommended_resources(
        db, current_user.student_profile.id, missing_skills
    )

    items = []
    for r in recommended[:20]:
        res = r["resource"]
        items.append(RecommendedResourceItem(
            resource=LearningResourceResponse(
                id=res.resource_id,
                title=res.title,
                provider=res.provider,
                description=res.description,
                url=res.url,
                resource_type=res.resource_type,
                difficulty=res.difficulty,
                is_free=res.is_free,
                skills=[ResourceSkillResponse(**s) for s in res.skills],
                created_at=res.created_at,
                updated_at=res.updated_at,
            ),
            relevance_score=r["relevance_score"],
            matched_skill=r["matched_skill"],
            skill_priority=r["skill_priority"],
        ))

    return RecommendedResourcesResponse(
        resources=items,
        total=len(items),
        career_name=roadmap.career_name,
    )


@router.get("/learning-resources/{resource_id}", response_model=LearningResourceResponse)
def get_learning_resource(
    resource_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> LearningResourceResponse:
    result = resource_svc.get_resource_by_id(db, resource_id)
    if not result:
        raise HTTPException(status_code=404, detail="Resource not found")

    return LearningResourceResponse(
        id=result.resource_id,
        title=result.title,
        provider=result.provider,
        description=result.description,
        url=result.url,
        resource_type=result.resource_type,
        difficulty=result.difficulty,
        is_free=result.is_free,
        skills=[ResourceSkillResponse(**s) for s in result.skills],
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.get("/learning-progress")
def get_learning_progress(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    records = resource_svc.get_student_progress(db, current_user.student_profile.id)
    summary = resource_svc.get_progress_summary(db, current_user.student_profile.id)
    return {"records": records, "summary": summary}


@router.post("/learning-progress", response_model=StudentLearningResourceResponse)
def create_learning_progress(
    resource_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    resource = resource_svc.get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    record = resource_svc.upsert_student_resource_progress(
        db, current_user.student_profile.id, resource_id, "not_started"
    )

    return StudentLearningResourceResponse(
        id=record.id,
        resource_id=record.resource_id,
        status=record.status,
        started_at=record.started_at,
        completed_at=record.completed_at,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.put("/learning-progress/{resource_id}", response_model=StudentLearningResourceResponse)
def update_learning_progress(
    resource_id: int,
    body: StudentLearningResourceUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    resource = resource_svc.get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    record = resource_svc.upsert_student_resource_progress(
        db, current_user.student_profile.id, resource_id, body.status
    )

    return StudentLearningResourceResponse(
        id=record.id,
        resource_id=record.resource_id,
        status=record.status,
        started_at=record.started_at,
        completed_at=record.completed_at,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )
