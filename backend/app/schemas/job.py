"""Pydantic schemas for jobs."""
from datetime import date, datetime

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: int
    job_title: str
    job_title_clean: str
    company: str
    city: str
    sector: str
    salary_min: float | None = None
    salary_max: float | None = None
    salary_average: float | None = None
    experience_min_years: float | None = None
    experience_max_years: float | None = None
    experience_required_raw: str | None = None
    education_level: str | None = None
    job_type: str | None = None
    gender_preference: str | None = None
    number_of_vacancies: int | None = None
    posted_date: date | None = None
    application_deadline: date | None = None

    model_config = {"from_attributes": True}


class JobSkillResponse(BaseModel):
    skill_name: str
    normalized_name: str


class JobDetailResponse(JobResponse):
    required_skills: list[JobSkillResponse] = []


class JobListItem(BaseModel):
    job_id: int
    job_title: str
    company: str
    city: str
    sector: str
    job_type: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_average: float | None = None
    education_level: str | None = None
    experience_required: str | None = None
    match_score: float | None = None
    skill_match_percentage: float | None = None
    career_score: float | None = None
    education_score: float | None = None
    experience_score: float | None = None
    matched_skills: int | None = None
    total_required_skills: int | None = None
    in_top_career: bool | None = None


class JobListResponse(BaseModel):
    items: list[JobListItem]
    total: int
    page: int
    page_size: int
    pages: int


class JobSearchFilters(BaseModel):
    city: str | None = None
    sector: str | None = None
    job_type: str | None = None
    education_level: str | None = None
    search: str | None = None
    page: int = 1
    page_size: int = 20
