from pydantic import BaseModel, Field
from typing import List, Optional

# 개별 운동 아이템
class RoutineExerciseItem(BaseModel):
    exercise_id: int = Field(
        ..., 
        description="운동의 고유 ID"
    )
    order: int = Field(
        ..., 
        description="해당 루틴 내에서의 운동 순서 (1, 2, 3...)"
    )
    recommended_reps: Optional[int] = Field(None, description="AI 추천 횟수")
    recommended_sets: Optional[int] = Field(None, description="AI 추천 세트")

# 하루치 루틴
class DailyRoutineSchema(BaseModel):
    day: int = Field(
        ..., 
        description="루틴 진행 일차 (1~7)", 
        ge=1, 
        le=7
    )
    title: str = Field(
        ..., 
        description="하루 루틴의 테마 제목 (예: '상체 가동성 확보', '코어 집중')"
    )
    description: str = Field(
        ..., 
        description="하루 루틴에 대한 간단한 한 줄 설명 (예: '코어 근육을 강화하여 허리 안정성을 높입니다.')"
    )
    exercises: List[RoutineExerciseItem] = Field(
        ..., 
        description="해당 일자에 수행할 운동 목록"
    )

# 3. 7일치 전체 루틴
class WeeklyRoutineResponse(BaseModel):
    routines: List[DailyRoutineSchema] = Field(
        ..., 
        description="1일차부터 7일차까지 구성된 운동 루틴 리스트",
        min_length=7,
        max_length=7
    )
    
class SimpleRoutineResponse(BaseModel):
    status: str = Field(..., description="응답 상태 (success/error)")
    message: str = Field(..., description="응답 메시지")