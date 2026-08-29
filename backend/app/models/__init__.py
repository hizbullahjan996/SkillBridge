from app.models.base import Base
from app.models.user import User, UserRole
from app.models.student import StudentProfile
from app.models.skill import Skill, SkillCategory
from app.models.student_skill import StudentSkill
from app.models.career import Career
from app.models.career_skill import CareerSkill
from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.career_job_mapping import CareerJobMapping, MappingType
from app.models.recommendation import CareerRecommendation
from app.models.skill_gap import SkillGapReport, SkillGapItem, GapItemStatus
from app.models.learning_resource import LearningResource, LearningResourceSkill, ResourceType, ResourceDifficulty
from app.models.student_learning_resource import StudentLearningResource, ResourceProgressStatus
from app.models.assistant import AssistantConversation, AssistantMessage
from app.models.admin_audit_log import AdminAuditLog

__all__ = [
    "Base",
    "User",
    "UserRole",
    "StudentProfile",
    "Skill",
    "SkillCategory",
    "StudentSkill",
    "Career",
    "CareerSkill",
    "Job",
    "JobSkill",
    "CareerJobMapping",
    "MappingType",
    "CareerRecommendation",
    "SkillGapReport",
    "SkillGapItem",
    "GapItemStatus",
    "LearningResource",
    "LearningResourceSkill",
    "ResourceType",
    "ResourceDifficulty",
    "StudentLearningResource",
    "ResourceProgressStatus",
    "AssistantConversation",
    "AssistantMessage",
    "AdminAuditLog",
]
