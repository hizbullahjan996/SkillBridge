"""Tests for Job, Recommendation, and SkillGap models."""
from datetime import date

from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.skill import Skill, SkillCategory
from app.models.career import Career
from app.models.student import StudentProfile
from app.models.user import User, UserRole
from app.models.recommendation import CareerRecommendation
from app.models.skill_gap import SkillGapReport, SkillGapItem, GapItemStatus


def _make_student(db_session):
    user = User(email="job_test@example.com", password_hash="h", role=UserRole.student)
    db_session.add(user)
    db_session.flush()
    profile = StudentProfile(
        user_id=user.id, full_name="J", age=22, gender="M",
        university_year="Senior", major="CS", cgpa=3.5,
        attendance_percentage=88, study_hours_per_week=18,
        projects_completed=4, certifications_count=1, internships=1,
        communication_skills=7, teamwork=7, problem_solving=8,
        interest_domain="Software Development",
    )
    db_session.add(profile)
    db_session.flush()
    return profile


def test_create_job(db_session):
    job = Job(
        job_title="Backend Developer",
        job_title_clean="Backend Developer",
        company="Tkxel",
        city="Karachi",
        sector="IT & Technology",
        salary_min=90000,
        salary_max=145000,
        salary_average=117500,
        experience_min_years=1.0,
        experience_max_years=3.0,
        experience_required_raw="1-3 years",
        education_level="Bachelor's",
        job_type="Remote",
        gender_preference="Female",
        number_of_vacancies=7,
        posted_date=date(2024, 9, 29),
        application_deadline=date(2024, 11, 20),
    )
    db_session.add(job)
    db_session.commit()

    assert job.id is not None
    assert job.job_title == "Backend Developer"
    assert job.salary_average == 117500


def test_job_skill_relationship(db_session):
    job = Job(
        job_title="Data Analyst", job_title_clean="Data Analyst",
        company="ACME", city="Lahore", sector="Technology",
    )
    skill = Skill(name="SQL", normalized_name="sql", category=SkillCategory.technical)
    db_session.add_all([job, skill])
    db_session.flush()

    js = JobSkill(job_id=job.id, skill_id=skill.id)
    db_session.add(js)
    db_session.commit()

    assert js.id is not None
    assert len(job.job_skills) == 1


def test_career_recommendation(db_session):
    profile = _make_student(db_session)
    career = Career(name="Data Analyst", normalized_name="data_analyst")
    db_session.add(career)
    db_session.flush()

    rec = CareerRecommendation(
        student_id=profile.id,
        career_id=career.id,
        rank=1,
        probability=0.85,
        model_version="v1.0",
    )
    db_session.add(rec)
    db_session.commit()

    assert rec.id is not None
    assert rec.probability == 0.85
    assert rec.rank == 1
    assert len(profile.career_recommendations) == 1


def test_skill_gap_report(db_session):
    profile = _make_student(db_session)
    career = Career(name="ML Engineer", normalized_name="ml_engineer")
    db_session.add(career)
    db_session.flush()

    report = SkillGapReport(
        student_id=profile.id,
        career_id=career.id,
        match_percentage=65.0,
    )
    db_session.add(report)
    db_session.commit()

    assert report.id is not None
    assert report.match_percentage == 65.0


def test_skill_gap_items(db_session):
    profile = _make_student(db_session)
    career = Career(name="Data Scientist", normalized_name="data_scientist")
    skill_matched = Skill(name="Python", normalized_name="python", category=SkillCategory.technical)
    skill_missing = Skill(name="TensorFlow", normalized_name="tensorflow", category=SkillCategory.technical)
    db_session.add_all([career, skill_matched, skill_missing])
    db_session.flush()

    report = SkillGapReport(student_id=profile.id, career_id=career.id, match_percentage=50.0)
    db_session.add(report)
    db_session.flush()

    item1 = SkillGapItem(report_id=report.id, skill_id=skill_matched.id, status=GapItemStatus.matched, priority=None)
    item2 = SkillGapItem(report_id=report.id, skill_id=skill_missing.id, status=GapItemStatus.missing, priority=1)
    db_session.add_all([item1, item2])
    db_session.commit()

    assert len(report.items) == 2
    matched_items = [i for i in report.items if i.status == GapItemStatus.matched]
    missing_items = [i for i in report.items if i.status == GapItemStatus.missing]
    assert len(matched_items) == 1
    assert len(missing_items) == 1
    assert missing_items[0].priority == 1


def test_cascade_delete_student_removes_recommendations(db_session):
    profile = _make_student(db_session)
    career = Career(name="Test", normalized_name="test_career")
    db_session.add(career)
    db_session.flush()

    rec = CareerRecommendation(student_id=profile.id, career_id=career.id, rank=1, probability=0.9)
    db_session.add(rec)
    db_session.commit()

    user = profile.user
    db_session.delete(user)
    db_session.commit()

    remaining = db_session.query(CareerRecommendation).all()
    assert len(remaining) == 0
