"""Job matching engine - scores jobs against student profiles."""
import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.career_job_mapping import CareerJobMapping
from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.recommendation import CareerRecommendation
from app.models.skill import Skill
from app.models.student import StudentProfile
from app.models.student_skill import StudentSkill

logger = logging.getLogger("skillbridge")

# Matching weights (configurable)
WEIGHT_CAREER = 0.35
WEIGHT_SKILL = 0.35
WEIGHT_EDUCATION = 0.15
WEIGHT_EXPERIENCE = 0.15

EDUCATION_HIERARCHY = {
    "matric": 1,
    "intermediate": 2,
    "bachelor's": 3,
    "mba": 4,
    "master's": 4,
    "mphil": 5,
    "phd": 6,
    "mbbs": 5,
}


def compute_career_score(job, top_career_ids, db):
    if not top_career_ids:
        return 0.0

    mappings = (
        db.query(CareerJobMapping)
        .filter(CareerJobMapping.career_id.in_(top_career_ids))
        .all()
    )

    matching_mappings = [
        m for m in mappings
        if m.job_title_clean.lower() == job.job_title_clean.lower()
    ]

    if not matching_mappings:
        return 0.0

    best_confidence = max(float(m.confidence or 0) for m in matching_mappings)
    best_career_id = max(matching_mappings, key=lambda m: float(m.confidence or 0)).career_id

    rank_bonus = 0.0
    if best_career_id in top_career_ids:
        rank = top_career_ids.index(best_career_id)
        rank_bonus = max(0, (3 - rank) / 3.0 * 0.1)

    return min(1.0, best_confidence + rank_bonus)


def compute_skill_score(student_skills_set, job_id, db):
    job_skill_rows = db.query(JobSkill).filter(JobSkill.job_id == job_id).all()
    if not job_skill_rows:
        return 1.0

    job_skill_ids = {js.skill_id for js in job_skill_rows}
    matched = len(student_skills_set & job_skill_ids)
    total = len(job_skill_ids)

    return matched / total if total > 0 else 1.0


def compute_education_score(student_major, job_education_level):
    if not job_education_level:
        return 1.0

    job_level = EDUCATION_HIERARCHY.get(job_education_level.lower(), 3)
    student_level = 3

    if student_major:
        major_lower = student_major.lower()
        if "phd" in major_lower:
            student_level = 6
        elif "mphil" in major_lower or "mbbs" in major_lower:
            student_level = 5
        elif "master" in major_lower or "mba" in major_lower:
            student_level = 4
        elif "bachelor" in major_lower:
            student_level = 3
        elif "intermediate" in major_lower:
            student_level = 2

    if student_level >= job_level:
        return 1.0
    elif student_level == job_level - 1:
        return 0.7
    else:
        return 0.3


def compute_experience_score(internships, job_exp_min):
    if job_exp_min is None:
        return 1.0
    if job_exp_min == 0:
        return 1.0

    effective = internships * 0.5

    if effective >= job_exp_min:
        return 1.0
    elif effective >= job_exp_min * 0.5:
        return 0.7
    else:
        return 0.3


def compute_job_match_score(job, profile, student_skill_ids, top_career_ids, db):
    career = compute_career_score(job, top_career_ids, db)
    skill = compute_skill_score(student_skill_ids, job.id, db)
    education = compute_education_score(profile.major, job.education_level)
    experience = compute_experience_score(profile.internships, job.experience_min_years)

    total = (
        career * WEIGHT_CAREER
        + skill * WEIGHT_SKILL
        + education * WEIGHT_EDUCATION
        + experience * WEIGHT_EXPERIENCE
    )

    return {
        "score": round(total * 100, 1),
        "career_score": round(career * 100, 1),
        "skill_match_percentage": round(skill * 100, 1),
        "education_score": round(education * 100, 1),
        "experience_score": round(experience * 100, 1),
    }


def get_recommended_jobs(db, user_id, page=1, page_size=10, city=None, sector=None, job_type=None, min_salary=None):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if not profile:
        return {"items": [], "total": 0, "page": page, "page_size": page_size, "pages": 0}

    top_recs = (
        db.query(CareerRecommendation)
        .filter(CareerRecommendation.student_id == profile.id)
        .order_by(CareerRecommendation.rank)
        .limit(3)
        .all()
    )
    top_career_ids = [r.career_id for r in top_recs]

    student_skills = db.query(StudentSkill).filter(StudentSkill.student_id == profile.id).all()
    student_skill_ids = {ss.skill_id for ss in student_skills}

    job_ids_for_careers = set()
    if top_career_ids:
        mappings = (
            db.query(CareerJobMapping)
            .filter(CareerJobMapping.career_id.in_(top_career_ids))
            .all()
        )
        for m in mappings:
            job_title_matches = db.query(Job.id).filter(Job.job_title_clean == m.job_title_clean).all()
            for (jid,) in job_title_matches:
                job_ids_for_careers.add(jid)

    query = db.query(Job)
    if city:
        query = query.filter(Job.city.ilike(f"%{city}%"))
    if sector:
        query = query.filter(Job.sector.ilike(f"%{sector}%"))
    if job_type:
        query = query.filter(Job.job_type.ilike(f"%{job_type}%"))
    if min_salary:
        query = query.filter(Job.salary_average >= min_salary)

    all_matching_jobs = query.all()

    scored_jobs = []
    for job in all_matching_jobs:
        scores = compute_job_match_score(job, profile, student_skill_ids, top_career_ids, db)

        skill_rows = db.query(JobSkill).filter(JobSkill.job_id == job.id).all()
        skill_ids = {js.skill_id for js in skill_rows}
        matched_count = len(student_skill_ids & skill_ids)
        total_required = len(skill_ids)

        scored_jobs.append({
            "job_id": job.id,
            "job_title": job.job_title,
            "company": job.company,
            "city": job.city,
            "sector": job.sector,
            "job_type": job.job_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_average": job.salary_average,
            "education_level": job.education_level,
            "experience_required": job.experience_required_raw,
            "match_score": scores["score"],
            "skill_match_percentage": scores["skill_match_percentage"],
            "career_score": scores["career_score"],
            "education_score": scores["education_score"],
            "experience_score": scores["experience_score"],
            "matched_skills": matched_count,
            "total_required_skills": total_required,
            "in_top_career": job.id in job_ids_for_careers,
        })

    scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    total = len(scored_jobs)
    start = (page - 1) * page_size
    end = start + page_size
    items = scored_jobs[start:end]
    pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }
