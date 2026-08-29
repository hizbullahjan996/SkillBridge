from sqlalchemy.orm import Session

from app.models.student import StudentProfile
from app.models.skill import Skill, SkillCategory
from app.models.student_skill import StudentSkill
from app.schemas.profile import (
    ProfileCompletionResponse,
    StudentProfileUpdate,
    StudentProfileResponse,
)
from app.schemas.skill import (
    SkillResponse,
    StudentSkillCreate,
    StudentSkillResponse,
)

# ML-required fields for career prediction
ML_REQUIRED_FIELDS = [
    "age",
    "gender",
    "university_year",
    "major",
    "cgpa",
    "attendance_percentage",
    "study_hours_per_week",
    "projects_completed",
    "certifications_count",
    "internships",
    "communication_skills",
    "teamwork",
    "problem_solving",
    "interest_domain",
]

# All profile fields (including ML-required)
ALL_PROFILE_FIELDS = [
    "age",
    "gender",
    "university_year",
    "major",
    "cgpa",
    "attendance_percentage",
    "study_hours_per_week",
    "projects_completed",
    "certifications_count",
    "internships",
    "communication_skills",
    "teamwork",
    "problem_solving",
    "interest_domain",
]


def get_student_profile(db: Session, user_id: int) -> StudentProfile | None:
    return db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()


def update_student_profile(
    db: Session, user_id: int, profile_data: StudentProfileUpdate
) -> StudentProfile | None:
    profile = get_student_profile(db, user_id)
    if not profile:
        return None

    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


def calculate_profile_completion(profile: StudentProfile) -> ProfileCompletionResponse:
    completed_fields = []
    missing_fields = []

    for field in ALL_PROFILE_FIELDS:
        value = getattr(profile, field, None)
        if value is not None and value != "":
            completed_fields.append(field)
        else:
            missing_fields.append(field)

    total = len(ALL_PROFILE_FIELDS)
    completed = len(completed_fields)
    percentage = (completed / total * 100) if total > 0 else 0

    return ProfileCompletionResponse(
        percentage=round(percentage, 1),
        completed_fields=completed_fields,
        missing_fields=missing_fields,
        total_required=total,
        completed_count=completed,
    )


def check_ml_readiness(
    db: Session, user_id: int
) -> dict:
    profile = get_student_profile(db, user_id)
    if not profile:
        return {
            "ready": False,
            "missing_fields": ML_REQUIRED_FIELDS.copy(),
            "missing_skills": [],
            "profile_completion": 0.0,
            "skills_count": 0,
        }

    missing_fields = []
    for field in ML_REQUIRED_FIELDS:
        value = getattr(profile, field, None)
        if value is None or value == "":
            missing_fields.append(field)

    student_skills = (
        db.query(StudentSkill)
        .filter(StudentSkill.student_id == profile.id)
        .all()
    )
    skills_count = len(student_skills)

    completion = calculate_profile_completion(profile)

    return {
        "ready": len(missing_fields) == 0 and skills_count > 0,
        "missing_fields": missing_fields,
        "missing_skills": [],
        "profile_completion": completion.percentage,
        "skills_count": skills_count,
    }


def get_all_skills(
    db: Session, category: str | None = None, search: str | None = None
) -> list[Skill]:
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    if search:
        query = query.filter(Skill.name.ilike(f"%{search}%"))
    return query.order_by(Skill.name).all()


def get_skill_by_id(db: Session, skill_id: int) -> Skill | None:
    return db.query(Skill).filter(Skill.id == skill_id).first()


def get_student_skills(db: Session, student_id: int) -> list[StudentSkill]:
    return (
        db.query(StudentSkill)
        .filter(StudentSkill.student_id == student_id)
        .all()
    )


def add_student_skill(
    db: Session, student_id: int, skill_data: StudentSkillCreate
) -> StudentSkill | None:
    existing = (
        db.query(StudentSkill)
        .filter(
            StudentSkill.student_id == student_id,
            StudentSkill.skill_id == skill_data.skill_id,
        )
        .first()
    )
    if existing:
        return None

    skill = get_skill_by_id(db, skill_data.skill_id)
    if not skill:
        return None

    student_skill = StudentSkill(
        student_id=student_id,
        skill_id=skill_data.skill_id,
        proficiency=skill_data.proficiency,
    )
    db.add(student_skill)
    db.commit()
    db.refresh(student_skill)
    return student_skill


def remove_student_skill(
    db: Session, student_id: int, skill_id: int
) -> bool:
    student_skill = (
        db.query(StudentSkill)
        .filter(
            StudentSkill.student_id == student_id,
            StudentSkill.skill_id == skill_id,
        )
        .first()
    )
    if not student_skill:
        return False

    db.delete(student_skill)
    db.commit()
    return True


def replace_student_skills(
    db: Session, student_id: int, skills: list[StudentSkillCreate]
) -> list[StudentSkill]:
    db.query(StudentSkill).filter(StudentSkill.student_id == student_id).delete()

    result = []
    for skill_data in skills:
        skill = get_skill_by_id(db, skill_data.skill_id)
        if skill:
            student_skill = StudentSkill(
                student_id=student_id,
                skill_id=skill_data.skill_id,
                proficiency=skill_data.proficiency,
            )
            db.add(student_skill)
            result.append(student_skill)

    db.commit()
    for s in result:
        db.refresh(s)
    return result
