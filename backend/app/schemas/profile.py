from datetime import datetime

from pydantic import BaseModel, Field


class StudentProfileUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    age: int | None = Field(None, ge=15, le=50)
    gender: str | None = Field(None, max_length=20)
    university_year: str | None = Field(None, max_length=20)
    major: str | None = Field(None, max_length=100)
    cgpa: float | None = Field(None, ge=0.0, le=4.0)
    attendance_percentage: float | None = Field(None, ge=0, le=100)
    study_hours_per_week: int | None = Field(None, ge=0, le=100)
    projects_completed: int | None = Field(None, ge=0, le=50)
    certifications_count: int | None = Field(None, ge=0, le=50)
    internships: int | None = Field(None, ge=0, le=20)
    communication_skills: int | None = Field(None, ge=0, le=10)
    teamwork: int | None = Field(None, ge=0, le=10)
    problem_solving: int | None = Field(None, ge=0, le=10)
    interest_domain: str | None = Field(None, max_length=100)


class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    age: int | None = None
    gender: str | None = None
    university_year: str | None = None
    major: str | None = None
    cgpa: float | None = None
    attendance_percentage: float | None = None
    study_hours_per_week: int | None = None
    projects_completed: int | None = None
    certifications_count: int | None = None
    internships: int | None = None
    communication_skills: int | None = None
    teamwork: int | None = None
    problem_solving: int | None = None
    interest_domain: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfileCompletionResponse(BaseModel):
    percentage: float
    completed_fields: list[str]
    missing_fields: list[str]
    total_required: int
    completed_count: int


class MLReadinessResponse(BaseModel):
    ready: bool
    missing_fields: list[str]
    missing_skills: list[str]
    profile_completion: float
    skills_count: int
