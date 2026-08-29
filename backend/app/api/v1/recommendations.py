"""API routes for career recommendations."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.recommendation import (
    CareerRecommendationResponse,
    LatestRecommendationResponse,
    RecommendationHistoryResponse,
)
from app.services.career_prediction_service import (
    get_career_recommendations,
    get_latest_recommendation,
    get_recommendation_history,
)

router = APIRouter(prefix="/recommendations", tags=["Career Recommendations"])


@router.post("/careers", response_model=CareerRecommendationResponse)
def predict_careers(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CareerRecommendationResponse:
    result = get_career_recommendations(db, current_user.id, top_k=3)
    return CareerRecommendationResponse(**result)


@router.get("/careers/history", response_model=RecommendationHistoryResponse)
def recommendation_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> RecommendationHistoryResponse:
    results = get_recommendation_history(db, current_user.id)
    return RecommendationHistoryResponse(results=results)


@router.get("/careers/latest", response_model=LatestRecommendationResponse)
def latest_recommendation(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> LatestRecommendationResponse:
    result = get_latest_recommendation(db, current_user.id)
    if not result:
        return LatestRecommendationResponse(
            model_version=None,
            created_at=None,
            recommendations=[],
        )
    return LatestRecommendationResponse(**result)
