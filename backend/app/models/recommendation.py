from datetime import datetime

from sqlalchemy import Integer, Float, ForeignKey, String, DateTime, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CareerRecommendation(Base):
    __tablename__ = "career_recommendations"
    __table_args__ = (
        CheckConstraint("rank >= 1 AND rank <= 10", name="ck_recommendation_rank"),
        CheckConstraint("probability >= 0.0 AND probability <= 1.0", name="ck_recommendation_probability"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    student: Mapped["StudentProfile"] = relationship(back_populates="career_recommendations")
    career: Mapped["Career"] = relationship(back_populates="career_recommendations")

    def __repr__(self) -> str:
        return f"<CareerRecommendation student_id={self.student_id} career_id={self.career_id} rank={self.rank}>"
