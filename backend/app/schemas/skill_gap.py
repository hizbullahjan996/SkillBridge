"""Pydantic schemas for Skill Gap and Learning Roadmap."""
from pydantic import BaseModel


class SkillGapMatchedSkill(BaseModel):
    id: int
    name: str
    normalized_name: str
    category: str


class SkillGapMissingSkill(BaseModel):
    skill_id: int
    skill_name: str
    normalized_name: str
    category: str
    priority_score: float
    priority: str
    demand_count: int
    career_relevance_count: int
    avg_importance: float


class SkillGapSummary(BaseModel):
    matched_count: int
    missing_count: int
    match_percentage: float
    total_required: int


class CareerSkillGapResponse(BaseModel):
    career: dict
    skill_gap: SkillGapSummary
    matched_skills: list[SkillGapMatchedSkill]
    missing_skills: list[SkillGapMissingSkill]


class JobSkillGapResponse(BaseModel):
    job: dict
    skill_gap: SkillGapSummary
    matched_skills: list[SkillGapMatchedSkill]
    missing_skills: list[SkillGapMissingSkill]


class RoadmapItemResponse(BaseModel):
    step: int
    skill: str
    skill_id: int
    reason: str
    priority_score: float
    priority: str
    demand_count: int
    category: str


class LearningRoadmapResponse(BaseModel):
    career_name: str
    total_missing: int
    roadmap: list[RoadmapItemResponse]


class NoRoadmapResponse(BaseModel):
    message: str
    detail: str
