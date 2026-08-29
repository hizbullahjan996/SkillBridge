import enum
from datetime import datetime

from sqlalchemy import String, Boolean, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ResourceType(str, enum.Enum):
    course = "course"
    documentation = "documentation"
    tutorial = "tutorial"
    video = "video"
    book = "book"
    practice = "practice"
    project = "project"


class ResourceDifficulty(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resource_type: Mapped[ResourceType] = mapped_column(String(20), nullable=False)
    difficulty: Mapped[ResourceDifficulty | None] = mapped_column(String(20), nullable=True)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    resource_skills: Mapped[list["LearningResourceSkill"]] = relationship(back_populates="resource", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<LearningResource id={self.id} title={self.title}>"


class LearningResourceSkill(Base):
    __tablename__ = "learning_resource_skills"
    __table_args__ = (
        Index("ix_resource_skill", "resource_id", "skill_id", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("learning_resources.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    resource: Mapped["LearningResource"] = relationship(back_populates="resource_skills")
    skill: Mapped["Skill"] = relationship()

    def __repr__(self) -> str:
        return f"<LearningResourceSkill resource_id={self.resource_id} skill_id={self.skill_id}>"
