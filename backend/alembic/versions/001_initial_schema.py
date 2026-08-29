"""initial_schema

Revision ID: 001_initial
Revises:
Create Date: 2026-08-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("student", "admin", name="userrole"), nullable=False, server_default="student"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "student_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", sa.String(20), nullable=False),
        sa.Column("university_year", sa.String(20), nullable=False),
        sa.Column("major", sa.String(100), nullable=False),
        sa.Column("cgpa", sa.Float(), nullable=False),
        sa.Column("attendance_percentage", sa.Float(), nullable=False),
        sa.Column("study_hours_per_week", sa.Integer(), nullable=False),
        sa.Column("projects_completed", sa.Integer(), nullable=False),
        sa.Column("certifications_count", sa.Integer(), nullable=False),
        sa.Column("internships", sa.Integer(), nullable=False),
        sa.Column("communication_skills", sa.Integer(), nullable=False),
        sa.Column("teamwork", sa.Integer(), nullable=False),
        sa.Column("problem_solving", sa.Integer(), nullable=False),
        sa.Column("interest_domain", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("age >= 15 AND age <= 50", name="ck_student_age"),
        sa.CheckConstraint("cgpa >= 0.0 AND cgpa <= 4.0", name="ck_student_cgpa"),
        sa.CheckConstraint("attendance_percentage >= 0 AND attendance_percentage <= 100", name="ck_student_attendance"),
        sa.CheckConstraint("communication_skills >= 0 AND communication_skills <= 10", name="ck_student_communication"),
        sa.CheckConstraint("teamwork >= 0 AND teamwork <= 10", name="ck_student_teamwork"),
        sa.CheckConstraint("problem_solving >= 0 AND problem_solving <= 10", name="ck_student_problem_solving"),
    )

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("normalized_name", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("category", sa.Enum("technical", "soft", name="skillcategory"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "student_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("proficiency", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("student_id", "skill_id", name="uq_student_skill"),
        sa.CheckConstraint("proficiency >= 0 AND proficiency <= 10", name="ck_student_skill_proficiency"),
    )

    op.create_table(
        "careers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("normalized_name", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "career_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("career_id", sa.Integer(), sa.ForeignKey("careers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("importance", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("career_id", "skill_id", name="uq_career_skill"),
        sa.CheckConstraint("importance >= 0 AND importance <= 10", name="ck_career_skill_importance"),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_title", sa.String(255), nullable=False, index=True),
        sa.Column("job_title_clean", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("city", sa.String(100), nullable=False, index=True),
        sa.Column("sector", sa.String(100), nullable=False, index=True),
        sa.Column("salary_min", sa.Float(), nullable=True),
        sa.Column("salary_max", sa.Float(), nullable=True),
        sa.Column("salary_average", sa.Float(), nullable=True),
        sa.Column("experience_min_years", sa.Float(), nullable=True),
        sa.Column("experience_max_years", sa.Float(), nullable=True),
        sa.Column("experience_required_raw", sa.String(50), nullable=True),
        sa.Column("education_level", sa.String(50), nullable=True),
        sa.Column("job_type", sa.String(20), nullable=True),
        sa.Column("gender_preference", sa.String(30), nullable=True),
        sa.Column("number_of_vacancies", sa.Integer(), nullable=True),
        sa.Column("posted_date", sa.Date(), nullable=True),
        sa.Column("application_deadline", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("salary_min >= 0", name="ck_job_salary_min"),
        sa.CheckConstraint("salary_max >= 0", name="ck_job_salary_max"),
        sa.CheckConstraint("experience_min_years >= 0", name="ck_job_exp_min"),
    )

    op.create_table(
        "job_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("importance", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),
        sa.CheckConstraint("importance >= 0 AND importance <= 10", name="ck_job_skill_importance"),
    )

    op.create_table(
        "career_job_mappings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("career_id", sa.Integer(), sa.ForeignKey("careers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_title_clean", sa.String(255), nullable=False, index=True),
        sa.Column("mapping_type", sa.Enum("strong", "moderate", "weak", name="mappingtype"), nullable=False),
        sa.Column("confidence", sa.String(20), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "career_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("career_id", sa.Integer(), sa.ForeignKey("careers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("probability", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("rank >= 1 AND rank <= 10", name="ck_recommendation_rank"),
        sa.CheckConstraint("probability >= 0.0 AND probability <= 1.0", name="ck_recommendation_probability"),
    )

    op.create_table(
        "skill_gap_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("career_id", sa.Integer(), sa.ForeignKey("careers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("match_percentage", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("match_percentage >= 0 AND match_percentage <= 100", name="ck_gap_match_percentage"),
    )

    op.create_table(
        "skill_gap_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("report_id", sa.Integer(), sa.ForeignKey("skill_gap_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.Enum("matched", "missing", name="gapitemstatus"), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("skill_gap_items")
    op.drop_table("skill_gap_reports")
    op.drop_table("career_recommendations")
    op.drop_table("career_job_mappings")
    op.drop_table("job_skills")
    op.drop_table("jobs")
    op.drop_table("career_skills")
    op.drop_table("careers")
    op.drop_table("student_skills")
    op.drop_table("skills")
    op.drop_table("student_profiles")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS gapitemstatus")
    op.execute("DROP TYPE IF EXISTS mappingtype")
    op.execute("DROP TYPE IF EXISTS skillcategory")
    op.execute("DROP TYPE IF EXISTS userrole")
