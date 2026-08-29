from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.students import router as students_router
from app.api.v1.skills import router as skills_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.skill_gaps import router as skill_gaps_router
from app.api.v1.learning_resources import router as learning_resources_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router)
api_router.include_router(students_router)
api_router.include_router(skills_router)
api_router.include_router(recommendations_router)
api_router.include_router(jobs_router)
api_router.include_router(skill_gaps_router)
api_router.include_router(learning_resources_router)
api_router.include_router(assistant_router)
api_router.include_router(admin_router)
