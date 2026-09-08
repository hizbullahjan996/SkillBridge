"""E2E regression tests for the career recommendation flow.

Covers the five endpoint behaviors from Phase 10:
1. POST /recommendations/careers -> creates CareerRecommendation rows
2. GET /recommendations/careers/latest -> returns non-empty recommendations
3. GET /recommendations/jobs -> returns ranked jobs when data exists
4. GET /skill-gaps/career/{career_id} -> returns skill gap data
5. GET /learning-resources/recommended -> returns resources for missing skills

These tests exercise the REAL ML model artifact so they guard against
feature-column / model-path regressions.
"""
import pytest

from app.core.security import hash_password
from app.models.career import Career
from app.models.career_job_mapping import CareerJobMapping, MappingType
from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.learning_resource import (
    LearningResource,
    LearningResourceSkill,
    ResourceDifficulty,
    ResourceType,
)
from app.models.skill import Skill, SkillCategory
from app.models.student import StudentProfile
from app.models.student_skill import StudentSkill
from app.models.user import User, UserRole

MODEL_CLASSES = [
    "AI Engineer",
    "Automation Engineer",
    "Backend Developer",
    "Business Analyst",
    "Cloud Engineer",
    "Cybersecurity Analyst",
    "Data Analyst",
    "Data Scientist",
    "DevOps Engineer",
    "Embedded Systems Engineer",
    "Full Stack Developer",
    "IT Support Engineer",
    "Machine Learning Engineer",
    "Penetration Tester",
    "SOC Analyst",
    "Software Engineer",
]

MAPPING_JOB_TITLE = "software_engineer_role"


def _create_user_profile(db_session):
    user = User(
        email="flow@example.com",
        password_hash=hash_password("Password123!"),
        role=UserRole.student,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    profile = StudentProfile(
        user_id=user.id,
        full_name="Flow Tester",
        age=22,
        gender="Male",
        university_year="Senior",
        major="Computer Science",
        cgpa=3.6,
        attendance_percentage=88,
        study_hours_per_week=18,
        projects_completed=5,
        certifications_count=2,
        internships=1,
        communication_skills=8,
        teamwork=8,
        problem_solving=9,
        interest_domain="Software Development",
    )
    db_session.add(profile)
    db_session.flush()
    return user, profile


def _seed_careers(db_session):
    careers = []
    for name in MODEL_CLASSES:
        normalized = name.lower().replace(" ", "_").replace("-", "_")
        career = Career(name=name, normalized_name=normalized)
        db_session.add(career)
        careers.append(career)
    db_session.flush()
    return careers


def _seed_skills_and_job(db_session):
    python = Skill(name="Python", normalized_name="python", category=SkillCategory.technical)
    docker = Skill(name="Docker", normalized_name="docker", category=SkillCategory.technical)
    db_session.add_all([python, docker])
    db_session.flush()

    job = Job(
        job_title="Software Engineer Role",
        job_title_clean=MAPPING_JOB_TITLE,
        company="TestCorp",
        city="Islamabad",
        sector="Technology",
        education_level="Bachelor's",
        experience_min_years=1,
        experience_required_raw="1 year",
        job_type="Full-time",
    )
    db_session.add(job)
    db_session.flush()

    db_session.add_all([
        JobSkill(job_id=job.id, skill_id=python.id, importance=8),
        JobSkill(job_id=job.id, skill_id=docker.id, importance=5),
    ])
    db_session.flush()
    return job, python, docker


def _link_career_mappings(db_session, careers):
    for career in careers:
        db_session.add(CareerJobMapping(
            career_id=career.id,
            job_title_clean=MAPPING_JOB_TITLE,
            mapping_type=MappingType.strong,
            confidence="1.0",
            is_verified=True,
        ))
    db_session.flush()


def _seed_learning_resource(db_session, docker):
    resource = LearningResource(
        title="Docker Crash Course",
        provider="TestAcademy",
        description="Hands-on Docker container tutorial.",
        url="https://example.com/docker",
        resource_type=ResourceType.tutorial,
        difficulty=ResourceDifficulty.beginner,
        is_free=True,
    )
    db_session.add(resource)
    db_session.flush()
    db_session.add(LearningResourceSkill(resource_id=resource.id, skill_id=docker.id))
    db_session.flush()


def _login(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "flow@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def flow_setup(client, db_session):
    user, profile = _create_user_profile(db_session)
    careers = _seed_careers(db_session)
    job, python, docker = _seed_skills_and_job(db_session)
    _link_career_mappings(db_session, careers)
    _seed_learning_resource(db_session, docker)
    db_session.add(StudentSkill(student_id=profile.id, skill_id=python.id, proficiency=9))
    db_session.commit()

    headers = _login(client)
    return {
        "user": user,
        "profile": profile,
        "careers": careers,
        "job": job,
        "python": python,
        "docker": docker,
        "headers": headers,
    }


class TestCareerRecommendationFlow:
    def test_predict_creates_recommendations(self, client, db_session, flow_setup):
        response = client.post("/api/recommendations/careers", headers=flow_setup["headers"])
        assert response.status_code == 200, response.text
        data = response.json()

        assert data["ready"] is True
        assert data["model_version"] == "1.0.0"
        assert len(data["recommendations"]) == 3
        assert data["recommendations"][0]["rank"] == 1
        assert all("career" in r and "probability" in r for r in data["recommendations"])

        from app.models.recommendation import CareerRecommendation

        recs = (
            db_session.query(CareerRecommendation)
            .filter(CareerRecommendation.student_id == flow_setup["profile"].id)
            .all()
        )
        assert len(recs) == 3
        assert sorted([r.rank for r in recs]) == [1, 2, 3]

    def test_latest_recommendation_non_empty(self, client, flow_setup):
        client.post("/api/recommendations/careers", headers=flow_setup["headers"])

        response = client.get("/api/recommendations/careers/latest", headers=flow_setup["headers"])
        assert response.status_code == 200
        data = response.json()

        assert data["model_version"] == "1.0.0"
        assert len(data["recommendations"]) == 3

    def test_recommended_jobs_return_ranked_jobs(self, client, flow_setup):
        client.post("/api/recommendations/careers", headers=flow_setup["headers"])

        response = client.get(
            "/api/recommendations/jobs?page=1&page_size=10", headers=flow_setup["headers"]
        )
        assert response.status_code == 200
        data = response.json()

        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        item = data["items"][0]
        assert item["job_id"] == flow_setup["job"].id
        assert item["match_score"] >= 0
        assert item["career_score"] >= 0
        assert item["in_top_career"] is not None

    def test_skill_gap_returns_data(self, client, flow_setup):
        predict_response = client.post(
            "/api/recommendations/careers", headers=flow_setup["headers"]
        )
        assert predict_response.status_code == 200
        top_career = predict_response.json()["recommendations"][0]["career"]

        career = next(c for c in flow_setup["careers"] if c.name == top_career)

        response = client.get(
            f"/api/skill-gaps/career/{career.id}", headers=flow_setup["headers"]
        )
        assert response.status_code == 200
        data = response.json()

        assert data["career"]["id"] == career.id
        assert data["career"]["name"] == top_career
        gap = data["skill_gap"]
        assert gap["total_required"] == 2
        matched_names = [m["name"] for m in data["matched_skills"]]
        missing_names = [m["skill_name"] for m in data["missing_skills"]]
        assert flow_setup["python"].name in matched_names
        assert flow_setup["docker"].name in missing_names

    def test_learning_resources_recommended(self, client, flow_setup):
        client.post("/api/recommendations/careers", headers=flow_setup["headers"])

        response = client.get(
            "/api/learning-resources/recommended", headers=flow_setup["headers"]
        )
        assert response.status_code == 200
        data = response.json()

        assert data["total"] >= 1
        assert data["career_name"] != ""
        titles = [item["resource"]["title"] for item in data["resources"]]
        assert "Docker Crash Course" in titles