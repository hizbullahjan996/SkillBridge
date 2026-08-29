from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.common import DBHealthResponse, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version="0.1.0",
    )


@router.get("/health/db", response_model=DBHealthResponse)
def health_db_check(db: Session = Depends(get_db)) -> DBHealthResponse:
    try:
        db.execute(text("SELECT 1"))
        return DBHealthResponse(status="ok", database="connected")
    except Exception:
        return DBHealthResponse(status="error", database="disconnected")
