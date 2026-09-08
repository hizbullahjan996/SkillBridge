"""API routes for job search and recommendations."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.skill import Skill
from app.models.user import User
from app.schemas.job import (
    JobDetailResponse,
    JobListItem,
    JobListResponse,
    JobSkillResponse,
)
from app.schemas.recommendation import CareerRecommendationResponse
from app.services.job_matching_service import get_recommended_jobs

router = APIRouter(tags=["Jobs"])


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    db: Annotated[Session, Depends(get_db)],
    city: str | None = None,
    sector: str | None = None,
    job_type: str | None = None,
    education_level: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> JobListResponse:
    query = db.query(Job)

    if city:
        query = query.filter(Job.city.ilike(f"%{city}%"))
    if sector:
        query = query.filter(Job.sector.ilike(f"%{sector}%"))
    if job_type:
        query = query.filter(Job.job_type.ilike(f"%{job_type}%"))
    if education_level:
        query = query.filter(Job.education_level.ilike(f"%{education_level}%"))
    if search:
        query = query.filter(
            Job.job_title.ilike(f"%{search}%") | Job.company.ilike(f"%{search}%")
        )

    total = query.count()
    jobs = query.offset((page - 1) * page_size).limit(page_size).all()
    pages = (total + page_size - 1) // page_size

    items = []
    for job in jobs:
        items.append(JobListItem(
            job_id=job.id,
            job_title=job.job_title,
            company=job.company,
            city=job.city,
            sector=job.sector,
            job_type=job.job_type,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            salary_average=job.salary_average,
            education_level=job.education_level,
            experience_required=job.experience_required_raw,
        ))

    return JobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/jobs/analytics")
def job_analytics(db: Annotated[Session, Depends(get_db)]):
    total = db.query(func.count(Job.id)).scalar() or 0

    cities = (
        db.query(Job.city, func.count(Job.id).label("cnt"))
        .group_by(Job.city)
        .order_by(func.count(Job.id).desc())
        .limit(10)
        .all()
    )

    sectors = (
        db.query(Job.sector, func.count(Job.id).label("cnt"))
        .group_by(Job.sector)
        .order_by(func.count(Job.id).desc())
        .limit(10)
        .all()
    )

    skills = (
        db.query(Skill.name, func.count(JobSkill.id).label("cnt"))
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .group_by(Skill.name)
        .order_by(func.count(JobSkill.id).desc())
        .limit(10)
        .all()
    )

    return {
        "total_jobs": total,
        "top_cities": [{"name": c, "count": n} for c, n in cities],
        "top_sectors": [{"name": s, "count": n} for s, n in sectors],
        "top_skills": [{"name": s, "count": n} for s, n in skills],
    }


@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
def get_job(
    job_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> JobDetailResponse:
    from fastapi import HTTPException
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    skill_rows = (
        db.query(JobSkill)
        .filter(JobSkill.job_id == job.id)
        .all()
    )
    skills = []
    for js in skill_rows:
        if js.skill:
            skills.append(JobSkillResponse(
                skill_name=js.skill.name,
                normalized_name=js.skill.normalized_name,
            ))

    return JobDetailResponse(
        id=job.id,
        job_title=job.job_title,
        job_title_clean=job.job_title_clean,
        company=job.company,
        city=job.city,
        sector=job.sector,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_average=job.salary_average,
        experience_min_years=job.experience_min_years,
        experience_max_years=job.experience_max_years,
        experience_required_raw=job.experience_required_raw,
        education_level=job.education_level,
        job_type=job.job_type,
        gender_preference=job.gender_preference,
        number_of_vacancies=job.number_of_vacancies,
        posted_date=job.posted_date,
        application_deadline=job.application_deadline,
        required_skills=skills,
    )


@router.get("/recommendations/jobs", response_model=JobListResponse)
def recommended_jobs(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    city: str | None = None,
    sector: str | None = None,
    job_type: str | None = None,
    min_salary: float | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
) -> JobListResponse:
    result = get_recommended_jobs(
        db,
        current_user.id,
        page=page,
        page_size=page_size,
        city=city,
        sector=sector,
        job_type=job_type,
        min_salary=min_salary,
    )
    return JobListResponse(**result)
