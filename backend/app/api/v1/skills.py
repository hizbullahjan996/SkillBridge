from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.skill import (
    SkillResponse,
    StudentSkillCreate,
    StudentSkillResponse,
)
from app.services.student_service import (
    add_student_skill,
    get_all_skills,
    get_skill_by_id,
    get_student_profile,
    remove_student_skill,
)

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("", response_model=list[SkillResponse])
def list_skills(
    db: Annotated[Session, Depends(get_db)],
    category: str | None = None,
    search: str | None = None,
) -> list[SkillResponse]:
    skills = get_all_skills(db, category=category, search=search)
    return [SkillResponse.model_validate(s) for s in skills]


@router.post(
    "/me",
    response_model=StudentSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_my_skill(
    current_user: Annotated[User, Depends(get_current_active_user)],
    body: StudentSkillCreate,
    db: Annotated[Session, Depends(get_db)],
) -> StudentSkillResponse:
    profile = get_student_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    skill = get_skill_by_id(db, body.skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    student_skill = add_student_skill(db, profile.id, body)
    if not student_skill:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Skill already exists for this student",
        )

    response = StudentSkillResponse.model_validate(student_skill)
    if student_skill.skill:
        response.skill = SkillResponse.model_validate(student_skill.skill)
    return response


@router.delete("/me/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_my_skill(
    current_user: Annotated[User, Depends(get_current_active_user)],
    skill_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    profile = get_student_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    removed = remove_student_skill(db, profile.id, skill_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found for this student",
        )
