import enum
from datetime import datetime

from sqlalchemy import String, Enum, Boolean, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MappingType(str, enum.Enum):
    strong = "strong"
    moderate = "moderate"
    weak = "weak"


class CareerJobMapping(Base):
    __tablename__ = "career_job_mappings"

    id: Mapped[int] = mapped_column(primary_key=True)
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    job_title_clean: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    mapping_type: Mapped[MappingType] = mapped_column(Enum(MappingType), nullable=False)
    confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    career: Mapped["Career"] = relationship(back_populates="career_job_mappings")

    def __repr__(self) -> str:
        return f"<CareerJobMapping career_id={self.career_id} job={self.job_title_clean}>"
