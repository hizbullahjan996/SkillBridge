import enum
from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ResourceProgressStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


class StudentLearningResource(Base):
    __tablename__ = "student_learning_resources"
    __table_args__ = (
        Index("ix_student_resource", "student_id", "resource_id", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("learning_resources.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[ResourceProgressStatus] = mapped_column(String(20), default=ResourceProgressStatus.not_started, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    student: Mapped["StudentProfile"] = relationship()
    resource: Mapped["LearningResource"] = relationship()

    def __repr__(self) -> str:
        return f"<StudentLearningResource student_id={self.student_id} resource_id={self.resource_id} status={self.status}>"
