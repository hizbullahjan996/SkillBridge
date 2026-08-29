"""Tests for Skill, Career, and relationship models."""
from app.models.skill import Skill, SkillCategory
from app.models.student_skill import StudentSkill
from app.models.career import Career
from app.models.career_skill import CareerSkill
from app.models.student import StudentProfile
from app.models.user import User, UserRole


def _make_user_profile(db_session):
    user = User(email="skill_test@example.com", password_hash="h", role=UserRole.student)
    db_session.add(user)
    db_session.flush()
    profile = StudentProfile(
        user_id=user.id, full_name="S", age=20, gender="M",
        university_year="Senior", major="CS", cgpa=3.0,
        attendance_percentage=90, study_hours_per_week=10,
        projects_completed=1, certifications_count=0, internships=0,
        communication_skills=5, teamwork=5, problem_solving=5,
        interest_domain="General",
    )
    db_session.add(profile)
    db_session.flush()
    return profile


def test_create_skill(db_session):
    skill = Skill(name="Python", normalized_name="python", category=SkillCategory.technical)
    db_session.add(skill)
    db_session.commit()
    assert skill.id is not None
    assert skill.name == "Python"


def test_skill_normalized_unique(db_session):
    from sqlalchemy.exc import IntegrityError

    s1 = Skill(name="Python", normalized_name="python", category=SkillCategory.technical)
    s2 = Skill(name="Python2", normalized_name="python", category=SkillCategory.technical)
    db_session.add(s1)
    db_session.commit()
    db_session.add(s2)
    try:
        db_session.commit()
        assert False, "Expected IntegrityError"
    except IntegrityError:
        db_session.rollback()


def test_soft_skill_category(db_session):
    skill = Skill(name="Teamwork", normalized_name="teamwork", category=SkillCategory.soft)
    db_session.add(skill)
    db_session.commit()
    assert skill.category == SkillCategory.soft


def test_student_skill_relationship(db_session):
    profile = _make_user_profile(db_session)
    skill = Skill(name="SQL", normalized_name="sql", category=SkillCategory.technical)
    db_session.add(skill)
    db_session.flush()

    ss = StudentSkill(student_id=profile.id, skill_id=skill.id, proficiency=7)
    db_session.add(ss)
    db_session.commit()

    assert ss.id is not None
    assert ss.proficiency == 7
    assert len(profile.student_skills) == 1
    assert profile.student_skills[0].skill.name == "SQL"


def test_student_skill_unique_constraint(db_session):
    from sqlalchemy.exc import IntegrityError

    profile = _make_user_profile(db_session)
    skill = Skill(name="React", normalized_name="react", category=SkillCategory.technical)
    db_session.add(skill)
    db_session.flush()

    ss1 = StudentSkill(student_id=profile.id, skill_id=skill.id, proficiency=5)
    ss2 = StudentSkill(student_id=profile.id, skill_id=skill.id, proficiency=8)
    db_session.add(ss1)
    db_session.commit()
    db_session.add(ss2)
    try:
        db_session.commit()
        assert False, "Expected IntegrityError for duplicate student+skill"
    except IntegrityError:
        db_session.rollback()


def test_create_career(db_session):
    career = Career(name="Data Analyst", normalized_name="data_analyst", description="Analyzes data")
    db_session.add(career)
    db_session.commit()
    assert career.id is not None
    assert career.name == "Data Analyst"


def test_career_skill_relationship(db_session):
    career = Career(name="AI Engineer", normalized_name="ai_engineer")
    skill = Skill(name="Python", normalized_name="python", category=SkillCategory.technical)
    db_session.add_all([career, skill])
    db_session.flush()

    cs = CareerSkill(career_id=career.id, skill_id=skill.id, importance=9)
    db_session.add(cs)
    db_session.commit()

    assert cs.id is not None
    assert len(career.career_skills) == 1
    assert career.career_skills[0].skill.name == "Python"


def test_career_job_mapping(db_session):
    from app.models.career_job_mapping import CareerJobMapping, MappingType

    career = Career(name="Backend Dev", normalized_name="backend_dev")
    db_session.add(career)
    db_session.flush()

    mapping = CareerJobMapping(
        career_id=career.id,
        job_title_clean="Backend Developer",
        mapping_type=MappingType.strong,
        confidence="High",
        notes="Exact match",
    )
    db_session.add(mapping)
    db_session.commit()

    assert mapping.id is not None
    assert mapping.mapping_type == MappingType.strong
    assert len(career.career_job_mappings) == 1
