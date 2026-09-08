"""Admin Service.

Provides dashboard statistics, user/student management, skill/career/job analytics,
learning progress analytics, AI assistant analytics, system health checks,
and audit logging. All statistics come from actual database records.
"""
import json
import logging
import math
import os
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.models.admin_audit_log import AdminAuditLog
from app.models.assistant import AssistantConversation, AssistantMessage
from app.models.career import Career
from app.models.career_skill import CareerSkill
from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.learning_resource import LearningResource, LearningResourceSkill
from app.models.recommendation import CareerRecommendation
from app.models.skill import Skill
from app.models.skill_gap import SkillGapReport, SkillGapItem, GapItemStatus
from app.models.student import StudentProfile
from app.models.student_learning_resource import StudentLearningResource
from app.models.student_skill import StudentSkill
from app.models.user import User, UserRole

logger = logging.getLogger("skillbridge")


@dataclass
class DashboardStats:
    users: int = 0
    students: int = 0
    jobs: int = 0
    skills: int = 0
    learning_resources: int = 0
    career_recommendations: int = 0
    ai_conversations: int = 0
    learning_progress_records: int = 0


def get_dashboard_stats(db: Session) -> DashboardStats:
    return DashboardStats(
        users=db.query(func.count(User.id)).scalar() or 0,
        students=db.query(func.count(StudentProfile.id)).scalar() or 0,
        jobs=db.query(func.count(Job.id)).scalar() or 0,
        skills=db.query(func.count(Skill.id)).scalar() or 0,
        learning_resources=db.query(func.count(LearningResource.id)).scalar() or 0,
        career_recommendations=db.query(func.count(CareerRecommendation.id)).scalar() or 0,
        ai_conversations=db.query(func.count(AssistantConversation.id)).scalar() or 0,
        learning_progress_records=db.query(func.count(StudentLearningResource.id)).scalar() or 0,
    )


@dataclass
class UserListItem:
    id: int
    email: str
    role: str
    is_active: bool
    created_at: object
    has_profile: bool


@dataclass
class UserListResult:
    items: list[UserListItem]
    total: int
    page: int
    page_size: int
    pages: int


def list_users(
    db: Session,
    search: str | None = None,
    role: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> UserListResult:
    query = db.query(User)

    if search:
        pattern = f"%{search}%"
        query = query.filter(User.email.ilike(pattern))

    if role:
        query = query.filter(User.role == role)

    if status == "active":
        query = query.filter(User.is_active == True)
    elif status == "inactive":
        query = query.filter(User.is_active == False)

    total = query.count()
    pages = math.ceil(total / page_size) if page_size > 0 else 0
    users = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for u in users:
        items.append(UserListItem(
            id=u.id,
            email=u.email,
            role=u.role.value,
            is_active=u.is_active,
            created_at=u.created_at,
            has_profile=u.student_profile is not None,
        ))

    return UserListResult(items=items, total=total, page=page, page_size=page_size, pages=pages)


def get_user_detail(db: Session, user_id: int) -> dict | None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    result = {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }

    if user.student_profile:
        p = user.student_profile
        result["student_profile"] = {
            "id": p.id,
            "full_name": p.full_name,
            "major": p.major,
            "cgpa": p.cgpa,
            "university_year": p.university_year,
            "interest_domain": p.interest_domain,
        }
        skills_count = db.query(func.count(StudentSkill.id)).filter(StudentSkill.student_id == p.id).scalar() or 0
        recs_count = db.query(func.count(CareerRecommendation.id)).filter(CareerRecommendation.student_id == p.id).scalar() or 0
        progress_count = db.query(func.count(StudentLearningResource.id)).filter(StudentLearningResource.student_id == p.id).scalar() or 0
        result["student_profile"]["skills_count"] = skills_count
        result["student_profile"]["recommendations_count"] = recs_count
        result["student_profile"]["learning_progress_count"] = progress_count
    else:
        result["student_profile"] = None

    return result


@dataclass
class StudentListItem:
    id: int
    user_id: int
    email: str
    full_name: str
    major: str | None
    university_year: str | None
    skills_count: int
    recommendations_count: int


@dataclass
class StudentListResult:
    items: list[StudentListItem]
    total: int
    page: int
    page_size: int
    pages: int


def list_students(
    db: Session,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> StudentListResult:
    query = (
        db.query(StudentProfile, User)
        .join(User, User.id == StudentProfile.user_id)
    )

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            StudentProfile.full_name.ilike(pattern) | User.email.ilike(pattern)
        )

    total = query.count()
    pages = math.ceil(total / page_size) if page_size > 0 else 0
    results = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for profile, user in results:
        skills_count = db.query(func.count(StudentSkill.id)).filter(StudentSkill.student_id == profile.id).scalar() or 0
        recs_count = db.query(func.count(CareerRecommendation.id)).filter(CareerRecommendation.student_id == profile.id).scalar() or 0
        items.append(StudentListItem(
            id=profile.id,
            user_id=user.id,
            email=user.email,
            full_name=profile.full_name,
            major=profile.major,
            university_year=profile.university_year,
            skills_count=skills_count,
            recommendations_count=recs_count,
        ))

    return StudentListResult(items=items, total=total, page=page, page_size=page_size, pages=pages)


def get_student_detail(db: Session, student_id: int) -> dict | None:
    profile = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not profile:
        return None

    user = db.query(User).filter(User.id == profile.user_id).first()

    student_skills = (
        db.query(StudentSkill)
        .filter(StudentSkill.student_id == student_id)
        .all()
    )
    skills = []
    for ss in student_skills:
        skill = db.query(Skill).filter(Skill.id == ss.skill_id).first()
        if skill:
            skills.append({"id": skill.id, "name": skill.name, "proficiency": ss.proficiency})

    recs = (
        db.query(CareerRecommendation)
        .filter(CareerRecommendation.student_id == student_id)
        .order_by(CareerRecommendation.rank)
        .all()
    )
    recommendations = []
    for r in recs:
        career = db.query(Career).filter(Career.id == r.career_id).first()
        if career:
            recommendations.append({"career_name": career.name, "rank": r.rank, "probability": round(r.probability * 100, 1)})

    gap_reports = (
        db.query(SkillGapReport)
        .filter(SkillGapReport.student_id == student_id)
        .order_by(SkillGapReport.created_at.desc())
        .limit(5)
        .all()
    )
    skill_gaps = [{"career_id": g.career_id, "match_percentage": g.match_percentage, "created_at": g.created_at} for g in gap_reports]

    progress = (
        db.query(StudentLearningResource)
        .filter(StudentLearningResource.student_id == student_id)
        .all()
    )
    learning_progress = [{"resource_id": p.resource_id, "status": p.status} for p in progress]

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "email": user.email if user else None,
        "full_name": profile.full_name,
        "major": profile.major,
        "cgpa": profile.cgpa,
        "university_year": profile.university_year,
        "interest_domain": profile.interest_domain,
        "skills": skills,
        "recommendations": recommendations,
        "skill_gaps": skill_gaps,
        "learning_progress": learning_progress,
    }


@dataclass
class SkillAnalyticsItem:
    skill_id: int
    skill_name: str
    category: str
    student_count: int
    job_count: int


@dataclass
class SkillAnalyticsResult:
    items: list[SkillAnalyticsItem]
    total: int
    page: int
    page_size: int
    pages: int


def list_skills_analytics(
    db: Session,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> SkillAnalyticsResult:
    query = db.query(Skill)

    if search:
        query = query.filter(Skill.name.ilike(f"%{search}%"))

    total = query.count()
    pages = math.ceil(total / page_size) if page_size > 0 else 0
    skills = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for skill in skills:
        student_count = db.query(func.count(StudentSkill.id)).filter(StudentSkill.skill_id == skill.id).scalar() or 0
        job_count = db.query(func.count(JobSkill.id)).filter(JobSkill.skill_id == skill.id).scalar() or 0
        items.append(SkillAnalyticsItem(
            skill_id=skill.id,
            skill_name=skill.name,
            category=skill.category.value,
            student_count=student_count,
            job_count=job_count,
        ))

    return SkillAnalyticsResult(items=items, total=total, page=page, page_size=page_size, pages=pages)


@dataclass
class CareerAnalyticsItem:
    career_id: int
    career_name: str
    recommendation_count: int
    job_count: int
    skill_count: int


def list_careers_analytics(db: Session) -> list[CareerAnalyticsItem]:
    careers = db.query(Career).all()
    items = []
    for career in careers:
        rec_count = db.query(func.count(CareerRecommendation.id)).filter(CareerRecommendation.career_id == career.id).scalar() or 0

        from app.models.career_job_mapping import CareerJobMapping
        job_count = db.query(func.count(CareerJobMapping.id)).filter(CareerJobMapping.career_id == career.id).scalar() or 0

        skill_count = db.query(func.count(CareerSkill.id)).filter(CareerSkill.career_id == career.id).scalar() or 0
        items.append(CareerAnalyticsItem(
            career_id=career.id,
            career_name=career.name,
            recommendation_count=rec_count,
            job_count=job_count,
            skill_count=skill_count,
        ))

    items.sort(key=lambda x: x.recommendation_count, reverse=True)
    return items


@dataclass
class JobAnalytics:
    total_jobs: int
    top_cities: list[dict]
    top_sectors: list[dict]
    top_skills: list[dict]


def get_job_analytics(db: Session) -> JobAnalytics:
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

    return JobAnalytics(
        total_jobs=total,
        top_cities=[{"name": c, "count": n} for c, n in cities],
        top_sectors=[{"name": s, "count": n} for s, n in sectors],
        top_skills=[{"name": s, "count": n} for s, n in skills],
    )


@dataclass
class LearningAnalytics:
    total_resources: int
    total_progress_records: int
    started: int
    completed: int
    completion_rate: float
    most_popular_resources: list[dict]
    most_studied_skills: list[dict]


def get_learning_analytics(db: Session) -> LearningAnalytics:
    total_resources = db.query(func.count(LearningResource.id)).scalar() or 0
    total_progress = db.query(func.count(StudentLearningResource.id)).scalar() or 0

    started = (
        db.query(func.count(StudentLearningResource.id))
        .filter(StudentLearningResource.status.in_(["in_progress", "completed"]))
        .scalar() or 0
    )
    completed = (
        db.query(func.count(StudentLearningResource.id))
        .filter(StudentLearningResource.status == "completed")
        .scalar() or 0
    )
    completion_rate = round((completed / started * 100) if started > 0 else 0.0, 1)

    popular = (
        db.query(LearningResource.title, func.count(StudentLearningResource.id).label("cnt"))
        .join(StudentLearningResource, StudentLearningResource.resource_id == LearningResource.id)
        .group_by(LearningResource.title)
        .order_by(func.count(StudentLearningResource.id).desc())
        .limit(10)
        .all()
    )

    studied = (
        db.query(Skill.name, func.count(StudentLearningResource.id).label("cnt"))
        .join(LearningResourceSkill, LearningResourceSkill.skill_id == Skill.id)
        .join(StudentLearningResource, StudentLearningResource.resource_id == LearningResourceSkill.resource_id)
        .group_by(Skill.name)
        .order_by(func.count(StudentLearningResource.id).desc())
        .limit(10)
        .all()
    )

    return LearningAnalytics(
        total_resources=total_resources,
        total_progress_records=total_progress,
        started=started,
        completed=completed,
        completion_rate=completion_rate,
        most_popular_resources=[{"title": t, "count": n} for t, n in popular],
        most_studied_skills=[{"name": s, "count": n} for s, n in studied],
    )


@dataclass
class AIAnalytics:
    total_conversations: int
    total_messages: int
    active_users: int
    avg_messages_per_conversation: float


def get_ai_analytics(db: Session) -> AIAnalytics:
    total_conversations = db.query(func.count(AssistantConversation.id)).scalar() or 0
    total_messages = db.query(func.count(AssistantMessage.id)).scalar() or 0

    active_users = (
        db.query(func.count(distinct(AssistantConversation.student_id)))
        .scalar() or 0
    )

    avg_msgs = round(total_messages / total_conversations, 1) if total_conversations > 0 else 0.0

    return AIAnalytics(
        total_conversations=total_conversations,
        total_messages=total_messages,
        active_users=active_users,
        avg_messages_per_conversation=avg_msgs,
    )


@dataclass
class SystemHealth:
    api_status: str
    database_status: str
    ml_model_status: str
    llm_provider_status: str


def get_system_health(db: Session) -> SystemHealth:
    db_status = "healthy"
    try:
        db.execute(func.now())
    except Exception:
        db_status = "unhealthy"

    ml_status = "not_configured"
    ml_path = os.getenv("ML_MODEL_PATH", "")
    if not ml_path:
        ml_path = str(Path(__file__).resolve().parent.parent / "ml" / "artifacts" / "skillbridge_career_classifier.joblib")
    if os.path.exists(ml_path):
        ml_status = "available"

    llm_status = "not_configured"
    api_key = os.getenv("LLM_API_KEY", "")
    provider = os.getenv("LLM_PROVIDER", "openai")
    if api_key:
        llm_status = f"configured ({provider})"
    else:
        llm_status = f"not_configured ({provider})"

    return SystemHealth(
        api_status="healthy",
        database_status=db_status,
        ml_model_status=ml_status,
        llm_provider_status=llm_status,
    )


def create_audit_log(
    db: Session,
    admin_user_id: int | None,
    action: str,
    resource_type: str | None = None,
    resource_id: int | None = None,
    metadata: dict | None = None,
) -> AdminAuditLog:
    log = AdminAuditLog(
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_audit_logs(
    db: Session,
    action: str | None = None,
    admin_user_id: int | None = None,
    resource_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    query = db.query(AdminAuditLog)

    if action:
        query = query.filter(AdminAuditLog.action == action)
    if admin_user_id:
        query = query.filter(AdminAuditLog.admin_user_id == admin_user_id)
    if resource_type:
        query = query.filter(AdminAuditLog.resource_type == resource_type)
    if date_from:
        query = query.filter(AdminAuditLog.timestamp >= date_from)
    if date_to:
        query = query.filter(AdminAuditLog.timestamp <= date_to)

    total = query.count()
    pages = math.ceil(total / page_size) if page_size > 0 else 0
    logs = query.order_by(AdminAuditLog.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for log in logs:
        admin_email = None
        if log.admin_user_id:
            admin = db.query(User).filter(User.id == log.admin_user_id).first()
            admin_email = admin.email if admin else None
        items.append({
            "id": log.id,
            "admin_user_id": log.admin_user_id,
            "admin_email": admin_email,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "metadata": json.loads(log.metadata_json) if log.metadata_json else None,
            "timestamp": log.timestamp,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size, "pages": pages}
