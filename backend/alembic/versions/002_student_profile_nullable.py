"""make_student_profile_fields_nullable

Revision ID: 002_student_profile_nullable
Revises: 001_initial
Create Date: 2026-08-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_student_profile_nullable"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("student_profiles", "age", nullable=True)
    op.alter_column("student_profiles", "gender", nullable=True)
    op.alter_column("student_profiles", "university_year", nullable=True)
    op.alter_column("student_profiles", "major", nullable=True)
    op.alter_column("student_profiles", "cgpa", nullable=True)
    op.alter_column("student_profiles", "attendance_percentage", nullable=True)
    op.alter_column("student_profiles", "study_hours_per_week", nullable=True)
    op.alter_column("student_profiles", "projects_completed", nullable=True)
    op.alter_column("student_profiles", "certifications_count", nullable=True)
    op.alter_column("student_profiles", "internships", nullable=True)
    op.alter_column("student_profiles", "communication_skills", nullable=True)
    op.alter_column("student_profiles", "teamwork", nullable=True)
    op.alter_column("student_profiles", "problem_solving", nullable=True)
    op.alter_column("student_profiles", "interest_domain", nullable=True)


def downgrade() -> None:
    op.alter_column("student_profiles", "interest_domain", nullable=False)
    op.alter_column("student_profiles", "problem_solving", nullable=False)
    op.alter_column("student_profiles", "teamwork", nullable=False)
    op.alter_column("student_profiles", "communication_skills", nullable=False)
    op.alter_column("student_profiles", "internships", nullable=False)
    op.alter_column("student_profiles", "certifications_count", nullable=False)
    op.alter_column("student_profiles", "projects_completed", nullable=False)
    op.alter_column("student_profiles", "study_hours_per_week", nullable=False)
    op.alter_column("student_profiles", "attendance_percentage", nullable=False)
    op.alter_column("student_profiles", "cgpa", nullable=False)
    op.alter_column("student_profiles", "major", nullable=False)
    op.alter_column("student_profiles", "university_year", nullable=False)
    op.alter_column("student_profiles", "gender", nullable=False)
    op.alter_column("student_profiles", "age", nullable=False)
