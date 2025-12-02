from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from redis import Redis
from src.database.database import get_db
from src.database.redis import get_redis
from src.api.deps import get_current_user_id
from src.recommendation.exercises_recommendation import RecommendationService

router = APIRouter()

@router.get("/exercise", status_code=status.HTTP_200_OK)
def get_instant_workout(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    service = RecommendationService(db, redis)
    recommendations = service.get_instant_recommendations(user_id)
    
    return {
        "status": "success",
        "data": recommendations,
        "message": "맞춤 추천 운동 3가지 추천 완료."
    }