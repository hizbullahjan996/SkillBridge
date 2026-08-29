"""Tests for User and StudentProfile models."""
from app.models.user import User, UserRole
from app.models.student import StudentProfile


def test_create_user(db_session):
    user = User(email="test@example.com", password_hash="hashed", role=UserRole.student)
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.student
    assert user.is_active is True


def test_user_email_unique(db_session):
    from sqlalchemy.exc import IntegrityError

    user1 = User(email="dup@example.com", password_hash="h1", role=UserRole.student)
    user2 = User(email="dup@example.com", password_hash="h2", role=UserRole.student)
    db_session.add(user1)
    db_session.commit()
    db_session.add(user2)
    try:
        db_session.commit()
        assert False, "Expected IntegrityError"
    except IntegrityError:
        db_session.rollback()


def test_admin_role(db_session):
    user = User(email="admin@example.com", password_hash="h", role=UserRole.admin)
    db_session.add(user)
    db_session.commit()
    assert user.role == UserRole.admin


def test_create_student_profile(db_session):
    user = User(email="s1@example.com", password_hash="h", role=UserRole.student)
    db_session.add(user)
    db_session.flush()

    profile = StudentProfile(
        user_id=user.id, full_name="Ali Khan", age=21, gender="Male",
        university_year="Senior", major="Computer Science", cgpa=3.5,
        attendance_percentage=90.0, study_hours_per_week=20,
        projects_completed=5, certifications_count=2, internships=1,
        communication_skills=8, teamwork=7, problem_solving=9,
        interest_domain="Data & AI",
    )
    db_session.add(profile)
    db_session.commit()

    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.full_name == "Ali Khan"
    assert profile.cgpa == 3.5


def test_student_user_relationship(db_session):
    user = User(email="rel@example.com", password_hash="h", role=UserRole.student)
    db_session.add(user)
    db_session.flush()

    profile = StudentProfile(
        user_id=user.id, full_name="Test User", age=20, gender="Female",
        university_year="Junior", major="Software Engineering", cgpa=3.8,
        attendance_percentage=85.0, study_hours_per_week=15,
        projects_completed=3, certifications_count=1, internships=0,
        communication_skills=7, teamwork=8, problem_solving=6,
        interest_domain="Web Development",
    )
    db_session.add(profile)
    db_session.commit()

    assert user.student_profile is not None
    assert user.student_profile.full_name == "Test User"


def test_cascade_delete_user_removes_profile(db_session):
    from sqlalchemy.orm import Session

    user = User(email="cascade@example.com", password_hash="h", role=UserRole.student)
    db_session.add(user)
    db_session.flush()

    profile = StudentProfile(
        user_id=user.id, full_name="Del Me", age=20, gender="Male",
        university_year="Freshman", major="CS", cgpa=3.0,
        attendance_percentage=80.0, study_hours_per_week=10,
        projects_completed=1, certifications_count=0, internships=0,
        communication_skills=5, teamwork=5, problem_solving=5,
        interest_domain="General",
    )
    db_session.add(profile)
    db_session.commit()

    db_session.delete(user)
    db_session.commit()

    remaining = db_session.query(StudentProfile).all()
    assert len(remaining) == 0
