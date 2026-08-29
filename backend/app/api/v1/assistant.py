"""API routes for AI Career Assistant."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.learning_resource import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantSource,
    AssistantConversationResponse,
    AssistantConversationDetail,
    AssistantMessageResponse,
)
from app.services import ai_career_assistant

router = APIRouter(tags=["AI Assistant"])


@router.post("/assistant/chat", response_model=AssistantChatResponse)
def assistant_chat(
    body: AssistantChatRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AssistantChatResponse:
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    result = ai_career_assistant.chat(
        db,
        current_user.student_profile.id,
        body.message,
        body.conversation_id,
    )

    return AssistantChatResponse(
        answer=result["answer"],
        sources=[AssistantSource(**s) for s in result["sources"]],
        conversation_id=result["conversation_id"],
    )


@router.get("/assistant/conversations", response_model=list[AssistantConversationResponse])
def list_conversations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    conversations = ai_career_assistant.get_student_conversations(
        db, current_user.student_profile.id
    )
    return [AssistantConversationResponse(**c) for c in conversations]


@router.get("/assistant/conversations/{conversation_id}", response_model=AssistantConversationDetail)
def get_conversation(
    conversation_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    result = ai_career_assistant.get_conversation_history(
        db, current_user.student_profile.id, conversation_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return AssistantConversationDetail(
        conversation=AssistantConversationResponse(**result["conversation"]),
        messages=[AssistantMessageResponse(**m) for m in result["messages"]],
    )


@router.delete("/assistant/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Student profile not found")

    deleted = ai_career_assistant.delete_conversation(
        db, current_user.student_profile.id, conversation_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"detail": "Conversation deleted"}
