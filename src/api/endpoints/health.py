from fastapi import APIRouter
from src.api.models.response import HealthCheckResponse
from src.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
# API 헬스체크
# 서버 상태 확인용
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        version=settings.VERSION,
        message="AI-TRINITY API is running"
    )