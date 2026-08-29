import enum
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SkillCategory(str, enum.Enum):
    technical = "technical"
    soft = "soft"


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[SkillCategory] = mapped_column(Enum(SkillCategory), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    student_skills: Mapped[list["StudentSkill"]] = relationship(back_populates="skill")
    career_skills: Mapped[list["CareerSkill"]] = relationship(back_populates="skill")
    job_skills: Mapped[list["JobSkill"]] = relationship(back_populates="skill")
    skill_gap_items: Mapped[list["SkillGapItem"]] = relationship(back_populates="skill")
    resource_skills: Mapped[list["LearningResourceSkill"]] = relationship(back_populates="skill")

    def __repr__(self) -> str:
        return f"<Skill id={self.id} name={self.name}>"
