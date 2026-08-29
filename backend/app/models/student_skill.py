from datetime import datetime

from sqlalchemy import Integer, ForeignKey, UniqueConstraint, DateTime, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class StudentSkill(Base):
    __tablename__ = "student_skills"
    __table_args__ = (
        UniqueConstraint("student_id", "skill_id", name="uq_student_skill"),
        CheckConstraint("proficiency >= 0 AND proficiency <= 10", name="ck_student_skill_proficiency"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    student: Mapped["StudentProfile"] = relationship(back_populates="student_skills")
    skill: Mapped["Skill"] = relationship(back_populates="student_skills")

    def __repr__(self) -> str:
        return f"<StudentSkill student_id={self.student_id} skill_id={self.skill_id} proficiency={self.proficiency}>"
