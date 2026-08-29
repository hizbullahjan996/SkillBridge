from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Career(Base):
    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    career_skills: Mapped[list["CareerSkill"]] = relationship(back_populates="career", cascade="all, delete-orphan")
    career_job_mappings: Mapped[list["CareerJobMapping"]] = relationship(back_populates="career", cascade="all, delete-orphan")
    career_recommendations: Mapped[list["CareerRecommendation"]] = relationship(back_populates="career")
    skill_gap_reports: Mapped[list["SkillGapReport"]] = relationship(back_populates="career")

    def __repr__(self) -> str:
        return f"<Career id={self.id} name={self.name}>"
