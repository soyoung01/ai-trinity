from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.api.models.response import HealthCheckResponse
from src.config import settings
from src.database.database import get_db

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
# API 헬스체크
# 서버 상태 확인용
def health_check(db: Session = Depends(get_db)):
    """
    서버 상태와 DB 연결 상태를 확인합니다.
    """
    db_status = "disconnected"
    status_msg = "unhealthy"
    
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
        status_msg = "healthy"
    except Exception as e:
        print(f"DB Connection Error: {e}")
        db_status = f"error: {str(e)}"

    return HealthCheckResponse(
        status=status_msg,
        version=settings.VERSION,
        message="AI-TRINITY API is running",
        db_status=db_status
    )