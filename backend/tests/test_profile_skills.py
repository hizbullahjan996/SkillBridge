"""Tests for profile and skills endpoints."""
import pytest
from app.models.user import User, UserRole
from app.models.student import StudentProfile
from app.models.skill import Skill, SkillCategory
from app.models.student_skill import StudentSkill
from app.core.security import hash_password


@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        password_hash=hash_password("Password123!"),
        role=UserRole.student,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_profile(db_session, test_user):
    profile = StudentProfile(
        user_id=test_user.id,
        full_name="Test Student",
        age=21,
        gender="Male",
        university_year="Junior",
        major="Computer Science",
        cgpa=3.5,
        attendance_percentage=85.0,
        study_hours_per_week=20,
        projects_completed=5,
        certifications_count=2,
        internships=1,
        communication_skills=7,
        teamwork=8,
        problem_solving=7,
        interest_domain="Software Development",
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture
def test_skills(db_session):
    skills = [
        Skill(name="Python", normalized_name="python", category=SkillCategory.technical),
        Skill(name="JavaScript", normalized_name="javascript", category=SkillCategory.technical),
        Skill(name="SQL", normalized_name="sql", category=SkillCategory.technical),
        Skill(name="Communication", normalized_name="communication", category=SkillCategory.soft),
    ]
    db_session.add_all(skills)
    db_session.commit()
    for s in skills:
        db_session.refresh(s)
    return skills


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "Password123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestProfileEndpoints:
    def test_get_my_profile(self, client, auth_headers, test_profile):
        response = client.get("/api/students/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Test Student"
        assert data["age"] == 21
        assert data["gender"] == "Male"
        assert data["cgpa"] == 3.5

    def test_get_my_profile_unauthorized(self, client):
        response = client.get("/api/students/me")
        assert response.status_code == 401

    def test_update_my_profile(self, client, auth_headers, test_profile):
        response = client.put(
            "/api/students/me",
            headers=auth_headers,
            json={"age": 22, "cgpa": 3.8},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["age"] == 22
        assert data["cgpa"] == 3.8

    def test_update_my_profile_invalid_cgpa(self, client, auth_headers, test_profile):
        response = client.put(
            "/api/students/me",
            headers=auth_headers,
            json={"cgpa": 5.0},
        )
        assert response.status_code == 422

    def test_update_my_profile_invalid_age(self, client, auth_headers, test_profile):
        response = client.put(
            "/api/students/me",
            headers=auth_headers,
            json={"age": 10},
        )
        assert response.status_code == 422

    def test_get_profile_completion(self, client, auth_headers, test_profile):
        response = client.get(
            "/api/students/me/profile-completion", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "percentage" in data
        assert "completed_fields" in data
        assert "missing_fields" in data
        assert data["percentage"] > 0

    def test_get_ml_readiness(self, client, auth_headers, test_profile, test_skills):
        for skill in test_skills[:2]:
            client.post(
                "/api/skills/me",
                headers=auth_headers,
                json={"skill_id": skill.id, "proficiency": 7},
            )

        response = client.get(
            "/api/students/me/ml-readiness", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
        assert "missing_fields" in data
        assert "missing_skills" in data
        assert "skills_count" in data


class TestSkillsEndpoints:
    def test_get_all_skills(self, client, test_skills):
        response = client.get("/api/skills")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    def test_get_skills_by_category(self, client, test_skills):
        response = client.get("/api/skills?category=technical")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_skills_search(self, client, test_skills):
        response = client.get("/api/skills?search=Python")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Python"

    def test_get_my_skills(self, client, auth_headers, test_profile, test_skills):
        client.post(
            "/api/skills/me",
            headers=auth_headers,
            json={"skill_id": test_skills[0].id, "proficiency": 8},
        )

        response = client.get("/api/students/me/skills", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["proficiency"] == 8

    def test_add_skill(self, client, auth_headers, test_profile, test_skills):
        response = client.post(
            "/api/skills/me",
            headers=auth_headers,
            json={"skill_id": test_skills[0].id, "proficiency": 7},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["skill_id"] == test_skills[0].id
        assert data["proficiency"] == 7

    def test_add_duplicate_skill(self, client, auth_headers, test_profile, test_skills):
        client.post(
            "/api/skills/me",
            headers=auth_headers,
            json={"skill_id": test_skills[0].id, "proficiency": 7},
        )
        response = client.post(
            "/api/skills/me",
            headers=auth_headers,
            json={"skill_id": test_skills[0].id, "proficiency": 5},
        )
        assert response.status_code == 409

    def test_add_nonexistent_skill(self, client, auth_headers, test_profile):
        response = client.post(
            "/api/skills/me",
            headers=auth_headers,
            json={"skill_id": 9999, "proficiency": 5},
        )
        assert response.status_code == 404

    def test_remove_skill(self, client, auth_headers, test_profile, test_skills):
        client.post(
            "/api/skills/me",
            headers=auth_headers,
            json={"skill_id": test_skills[0].id, "proficiency": 7},
        )

        response = client.delete(
            f"/api/skills/me/{test_skills[0].id}", headers=auth_headers
        )
        assert response.status_code == 204

        response = client.get("/api/students/me/skills", headers=auth_headers)
        assert len(response.json()) == 0

    def test_remove_nonexistent_skill(self, client, auth_headers, test_profile):
        response = client.delete("/api/skills/me/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_add_skill_unauthorized(self, client, test_skills):
        response = client.post(
            "/api/skills/me",
            json={"skill_id": test_skills[0].id, "proficiency": 5},
        )
        assert response.status_code == 401
