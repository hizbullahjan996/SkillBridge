"""Pydantic schemas for Learning Resources and AI Assistant."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- Learning Resource ---
class LearningResourceBase(BaseModel):
    title: str
    provider: str
    description: Optional[str] = None
    url: Optional[str] = None
    resource_type: str
    difficulty: Optional[str] = None
    is_free: bool = True


class LearningResourceCreate(LearningResourceBase):
    skill_ids: list[int] = []


class LearningResourceResponse(LearningResourceBase):
    id: int
    skills: list["ResourceSkillResponse"] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResourceSkillResponse(BaseModel):
    id: int
    name: str
    normalized_name: str

    class Config:
        from_attributes = True


class LearningResourceListResponse(BaseModel):
    items: list[LearningResourceResponse]
    total: int
    page: int
    page_size: int
    pages: int


# --- Resource Recommendation ---
class RecommendedResourceItem(BaseModel):
    resource: LearningResourceResponse
    relevance_score: float
    matched_skill: str
    skill_priority: str


class RecommendedResourcesResponse(BaseModel):
    resources: list[RecommendedResourceItem]
    total: int
    career_name: str


# --- Student Learning Resource Progress ---
class StudentLearningResourceBase(BaseModel):
    resource_id: int


class StudentLearningResourceUpdate(BaseModel):
    status: str = Field(..., pattern="^(not_started|in_progress|completed)$")


class StudentLearningResourceResponse(BaseModel):
    id: int
    resource_id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    resource: Optional[LearningResourceResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningProgressSummary(BaseModel):
    total: int
    not_started: int
    in_progress: int
    completed: int


# --- AI Assistant ---
class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[int] = None


class AssistantSource(BaseModel):
    type: str
    reference: str


class AssistantChatResponse(BaseModel):
    answer: str
    sources: list[AssistantSource] = []
    conversation_id: int


class AssistantConversationResponse(BaseModel):
    id: int
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssistantMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class AssistantConversationDetail(BaseModel):
    conversation: AssistantConversationResponse
    messages: list[AssistantMessageResponse]


# --- Roadmap with Resources ---
class RoadmapItemWithResources(BaseModel):
    step: int
    skill: str
    skill_id: int
    reason: str
    priority_score: float
    priority: str
    demand_count: int
    category: str
    resources: list[LearningResourceResponse] = []


class LearningRoadmapWithResourcesResponse(BaseModel):
    career_name: str
    total_missing: int
    roadmap: list[RoadmapItemWithResources]
