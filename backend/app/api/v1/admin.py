"""Admin API routes.

All endpoints require admin role. Authorization is enforced via require_role().
"""
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.learning_resource import LearningResourceCreate, LearningResourceResponse, ResourceSkillResponse
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])

admin_only = Depends(require_role(UserRole.admin))


@router.get("/dashboard")
def dashboard(
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
):
    stats = admin_service.get_dashboard_stats(db)
    return {
        "users": stats.users,
        "students": stats.students,
        "jobs": stats.jobs,
        "skills": stats.skills,
        "learning_resources": stats.learning_resources,
        "career_recommendations": stats.career_recommendations,
        "ai_conversations": stats.ai_conversations,
        "learning_progress_records": stats.learning_progress_records,
    }


@router.get("/users")
def list_users(
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
    search: str | None = None,
    role: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    result = admin_service.list_users(db, search=search, role=role, status=status, page=page, page_size=page_size)
    return {
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at,
                "has_profile": u.has_profile,
            }
            for u in result.items
        ],
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
        "pages": result.pages,
    }


@router.get("/users/{user_id}")
def get_user(
    user_id: int,
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
):
    result = admin_service.get_user_detail(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.get("/students")
def list_students(
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    result = admin_service.list_students(db, search=search, page=page, page_size=page_size)
    return {
        "items": [
            {
                "id": s.id,
                "user_id": s.user_id,
                "email": s.email,
                "full_name": s.full_name,
                "major": s.major,
                "university_year": s.university_year,
                "skills_count": s.skills_count,
                "recommendations_count": s.recommendations_count,
            }
            for s in result.items
        ],
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
        "pages": result.pages,
    }


@router.get("/students/{student_id}")
def get_student(
    student_id: int,
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
):
    result = admin_service.get_student_detail(db, student_id)
    if not result:
        raise HTTPException(status_code=404, detail="Student not found")
    return result


@router.get("/skills")
def list_skills(
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    result = admin_service.list_skills_analytics(db, search=search, page=page, page_size=page_size)
    return {
        "items": [
            {
                "skill_id": s.skill_id,
                "skill_name": s.skill_name,
                "category": s.category,
                "student_count": s.student_count,
                "job_count": s.job_count,
            }
            for s in result.items
        ],
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
        "pages": result.pages,
    }


@router.get("/careers")
def list_careers(
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
):
    items = admin_service.list_careers_analytics(db)
    return [
        {
            "career_id": c.career_id,
            "career_name": c.career_name,
            "recommendation_count": c.recommendation_count,
            "job_count": c.job_count,
            "skill_count": c.skill_count,
        }
        for c in items
    ]


@router.get("/jobs/analytics")
def job_analytics(
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
):
    analytics = admin_service.get_job_analytics(db)
    return {
        "total_jobs": analytics.total_jobs,
        "top_cities": analytics.top_cities,
        "top_sectors": analytics.top_sectors,
        "top_skills": analytics.top_skills,
    }


@router.get("/resources")
def list_resources(
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
    search: str | None = None,
    resource_type: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    from app.services import learning_resource_service as resource_svc
    result = resource_svc.search_resources(db, search=search, resource_type=resource_type, page=page, page_size=page_size)
    return {
        "items": [
            {
                "id": r.resource_id,
                "title": r.title,
                "provider": r.provider,
                "resource_type": r.resource_type,
                "difficulty": r.difficulty,
                "is_free": r.is_free,
                "skills": r.skills,
            }
            for r in result.items
        ],
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
        "pages": result.pages,
    }


@router.get("/learning/analytics")
def learning_analytics(
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
):
    analytics = admin_service.get_learning_analytics(db)
    return {
        "total_resources": analytics.total_resources,
        "total_progress_records": analytics.total_progress_records,
        "started": analytics.started,
        "completed": analytics.completed,
        "completion_rate": analytics.completion_rate,
        "most_popular_resources": analytics.most_popular_resources,
        "most_studied_skills": analytics.most_studied_skills,
    }


@router.get("/ai/analytics")
def ai_analytics(
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
):
    analytics = admin_service.get_ai_analytics(db)
    return {
        "total_conversations": analytics.total_conversations,
        "total_messages": analytics.total_messages,
        "active_users": analytics.active_users,
        "avg_messages_per_conversation": analytics.avg_messages_per_conversation,
    }


@router.get("/system/health")
def system_health(
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
):
    health = admin_service.get_system_health(db)
    return {
        "api_status": health.api_status,
        "database_status": health.database_status,
        "ml_model_status": health.ml_model_status,
        "llm_provider_status": health.llm_provider_status,
    }


@router.get("/audit-logs")
def list_audit_logs(
    current_user: Annotated[User, admin_only],
    db: Annotated[Session, Depends(get_db)],
    action: str | None = None,
    resource_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    result = admin_service.list_audit_logs(
        db,
        action=action,
        admin_user_id=current_user.id,
        resource_type=resource_type,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return result
