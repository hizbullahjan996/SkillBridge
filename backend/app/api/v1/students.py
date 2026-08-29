from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.student import StudentProfile
from app.models.user import User
from app.schemas.profile import (
    MLReadinessResponse,
    ProfileCompletionResponse,
    StudentProfileResponse,
    StudentProfileUpdate,
)
from app.schemas.skill import StudentSkillResponse
from app.services.student_service import (
    calculate_profile_completion,
    check_ml_readiness,
    get_student_profile,
    update_student_profile,
)

router = APIRouter(prefix="/students", tags=["Student Profile"])


@router.get("/me", response_model=StudentProfileResponse)
def get_my_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudentProfileResponse:
    profile = get_student_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return StudentProfileResponse.model_validate(profile)


@router.put("/me", response_model=StudentProfileResponse)
def update_my_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
    body: StudentProfileUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> StudentProfileResponse:
    profile = update_student_profile(db, current_user.id, body)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return StudentProfileResponse.model_validate(profile)


@router.get("/me/profile-completion", response_model=ProfileCompletionResponse)
def get_profile_completion(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ProfileCompletionResponse:
    profile = get_student_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return calculate_profile_completion(profile)


@router.get("/me/ml-readiness", response_model=MLReadinessResponse)
def get_ml_readiness(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MLReadinessResponse:
    result = check_ml_readiness(db, current_user.id)
    return MLReadinessResponse(**result)


@router.get("/me/skills", response_model=list[StudentSkillResponse])
def get_my_skills(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[StudentSkillResponse]:
    from app.models.student import StudentProfile
    from app.models.student_skill import StudentSkill

    profile = get_student_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    student_skills = (
        db.query(StudentSkill)
        .filter(StudentSkill.student_id == profile.id)
        .all()
    )

    result = []
    for ss in student_skills:
        response = StudentSkillResponse.model_validate(ss)
        if ss.skill:
            from app.schemas.skill import SkillResponse
            response.skill = SkillResponse.model_validate(ss.skill)
        result.append(response)

    return result
