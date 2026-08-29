from datetime import datetime

from pydantic import BaseModel, Field


class SkillResponse(BaseModel):
    id: int
    name: str
    normalized_name: str
    category: str

    model_config = {"from_attributes": True}


class StudentSkillCreate(BaseModel):
    skill_id: int
    proficiency: int = Field(ge=0, le=10, default=5)


class StudentSkillResponse(BaseModel):
    id: int
    student_id: int
    skill_id: int
    proficiency: int
    skill: SkillResponse | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentSkillUpdate(BaseModel):
    proficiency: int = Field(ge=0, le=10)


class StudentSkillsBulkUpdate(BaseModel):
    skills: list[StudentSkillCreate]
