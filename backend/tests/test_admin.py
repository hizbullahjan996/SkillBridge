"""Tests for Admin service and API."""
import pytest
from app.models.user import User, UserRole
from app.models.student import StudentProfile
from app.models.skill import Skill, SkillCategory
from app.models.career import Career
from app.models.recommendation import CareerRecommendation
from app.models.job import Job
from app.models.learning_resource import LearningResource, LearningResourceSkill
from app.models.admin_audit_log import AdminAuditLog
from app.core.security import hash_password
from app.services import admin_service


@pytest.fixture
def admin_user(db_session):
    user = User(
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        role=UserRole.admin,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_user(db_session):
    user = User(
        email="student@test.com",
        password_hash=hash_password("student123"),
        role=UserRole.student,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    profile = StudentProfile(user_id=user.id, full_name="Test Student", major="CS")
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_data(db_session):
    skill = Skill(name="Python", normalized_name="python", category=SkillCategory.technical)
    db_session.add(skill)
    db_session.flush()

    career = Career(name="Data Science", normalized_name="data_science", description="DS career")
    db_session.add(career)
    db_session.flush()

    job = Job(
        job_title="Data Scientist",
        job_title_clean="data scientist",
        company="Test Corp",
        city="Lahore",
        sector="Technology",
    )
    db_session.add(job)
    db_session.flush()

    resource = LearningResource(
        title="Python Tutorial",
        provider="Python.org",
        resource_type="documentation",
        is_free=True,
    )
    db_session.add(resource)
    db_session.commit()

    return {"skill": skill, "career": career, "job": job, "resource": resource}


class TestDashboardStats:
    def test_empty_database(self, db_session):
        stats = admin_service.get_dashboard_stats(db_session)
        assert stats.users == 0
        assert stats.students == 0
        assert stats.jobs == 0
        assert stats.skills == 0

    def test_with_data(self, db_session, admin_user, student_user, sample_data):
        stats = admin_service.get_dashboard_stats(db_session)
        assert stats.users == 2
        assert stats.students == 1
        assert stats.jobs == 1
        assert stats.skills == 1
        assert stats.learning_resources == 1


class TestUserManagement:
    def test_list_users(self, db_session, admin_user, student_user):
        result = admin_service.list_users(db_session)
        assert result.total == 2
        assert len(result.items) == 2

    def test_search_users(self, db_session, admin_user, student_user):
        result = admin_service.list_users(db_session, search="admin")
        assert result.total == 1
        assert result.items[0].email == "admin@test.com"

    def test_filter_by_role(self, db_session, admin_user, student_user):
        result = admin_service.list_users(db_session, role="admin")
        assert result.total == 1

    def test_get_user_detail(self, db_session, admin_user, student_user):
        result = admin_service.get_user_detail(db_session, student_user.id)
        assert result is not None
        assert result["email"] == "student@test.com"
        assert result["student_profile"] is not None

    def test_get_user_not_found(self, db_session):
        result = admin_service.get_user_detail(db_session, 9999)
        assert result is None


class TestStudentManagement:
    def test_list_students(self, db_session, student_user):
        result = admin_service.list_students(db_session)
        assert result.total == 1
        assert result.items[0].full_name == "Test Student"

    def test_search_students(self, db_session, student_user):
        result = admin_service.list_students(db_session, search="Test")
        assert result.total == 1

    def test_get_student_detail(self, db_session, student_user):
        result = admin_service.get_student_detail(db_session, student_user.student_profile.id)
        assert result is not None
        assert result["full_name"] == "Test Student"

    def test_get_student_not_found(self, db_session):
        result = admin_service.get_student_detail(db_session, 9999)
        assert result is None


class TestSkillAnalytics:
    def test_list_skills(self, db_session, sample_data):
        result = admin_service.list_skills_analytics(db_session)
        assert result.total == 1
        assert result.items[0].skill_name == "Python"

    def test_search_skills(self, db_session, sample_data):
        result = admin_service.list_skills_analytics(db_session, search="Python")
        assert result.total == 1


class TestCareerAnalytics:
    def test_list_careers(self, db_session, sample_data):
        items = admin_service.list_careers_analytics(db_session)
        assert len(items) == 1
        assert items[0].career_name == "Data Science"


class TestJobAnalytics:
    def test_get_job_analytics(self, db_session, sample_data):
        analytics = admin_service.get_job_analytics(db_session)
        assert analytics.total_jobs == 1
        assert len(analytics.top_cities) == 1
        assert analytics.top_cities[0]["name"] == "Lahore"


class TestLearningAnalytics:
    def test_get_learning_analytics(self, db_session, sample_data):
        analytics = admin_service.get_learning_analytics(db_session)
        assert analytics.total_resources == 1
        assert analytics.completion_rate == 0.0


class TestAIAnalytics:
    def test_get_ai_analytics(self, db_session):
        analytics = admin_service.get_ai_analytics(db_session)
        assert analytics.total_conversations == 0
        assert analytics.total_messages == 0


class TestSystemHealth:
    def test_get_system_health(self, db_session):
        health = admin_service.get_system_health(db_session)
        assert health.api_status == "healthy"
        assert health.database_status == "healthy"


class TestAuditLog:
    def test_create_audit_log(self, db_session, admin_user):
        log = admin_service.create_audit_log(
            db_session, admin_user.id, "test_action", "user", 1
        )
        assert log.action == "test_action"
        assert log.resource_type == "user"
        assert log.resource_id == 1

    def test_list_audit_logs(self, db_session, admin_user):
        admin_service.create_audit_log(db_session, admin_user.id, "action1")
        admin_service.create_audit_log(db_session, admin_user.id, "action2")
        result = admin_service.list_audit_logs(db_session)
        assert result["total"] == 2


class TestAdminAPIAuthorization:
    def test_unauthenticated_returns_401(self, client):
        response = client.get("/api/admin/dashboard")
        assert response.status_code == 401

    def test_student_returns_403(self, client, db_session):
        from app.core.jwt import create_access_token
        from app.core.security import hash_password

        user = User(
            email="student_api@test.com",
            password_hash=hash_password("student123"),
            role=UserRole.student,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()
        profile = StudentProfile(user_id=user.id, full_name="API Student", major="CS")
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(user)

        token = create_access_token(data={"sub": user.id})
        response = client.get(
            "/api/admin/dashboard",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_admin_can_access_dashboard(self, client, db_session):
        from app.core.jwt import create_access_token
        from app.core.security import hash_password

        user = User(
            email="admin_api@test.com",
            password_hash=hash_password("admin123"),
            role=UserRole.admin,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        token = create_access_token(data={"sub": user.id})
        response = client.get(
            "/api/admin/dashboard",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert "users" in response.json()

    def test_admin_can_access_users(self, client, db_session):
        from app.core.jwt import create_access_token
        from app.core.security import hash_password

        user = User(
            email="admin_users@test.com",
            password_hash=hash_password("admin123"),
            role=UserRole.admin,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        token = create_access_token(data={"sub": user.id})
        response = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert "items" in response.json()

    def test_admin_can_access_system_health(self, client, db_session):
        from app.core.jwt import create_access_token
        from app.core.security import hash_password

        user = User(
            email="admin_health@test.com",
            password_hash=hash_password("admin123"),
            role=UserRole.admin,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        token = create_access_token(data={"sub": user.id})
        response = client.get(
            "/api/admin/system/health",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert "api_status" in response.json()
