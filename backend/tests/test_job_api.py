"""Tests for Jobs API endpoints and matching service."""
from datetime import date

from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.skill import Skill, SkillCategory
from app.models.career import Career
from app.models.career_skill import CareerSkill
from app.models.career_job_mapping import CareerJobMapping, MappingType
from app.models.student import StudentProfile
from app.models.student_skill import StudentSkill
from app.models.user import User, UserRole
from app.models.recommendation import CareerRecommendation


def _create_job(db, title="Backend Developer", company="Tkxel", city="Karachi", sector="IT"):
    job = Job(
        job_title=title,
        job_title_clean=title.lower(),
        company=company,
        city=city,
        sector=sector,
        salary_min=90000,
        salary_max=145000,
        salary_average=117500,
        experience_min_years=1.0,
        experience_max_years=3.0,
        experience_required_raw="1-3 years",
        education_level="Bachelor's",
        job_type="Remote",
        number_of_vacancies=5,
        posted_date=date(2024, 9, 29),
        application_deadline=date(2024, 11, 20),
    )
    db.add(job)
    db.flush()
    return job


def _create_skill(db, name):
    skill = Skill(name=name, normalized_name=name.lower().replace(" ", "_"), category=SkillCategory.technical)
    db.add(skill)
    db.flush()
    return skill


def _create_student_with_skills(db):
    user = User(email="jobtest@example.com", password_hash="h", role=UserRole.student)
    db.add(user)
    db.flush()
    profile = StudentProfile(
        user_id=user.id, full_name="Test Student", age=22, gender="M",
        university_year="Senior", major="BS Computer Science", cgpa=3.5,
        attendance_percentage=88, study_hours_per_week=18,
        projects_completed=4, certifications_count=1, internships=1,
        communication_skills=7, teamwork=7, problem_solving=8,
        interest_domain="Software Development",
    )
    db.add(profile)
    db.flush()
    return user, profile


class TestJobAPI:
    def test_list_jobs_empty(self, client):
        response = client.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_jobs_with_data(self, client, db_session):
        _create_job(db_session, "Backend Developer", "Tkxel", "Karachi")
        _create_job(db_session, "Frontend Developer", "Devsinc", "Lahore")
        db_session.commit()

        response = client.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_jobs_filter_city(self, client, db_session):
        _create_job(db_session, "Backend Developer", "Tkxel", "Karachi")
        _create_job(db_session, "Frontend Developer", "Devsinc", "Lahore")
        db_session.commit()

        response = client.get("/api/jobs?city=Karachi")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["city"] == "Karachi"

    def test_list_jobs_filter_sector(self, client, db_session):
        _create_job(db_session, "Backend Developer", "Tkxel", "Karachi", "IT & Technology")
        _create_job(db_session, "Nurse", "Hospital", "Lahore", "Healthcare")
        db_session.commit()

        response = client.get("/api/jobs?sector=IT")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "IT" in data["items"][0]["sector"]

    def test_list_jobs_filter_job_type(self, client, db_session):
        _create_job(db_session, "Backend Developer", "Tkxel", "Karachi")
        job2 = Job(
            job_title="Frontend Developer", job_title_clean="frontend developer",
            company="Devsinc", city="Lahore", sector="IT",
            job_type="Onsite",
        )
        db_session.add(job2)
        db_session.commit()

        response = client.get("/api/jobs?job_type=Remote")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["job_type"] == "Remote"

    def test_list_jobs_search(self, client, db_session):
        _create_job(db_session, "Backend Developer", "Tkxel", "Karachi")
        _create_job(db_session, "Data Analyst", "ACME", "Lahore")
        db_session.commit()

        response = client.get("/api/jobs?search=backend")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "Backend" in data["items"][0]["job_title"]

    def test_list_jobs_pagination(self, client, db_session):
        for i in range(25):
            _create_job(db_session, f"Job {i}", f"Company {i}", "Karachi")
        db_session.commit()

        response = client.get("/api/jobs?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert len(data["items"]) == 10
        assert data["pages"] == 3

    def test_get_job_detail(self, client, db_session):
        job = _create_job(db_session)
        skill = _create_skill(db_session, "Python")
        js = JobSkill(job_id=job.id, skill_id=skill.id)
        db_session.add(js)
        db_session.commit()

        response = client.get(f"/api/jobs/{job.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["job_title"] == "Backend Developer"
        assert len(data["required_skills"]) == 1
        assert data["required_skills"][0]["skill_name"] == "Python"

    def test_get_job_not_found(self, client, db_session):
        response = client.get("/api/jobs/9999")
        assert response.status_code == 404


class TestJobMatchingService:
    def test_compute_skill_score(self, client, db_session):
        from app.services.job_matching_service import compute_skill_score

        job = _create_job(db_session)
        skill1 = _create_skill(db_session, "Python")
        skill2 = _create_skill(db_session, "JavaScript")
        db_session.add_all([
            JobSkill(job_id=job.id, skill_id=skill1.id),
            JobSkill(job_id=job.id, skill_id=skill2.id),
        ])
        db_session.commit()

        student_has = {skill1.id}
        score = compute_skill_score(student_has, job.id, db_session)
        assert score == 0.5

    def test_compute_education_score(self):
        from app.services.job_matching_service import compute_education_score
        assert compute_education_score("BS Computer Science", "Bachelor's") == 1.0
        assert compute_education_score("Intermediate", "Bachelor's") < 1.0

    def test_compute_experience_score(self):
        from app.services.job_matching_service import compute_experience_score
        assert compute_experience_score(3, 1) == 1.0
        assert compute_experience_score(0, 2) < 1.0
        assert compute_experience_score(0, None) == 1.0


class TestRecommendedJobsAPI:
    def test_recommended_jobs_no_profile(self, client, db_session):
        user = User(email="norec@example.com", password_hash="h", role=UserRole.student)
        db_session.add(user)
        db_session.commit()

        from app.core.jwt import create_access_token
        token = create_access_token(data={"sub": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/recommendations/jobs", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 0
