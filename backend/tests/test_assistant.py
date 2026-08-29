"""Tests for AI Career Assistant."""
import pytest
from unittest.mock import patch, MagicMock

from app.models.user import User, UserRole
from app.models.skill import Skill, SkillCategory
from app.models.student_skill import StudentSkill
from app.core.security import hash_password
from app.services import ai_career_assistant


@pytest.fixture
def student_user(db_session):
    user = User(
        email="assistant@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.student,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    from app.models.student import StudentProfile
    profile = StudentProfile(
        user_id=user.id,
        full_name="Test Student",
        major="Computer Science",
        cgpa=3.5,
        university_year="3rd Year",
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def skill_with_resources(db_session):
    skill = Skill(name="Python", normalized_name="python", category=SkillCategory.technical)
    db_session.add(skill)
    db_session.commit()
    db_session.refresh(skill)
    return skill


class TestBuildContext:
    def test_build_context_no_profile(self, db_session):
        ctx = ai_career_assistant.build_context(db_session, 9999)
        assert ctx.profile is None
        assert ctx.skills == []

    def test_build_context_with_profile(self, db_session, student_user):
        ctx = ai_career_assistant.build_context(db_session, student_user.student_profile.id)
        assert ctx.profile is not None
        assert ctx.profile["full_name"] == "Test Student"

    def test_build_context_with_skills(self, db_session, student_user, skill_with_resources):
        ss = StudentSkill(student_id=student_user.student_profile.id, skill_id=skill_with_resources.id, proficiency=7)
        db_session.add(ss)
        db_session.commit()

        ctx = ai_career_assistant.build_context(db_session, student_user.student_profile.id)
        assert len(ctx.skills) == 1
        assert ctx.skills[0]["name"] == "Python"


class TestFormatContext:
    def test_format_empty_context(self):
        from app.services.ai_career_assistant import AssistantContext
        ctx = AssistantContext()
        result = ai_career_assistant.format_context_for_llm(ctx)
        assert result == ""

    def test_format_with_profile(self):
        from app.services.ai_career_assistant import AssistantContext
        ctx = AssistantContext(profile={"full_name": "Test", "major": "CS"})
        result = ai_career_assistant.format_context_for_llm(ctx)
        assert "Test" in result
        assert "CS" in result


class TestValidateResponse:
    def test_empty_response(self):
        from app.services.ai_career_assistant import AssistantContext
        ctx = AssistantContext()
        result = ai_career_assistant.validate_response("", ctx)
        assert "sorry" in result.lower() or "couldn't" in result.lower()

    def test_normal_response(self):
        from app.services.ai_career_assistant import AssistantContext
        ctx = AssistantContext()
        result = ai_career_assistant.validate_response("Hello, how can I help?", ctx)
        assert result == "Hello, how can I help?"

    def test_long_response_truncated(self):
        from app.services.ai_career_assistant import AssistantContext
        ctx = AssistantContext()
        long_text = "A" * 4000
        result = ai_career_assistant.validate_response(long_text, ctx)
        assert len(result) < 4000

    def test_dangerous_content_sanitized(self):
        from app.services.ai_career_assistant import AssistantContext
        ctx = AssistantContext()
        result = ai_career_assistant.validate_response("Here is the api_key: secret123", ctx)
        assert "api_key" not in result.lower()


class TestExtractSources:
    def test_skill_sources(self):
        from app.services.ai_career_assistant import AssistantContext
        ctx = AssistantContext()
        sources = ai_career_assistant.extract_sources_from_message("What skills should I learn?", ctx)
        assert any(s.type == "skills" for s in sources)

    def test_career_sources(self):
        from app.services.ai_career_assistant import AssistantContext
        ctx = AssistantContext()
        sources = ai_career_assistant.extract_sources_from_message("Which career matches me?", ctx)
        assert any(s.type == "career_recommendations" for s in sources)

    def test_gap_sources(self):
        from app.services.ai_career_assistant import AssistantContext
        ctx = AssistantContext()
        sources = ai_career_assistant.extract_sources_from_message("What skills am I missing?", ctx)
        assert any(s.type == "skill_gap" for s in sources)

    def test_fallback_to_context_sources(self):
        from app.services.ai_career_assistant import AssistantContext, AssistantSource
        ctx = AssistantContext(sources=[AssistantSource(type="test", reference="test ref")])
        sources = ai_career_assistant.extract_sources_from_message("random question", ctx)
        assert len(sources) > 0


class TestChatAPI:
    def test_unauthenticated_returns_401(self, client):
        response = client.post("/api/assistant/chat", json={"message": "Hello"})
        assert response.status_code == 401

    def test_empty_message_rejected(self, client, db_session):
        user = User(
            email="empty@test.com",
            password_hash=hash_password("password123"),
            role=UserRole.student,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()
        from app.models.student import StudentProfile
        profile = StudentProfile(user_id=user.id, full_name="Empty Test")
        db_session.add(profile)
        db_session.commit()

        from app.core.jwt import create_access_token
        token = create_access_token(data={"sub": user.id})
        response = client.post(
            "/api/assistant/chat",
            json={"message": ""},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422

    def test_llm_failure_handled(self, client, db_session):
        user = User(
            email="llmfail@test.com",
            password_hash=hash_password("password123"),
            role=UserRole.student,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()
        from app.models.student import StudentProfile
        profile = StudentProfile(user_id=user.id, full_name="LLM Fail Test")
        db_session.add(profile)
        db_session.commit()

        from app.core.jwt import create_access_token
        token = create_access_token(data={"sub": user.id})

        with patch("app.services.ai_career_assistant.get_llm_provider") as mock_provider:
            mock_llm = MagicMock()
            mock_llm.generate.side_effect = Exception("LLM unavailable")
            mock_provider.return_value = mock_llm

            response = client.post(
                "/api/assistant/chat",
                json={"message": "Hello"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200
            data = response.json()
            assert "unavailable" in data["answer"].lower() or "sorry" in data["answer"].lower()


class TestConversationSecurity:
    def test_user_cannot_read_other_conversation(self, client, db_session):
        user1 = User(
            email="user1@test.com",
            password_hash=hash_password("password123"),
            role=UserRole.student,
            is_active=True,
        )
        user2 = User(
            email="user2@test.com",
            password_hash=hash_password("password123"),
            role=UserRole.student,
            is_active=True,
        )
        db_session.add_all([user1, user2])
        db_session.flush()

        from app.models.student import StudentProfile
        from app.models.assistant import AssistantConversation, AssistantMessage

        profile1 = StudentProfile(user_id=user1.id, full_name="User 1")
        profile2 = StudentProfile(user_id=user2.id, full_name="User 2")
        db_session.add_all([profile1, profile2])
        db_session.flush()

        conv = AssistantConversation(student_id=profile1.id, title="Private")
        db_session.add(conv)
        db_session.flush()

        msg = AssistantMessage(conversation_id=conv.id, role="user", content="Secret")
        db_session.add(msg)
        db_session.commit()

        from app.core.jwt import create_access_token
        token2 = create_access_token(data={"sub": user2.id})
        response = client.get(
            f"/api/assistant/conversations/{conv.id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 404
