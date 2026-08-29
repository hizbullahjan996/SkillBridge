"""Tests for Skill Gap Analysis and Learning Roadmap."""
import pytest
from app.models.career import Career
from app.models.career_job_mapping import CareerJobMapping, MappingType
from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.skill import Skill, SkillCategory
from app.models.student import StudentProfile
from app.models.student_skill import StudentSkill
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.services.skill_gap_service import (
    classify_priority, compute_priority_scores, compute_skill_gap,
    get_career_required_skills, get_job_required_skills, get_student_skill_ids,
)
from app.services.learning_roadmap_service import generate_roadmap_from_gap


def _make_skill(db, name):
    skill = Skill(name=name, normalized_name=name.lower().replace(" ", "_").replace("-", "_"), category=SkillCategory.technical)
    db.add(skill)
    db.flush()
    return skill

def _make_student_skill(db, student_id, skill_id, proficiency=7):
    ss = StudentSkill(student_id=student_id, skill_id=skill_id, proficiency=proficiency)
    db.add(ss)
    db.flush()
    return ss

def _make_career(db, name):
    career = Career(name=name, normalized_name=name.lower().replace(" ", "_"))
    db.add(career)
    db.flush()
    return career

def _make_job(db, title, company="ACME", city="Karachi"):
    job = Job(job_title=title, job_title_clean=title.lower(), company=company, city=city, sector="IT")
    db.add(job)
    db.flush()
    return job

def _make_job_skill(db, job_id, skill_id, importance=5):
    js = JobSkill(job_id=job_id, skill_id=skill_id, importance=importance)
    db.add(js)
    db.flush()
    return js

def _make_mapping(db, career_id, job_title_clean):
    m = CareerJobMapping(career_id=career_id, job_title_clean=job_title_clean, mapping_type=MappingType.strong, confidence="0.8")
    db.add(m)
    db.flush()
    return m


@pytest.fixture
def auth_client(client, db_session):
    """Register a user and return (client, auth_headers, profile)."""
    response = client.post("/api/auth/register", json={
        "email": "gap_test@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "full_name": "Gap Student",
    })
    assert response.status_code == 201
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    profile = db_session.query(StudentProfile).join(User).filter(User.email == "gap_test@example.com").first()
    return client, headers, profile


class TestSkillGapService:
    def test_get_student_skill_ids(self, db_session):
        from app.models.user import User, UserRole
        user = User(email="svc1@test.com", password_hash="h", role=UserRole.student)
        db_session.add(user)
        db_session.flush()
        profile = StudentProfile(user_id=user.id, full_name="S", age=22, gender="M", university_year="Senior", major="CS", cgpa=3.5, attendance_percentage=88, study_hours_per_week=18, projects_completed=4, certifications_count=1, internships=1, communication_skills=7, teamwork=7, problem_solving=8, interest_domain="Software Development")
        db_session.add(profile)
        db_session.flush()
        s1 = _make_skill(db_session, "Python")
        s2 = _make_skill(db_session, "SQL")
        _make_student_skill(db_session, profile.id, s1.id)
        _make_student_skill(db_session, profile.id, s2.id, proficiency=4)
        db_session.commit()
        ids = get_student_skill_ids(db_session, profile.id)
        assert ids == {s1.id, s2.id}

    def test_get_student_skill_ids_empty(self, db_session):
        from app.models.user import User, UserRole
        user = User(email="svc2@test.com", password_hash="h", role=UserRole.student)
        db_session.add(user)
        db_session.flush()
        profile = StudentProfile(user_id=user.id, full_name="S", age=22, gender="M", university_year="Senior", major="CS", cgpa=3.5, attendance_percentage=88, study_hours_per_week=18, projects_completed=4, certifications_count=1, internships=1, communication_skills=7, teamwork=7, problem_solving=8, interest_domain="Software Development")
        db_session.add(profile)
        db_session.flush()
        db_session.commit()
        ids = get_student_skill_ids(db_session, profile.id)
        assert ids == set()

    def test_compute_skill_gap(self, db_session):
        from app.models.user import User, UserRole
        user = User(email="svc3@test.com", password_hash="h", role=UserRole.student)
        db_session.add(user)
        db_session.flush()
        profile = StudentProfile(user_id=user.id, full_name="S", age=22, gender="M", university_year="Senior", major="CS", cgpa=3.5, attendance_percentage=88, study_hours_per_week=18, projects_completed=4, certifications_count=1, internships=1, communication_skills=7, teamwork=7, problem_solving=8, interest_domain="Software Development")
        db_session.add(profile)
        db_session.flush()
        s1 = _make_skill(db_session, "Python")
        s2 = _make_skill(db_session, "SQL")
        s3 = _make_skill(db_session, "Docker")
        _make_student_skill(db_session, profile.id, s1.id)
        _make_student_skill(db_session, profile.id, s2.id)
        db_session.commit()
        required = {
            s1.id: {"skill_id": s1.id, "skill_name": "Python", "normalized_name": "python", "category": "technical", "avg_importance": 8.0, "demand_count": 5},
            s2.id: {"skill_id": s2.id, "skill_name": "SQL", "normalized_name": "sql", "category": "technical", "avg_importance": 7.0, "demand_count": 4},
            s3.id: {"skill_id": s3.id, "skill_name": "Docker", "normalized_name": "docker", "category": "technical", "avg_importance": 6.0, "demand_count": 3},
        }
        result = compute_skill_gap(db_session, profile.id, required)
        assert result.matched_count == 2
        assert result.missing_count == 1
        assert result.total_required == 3
        assert result.match_percentage == 66.7
        assert len(result.matched_skills) == 2
        assert len(result.missing_skills) == 1
        assert result.missing_skills[0].skill_name == "Docker"

    def test_compute_skill_gap_empty_required(self, db_session):
        from app.models.user import User, UserRole
        user = User(email="svc4@test.com", password_hash="h", role=UserRole.student)
        db_session.add(user)
        db_session.flush()
        profile = StudentProfile(user_id=user.id, full_name="S", age=22, gender="M", university_year="Senior", major="CS", cgpa=3.5, attendance_percentage=88, study_hours_per_week=18, projects_completed=4, certifications_count=1, internships=1, communication_skills=7, teamwork=7, problem_solving=8, interest_domain="Software Development")
        db_session.add(profile)
        db_session.flush()
        db_session.commit()
        result = compute_skill_gap(db_session, profile.id, {})
        assert result.match_percentage == 0.0
        assert result.total_required == 0

    def test_compute_skill_gap_all_matched(self, db_session):
        from app.models.user import User, UserRole
        user = User(email="svc5@test.com", password_hash="h", role=UserRole.student)
        db_session.add(user)
        db_session.flush()
        profile = StudentProfile(user_id=user.id, full_name="S", age=22, gender="M", university_year="Senior", major="CS", cgpa=3.5, attendance_percentage=88, study_hours_per_week=18, projects_completed=4, certifications_count=1, internships=1, communication_skills=7, teamwork=7, problem_solving=8, interest_domain="Software Development")
        db_session.add(profile)
        db_session.flush()
        s1 = _make_skill(db_session, "Python")
        _make_student_skill(db_session, profile.id, s1.id)
        db_session.commit()
        required = {s1.id: {"skill_id": s1.id, "skill_name": "Python", "normalized_name": "python", "category": "technical", "avg_importance": 5.0, "demand_count": 1}}
        result = compute_skill_gap(db_session, profile.id, required)
        assert result.match_percentage == 100.0
        assert result.missing_count == 0

    def test_classify_priority(self):
        assert classify_priority(80.0) == "High"
        assert classify_priority(70.0) == "High"
        assert classify_priority(69.9) == "Medium"
        assert classify_priority(40.0) == "Medium"
        assert classify_priority(39.9) == "Low"
        assert classify_priority(0.0) == "Low"

    def test_compute_priority_scores(self):
        missing = {
            1: {"skill_name": "Docker", "normalized_name": "docker", "category": "technical", "avg_importance": 8.0},
            2: {"skill_name": "AWS", "normalized_name": "aws", "category": "technical", "avg_importance": 5.0},
        }
        demand = {1: 10, 2: 3}
        results = compute_priority_scores(missing, demand)
        assert len(results) == 2
        assert results[0].skill_name == "Docker"
        assert results[0].demand_count == 10
        assert results[0].priority_score > results[1].priority_score

    def test_compute_priority_scores_empty(self):
        assert compute_priority_scores({}, {}) == []

    def test_get_job_required_skills(self, db_session):
        job = _make_job(db_session, "Backend Developer")
        s1 = _make_skill(db_session, "Python")
        s2 = _make_skill(db_session, "SQL")
        _make_job_skill(db_session, job.id, s1.id, importance=9)
        _make_job_skill(db_session, job.id, s2.id, importance=7)
        db_session.commit()
        skills = get_job_required_skills(db_session, job.id)
        assert len(skills) == 2
        assert s1.id in skills
        assert skills[s1.id]["avg_importance"] == 9.0

    def test_get_career_required_skills(self, db_session):
        career = _make_career(db_session, "Data Analyst")
        job = _make_job(db_session, "Data Analyst", company="ACME")
        s1 = _make_skill(db_session, "SQL")
        s2 = _make_skill(db_session, "Python")
        _make_job_skill(db_session, job.id, s1.id, importance=8)
        _make_job_skill(db_session, job.id, s2.id, importance=6)
        _make_mapping(db_session, career.id, "data analyst")
        db_session.commit()
        skills = get_career_required_skills(db_session, career.id)
        assert len(skills) == 2
        assert s1.id in skills


class TestSkillGapAPI:
    def test_career_skill_gap(self, auth_client, db_session):
        client, headers, profile = auth_client
        career = _make_career(db_session, "Data Analyst")
        job = _make_job(db_session, "Data Analyst")
        s1 = _make_skill(db_session, "SQL")
        s2 = _make_skill(db_session, "Python")
        _make_student_skill(db_session, profile.id, s1.id)
        _make_job_skill(db_session, job.id, s1.id, importance=8)
        _make_job_skill(db_session, job.id, s2.id, importance=6)
        _make_mapping(db_session, career.id, "data analyst")
        db_session.commit()
        response = client.get(f"/api/skill-gaps/career/{career.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["career"]["name"] == "Data Analyst"
        assert data["skill_gap"]["matched_count"] == 1
        assert data["skill_gap"]["missing_count"] == 1

    def test_job_skill_gap(self, auth_client, db_session):
        client, headers, profile = auth_client
        job = _make_job(db_session, "Backend Developer")
        s1 = _make_skill(db_session, "Python")
        s2 = _make_skill(db_session, "Docker")
        _make_student_skill(db_session, profile.id, s1.id)
        _make_job_skill(db_session, job.id, s1.id, importance=9)
        _make_job_skill(db_session, job.id, s2.id, importance=7)
        db_session.commit()
        response = client.get(f"/api/skill-gaps/job/{job.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["job"]["title"] == "Backend Developer"
        assert data["skill_gap"]["matched_count"] == 1
        assert data["skill_gap"]["missing_count"] == 1

    def test_career_skill_gap_unauthorized(self, client):
        response = client.get("/api/skill-gaps/career/1")
        assert response.status_code in (401, 403)

    def test_career_skill_gap_not_found(self, auth_client):
        client, headers, profile = auth_client
        response = client.get("/api/skill-gaps/career/9999", headers=headers)
        assert response.status_code == 404

    def test_job_skill_gap_not_found(self, auth_client):
        client, headers, profile = auth_client
        response = client.get("/api/skill-gaps/job/9999", headers=headers)
        assert response.status_code == 404


class TestLearningRoadmap:
    def test_generate_roadmap_from_gap(self):
        from app.services.skill_gap_service import SkillGapResult, SkillGapItemResult
        gap = SkillGapResult(
            matched_skills=[{"id": 1, "name": "Python"}],
            missing_skills=[
                SkillGapItemResult(skill_id=2, skill_name="Docker", normalized_name="docker", category="technical", priority_score=85.0, priority="High", demand_count=10, career_relevance_count=10, avg_importance=8.0),
                SkillGapItemResult(skill_id=3, skill_name="AWS", normalized_name="aws", category="technical", priority_score=60.0, priority="Medium", demand_count=5, career_relevance_count=5, avg_importance=6.0),
            ],
            match_percentage=33.3, total_required=3, matched_count=1, missing_count=2,
        )
        roadmap = generate_roadmap_from_gap(gap, "Data Analyst")
        assert roadmap.total_missing == 2
        assert roadmap.career_name == "Data Analyst"
        assert len(roadmap.roadmap) == 2

    def test_generate_roadmap_empty_gap(self):
        from app.services.skill_gap_service import SkillGapResult
        gap = SkillGapResult(matched_skills=[], missing_skills=[], match_percentage=100.0, total_required=0, matched_count=0, missing_count=0)
        roadmap = generate_roadmap_from_gap(gap, "Data Analyst")
        assert roadmap.total_missing == 0
        assert len(roadmap.roadmap) == 0

    def test_roadmap_ordering(self):
        from app.services.skill_gap_service import SkillGapResult, SkillGapItemResult
        gap = SkillGapResult(
            matched_skills=[],
            missing_skills=[
                SkillGapItemResult(skill_id=1, skill_name="Low Skill", normalized_name="low_skill", category="technical", priority_score=20.0, priority="Low", demand_count=1, career_relevance_count=1, avg_importance=3.0),
                SkillGapItemResult(skill_id=2, skill_name="High Skill", normalized_name="high_skill", category="technical", priority_score=90.0, priority="High", demand_count=10, career_relevance_count=10, avg_importance=9.0),
                SkillGapItemResult(skill_id=3, skill_name="Med Skill", normalized_name="med_skill", category="technical", priority_score=50.0, priority="Medium", demand_count=5, career_relevance_count=5, avg_importance=5.0),
            ],
            match_percentage=0.0, total_required=3, matched_count=0, missing_count=3,
        )
        roadmap = generate_roadmap_from_gap(gap)
        assert roadmap.roadmap[0].skill == "High Skill"
        assert roadmap.roadmap[1].skill == "Med Skill"
        assert roadmap.roadmap[2].skill == "Low Skill"


class TestLearningRoadmapAPI:
    def test_default_roadmap_no_recommendations(self, auth_client):
        client, headers, profile = auth_client
        response = client.get("/api/learning-roadmap", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_career_roadmap(self, auth_client, db_session):
        client, headers, profile = auth_client
        career = _make_career(db_session, "Data Analyst")
        job = _make_job(db_session, "Data Analyst")
        s1 = _make_skill(db_session, "SQL")
        s2 = _make_skill(db_session, "Python")
        _make_student_skill(db_session, profile.id, s1.id)
        _make_job_skill(db_session, job.id, s1.id, importance=8)
        _make_job_skill(db_session, job.id, s2.id, importance=6)
        _make_mapping(db_session, career.id, "data analyst")
        db_session.commit()
        response = client.get(f"/api/learning-roadmap/career/{career.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["career_name"] == "Data Analyst"
        assert data["total_missing"] >= 0

    def test_job_roadmap(self, auth_client, db_session):
        client, headers, profile = auth_client
        job = _make_job(db_session, "Backend Developer")
        s1 = _make_skill(db_session, "Python")
        s2 = _make_skill(db_session, "Docker")
        _make_student_skill(db_session, profile.id, s1.id)
        _make_job_skill(db_session, job.id, s1.id, importance=9)
        _make_job_skill(db_session, job.id, s2.id, importance=7)
        db_session.commit()
        response = client.get(f"/api/learning-roadmap/job/{job.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_missing"] >= 0

    def test_roadmap_unauthorized(self, client):
        response = client.get("/api/learning-roadmap")
        assert response.status_code in (401, 403)
