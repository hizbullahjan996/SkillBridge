from datetime import datetime, date

from sqlalchemy import String, Float, Integer, DateTime, Date, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint("salary_min >= 0", name="ck_job_salary_min"),
        CheckConstraint("salary_max >= 0", name="ck_job_salary_max"),
        CheckConstraint("experience_min_years >= 0", name="ck_job_exp_min"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    job_title_clean: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    sector: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_average: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_min_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_max_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_required_raw: Mapped[str | None] = mapped_column(String(50), nullable=True)
    education_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    job_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    gender_preference: Mapped[str | None] = mapped_column(String(30), nullable=True)
    number_of_vacancies: Mapped[int | None] = mapped_column(Integer, nullable=True)
    posted_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    application_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    job_skills: Mapped[list["JobSkill"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    skill_gap_reports: Mapped[list["SkillGapReport"]] = relationship(back_populates="job")

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.job_title} company={self.company}>"
