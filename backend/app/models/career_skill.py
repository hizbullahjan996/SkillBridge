from datetime import datetime

from sqlalchemy import Integer, ForeignKey, UniqueConstraint, DateTime, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CareerSkill(Base):
    __tablename__ = "career_skills"
    __table_args__ = (
        UniqueConstraint("career_id", "skill_id", name="uq_career_skill"),
        CheckConstraint("importance >= 0 AND importance <= 10", name="ck_career_skill_importance"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    importance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    career: Mapped["Career"] = relationship(back_populates="career_skills")
    skill: Mapped["Skill"] = relationship(back_populates="career_skills")

    def __repr__(self) -> str:
        return f"<CareerSkill career_id={self.career_id} skill_id={self.skill_id}>"
