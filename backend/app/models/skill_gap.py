import enum
from datetime import datetime

from sqlalchemy import Integer, Float, ForeignKey, String, Enum, DateTime, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class GapItemStatus(str, enum.Enum):
    matched = "matched"
    missing = "missing"


class SkillGapReport(Base):
    __tablename__ = "skill_gap_reports"
    __table_args__ = (
        CheckConstraint("match_percentage >= 0 AND match_percentage <= 100", name="ck_gap_match_percentage"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    match_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    student: Mapped["StudentProfile"] = relationship(back_populates="skill_gap_reports")
    career: Mapped["Career"] = relationship(back_populates="skill_gap_reports")
    job: Mapped["Job | None"] = relationship(back_populates="skill_gap_reports")
    items: Mapped[list["SkillGapItem"]] = relationship(back_populates="report", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SkillGapReport id={self.id} student_id={self.student_id} match={self.match_percentage}%>"


class SkillGapItem(Base):
    __tablename__ = "skill_gap_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("skill_gap_reports.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[GapItemStatus] = mapped_column(Enum(GapItemStatus), nullable=False)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    report: Mapped["SkillGapReport"] = relationship(back_populates="items")
    skill: Mapped["Skill"] = relationship(back_populates="skill_gap_items")

    def __repr__(self) -> str:
        return f"<SkillGapItem report_id={self.report_id} skill_id={self.skill_id} status={self.status}>"
