"""Tests for Learning Resources API and service."""
import pytest
from app.models.skill import Skill, SkillCategory
from app.models.learning_resource import LearningResource, LearningResourceSkill
from app.models.student_skill import StudentSkill
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.services import learning_resource_service as resource_svc


@pytest.fixture
def student_user(db_session):
    user = User(
        email="resource@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.student,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    from app.models.student import StudentProfile
    profile = StudentProfile(user_id=user.id, full_name="Resource Test Student")
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_skill(db_session):
    skill = Skill(name="Python", normalized_name="python", category=SkillCategory.technical)
    db_session.add(skill)
    db_session.commit()
    db_session.refresh(skill)
    return skill


@pytest.fixture
def sample_resource(db_session, sample_skill):
    resource = LearningResource(
        title="Official Python Tutorial",
        provider="Python.org",
        description="Comprehensive Python tutorial",
        url="https://docs.python.org/3/tutorial/",
        resource_type="documentation",
        difficulty="beginner",
        is_free=True,
    )
    db_session.add(resource)
    db_session.flush()
    link = LearningResourceSkill(resource_id=resource.id, skill_id=sample_skill.id)
    db_session.add(link)
    db_session.commit()
    db_session.refresh(resource)
    return resource


class TestResourceSearch:
    def test_search_returns_all(self, db_session, sample_resource):
        result = resource_svc.search_resources(db_session)
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].title == "Official Python Tutorial"

    def test_search_by_skill(self, db_session, sample_resource):
        result = resource_svc.search_resources(db_session, skill_name="python")
        assert result.total == 1

    def test_search_by_type(self, db_session, sample_resource):
        result = resource_svc.search_resources(db_session, resource_type="documentation")
        assert result.total == 1

    def test_search_by_difficulty(self, db_session, sample_resource):
        result = resource_svc.search_resources(db_session, difficulty="beginner")
        assert result.total == 1

    def test_search_by_free(self, db_session, sample_resource):
        result = resource_svc.search_resources(db_session, is_free=True)
        assert result.total == 1

    def test_search_by_text(self, db_session, sample_resource):
        result = resource_svc.search_resources(db_session, search="Python")
        assert result.total == 1

    def test_search_no_match(self, db_session, sample_resource):
        result = resource_svc.search_resources(db_session, search="Nonexistent")
        assert result.total == 0

    def test_pagination(self, db_session, sample_resource):
        result = resource_svc.search_resources(db_session, page=1, page_size=5)
        assert result.page == 1
        assert result.page_size == 5
        assert result.pages == 1


class TestResourceById:
    def test_get_by_id(self, db_session, sample_resource):
        result = resource_svc.get_resource_by_id(db_session, sample_resource.id)
        assert result is not None
        assert result.title == "Official Python Tutorial"
        assert len(result.skills) == 1

    def test_get_by_id_not_found(self, db_session):
        result = resource_svc.get_resource_by_id(db_session, 9999)
        assert result is None


class TestRecommendedResources:
    def test_empty_missing_skills(self, db_session):
        result = resource_svc.get_recommended_resources(db_session, 1, [])
        assert result == []

    def test_recommended_for_missing_skill(self, db_session, sample_resource, sample_skill):
        missing = [{"skill_id": sample_skill.id, "skill_name": "Python", "priority": "High", "priority_score": 80.0}]
        result = resource_svc.get_recommended_resources(db_session, 1, missing)
        assert len(result) == 1
        assert result[0]["matched_skill"] == "Python"

    def test_recommended_excludes_matched_skills(self, db_session, sample_resource, sample_skill):
        missing = [{"skill_id": 9999, "skill_name": "Java", "priority": "High", "priority_score": 80.0}]
        result = resource_svc.get_recommended_resources(db_session, 1, missing)
        assert len(result) == 0


class TestStudentProgress:
    def test_get_empty_progress(self, db_session, student_user):
        result = resource_svc.get_student_progress(db_session, student_user.student_profile.id)
        assert result == []

    def test_upsert_creates_record(self, db_session, sample_resource, student_user):
        record = resource_svc.upsert_student_resource_progress(
            db_session, student_user.student_profile.id, sample_resource.id, "in_progress"
        )
        assert record is not None
        assert record.status == "in_progress"
        assert record.started_at is not None

    def test_upsert_updates_record(self, db_session, sample_resource, student_user):
        resource_svc.upsert_student_resource_progress(
            db_session, student_user.student_profile.id, sample_resource.id, "in_progress"
        )
        updated = resource_svc.upsert_student_resource_progress(
            db_session, student_user.student_profile.id, sample_resource.id, "completed"
        )
        assert updated.status == "completed"
        assert updated.completed_at is not None

    def test_progress_summary(self, db_session, sample_resource, student_user):
        resource_svc.upsert_student_resource_progress(
            db_session, student_user.student_profile.id, sample_resource.id, "completed"
        )
        summary = resource_svc.get_progress_summary(db_session, student_user.student_profile.id)
        assert summary["total"] == 1
        assert summary["completed"] == 1


class TestResourcesForSkills:
    def test_empty_skill_ids(self, db_session):
        result = resource_svc.get_resources_for_skills(db_session, [])
        assert result == {}

    def test_returns_resources_for_skill(self, db_session, sample_resource, sample_skill):
        result = resource_svc.get_resources_for_skills(db_session, [sample_skill.id])
        assert sample_skill.id in result
        assert len(result[sample_skill.id]) == 1
