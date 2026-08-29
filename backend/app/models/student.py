from datetime import datetime

from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    __table_args__ = (
        CheckConstraint("age >= 15 AND age <= 50", name="ck_student_age"),
        CheckConstraint("cgpa >= 0.0 AND cgpa <= 4.0", name="ck_student_cgpa"),
        CheckConstraint("attendance_percentage >= 0 AND attendance_percentage <= 100", name="ck_student_attendance"),
        CheckConstraint("communication_skills >= 0 AND communication_skills <= 10", name="ck_student_communication"),
        CheckConstraint("teamwork >= 0 AND teamwork <= 10", name="ck_student_teamwork"),
        CheckConstraint("problem_solving >= 0 AND problem_solving <= 10", name="ck_student_problem_solving"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    university_year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    major: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cgpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    attendance_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    study_hours_per_week: Mapped[int | None] = mapped_column(Integer, nullable=True)
    projects_completed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    certifications_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    internships: Mapped[int | None] = mapped_column(Integer, nullable=True)
    communication_skills: Mapped[int | None] = mapped_column(Integer, nullable=True)
    teamwork: Mapped[int | None] = mapped_column(Integer, nullable=True)
    problem_solving: Mapped[int | None] = mapped_column(Integer, nullable=True)
    interest_domain: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="student_profile")
    student_skills: Mapped[list["StudentSkill"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    career_recommendations: Mapped[list["CareerRecommendation"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    skill_gap_reports: Mapped[list["SkillGapReport"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    learning_resources: Mapped[list["StudentLearningResource"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    assistant_conversations: Mapped[list["AssistantConversation"]] = relationship(back_populates="student", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<StudentProfile id={self.id} name={self.full_name}>"
