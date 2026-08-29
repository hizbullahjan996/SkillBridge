"""Pydantic schemas for career recommendations."""
from datetime import datetime

from pydantic import BaseModel


class CareerRecommendationItem(BaseModel):
    rank: int
    career: str
    probability: float


class CareerRecommendationResponse(BaseModel):
    ready: bool
    message: str
    recommendations: list[CareerRecommendationItem]
    model_version: str | None = None
    missing_fields: list[str] = []
    missing_skills: list[str] = []


class RecommendationHistoryItem(BaseModel):
    model_version: str | None = None
    created_at: str | None = None
    recommendations: list[CareerRecommendationItem]


class RecommendationHistoryResponse(BaseModel):
    results: list[RecommendationHistoryItem]


class LatestRecommendationResponse(BaseModel):
    model_version: str | None = None
    created_at: str | None = None
    recommendations: list[CareerRecommendationItem]
