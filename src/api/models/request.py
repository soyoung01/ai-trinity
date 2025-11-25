from pydantic import BaseModel, Field, field_validator
from typing import Optional


# 사용자 체력 테스트 입력
class StaminaInput(BaseModel):
    
    plank: Optional[float] = Field(None, ge=0, le=600, description="플랭크 (초)")
    push_up: Optional[int] = Field(None, ge=0, le=200, description="푸쉬업 (회)")
    chair_squat: Optional[int] = Field(None, ge=0, le=100, description="의자 스쿼트 30초 (회)")
    step_test: Optional[int] = Field(None, ge=0, le=200, description="Step 테스트 1분 (회)")
    forward_fold: Optional[int] = Field(None, ge=1, le=5, description="유연성 점수 (1-5)")
    balance: Optional[float] = Field(None, ge=0, le=300, description="한발서기 (초)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "plank": 60,
                "push_up": 25,
                "chair_squat": 26,
                "step_test": 50,
                "forward_fold": 4,
                "balance": 55
            }
        }


# 백분위 계산 요청
class PercentileRequest(BaseModel):
    
    gender: str = Field(..., description="성별 (M/F)")
    age: int = Field(..., ge=1, le=120, description="나이")
    bmi: Optional[float] = Field(None, ge=10.0, le=50.0, description="BMI")
    stamina: StaminaInput = Field(..., description="체력 테스트 결과")
    
    @field_validator('gender')
    @classmethod
    
    # 성별 검증
    def validate_gender(cls, v):
        v = v.upper()
        if v not in ['M', 'F']:
            raise ValueError('성별은 M(남성) 또는 F(여성)만 가능합니다')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "gender": "M",
                "age": 25,
                "bmi": 23.5,
                "stamina": {
                    "plank": 60,
                    "push_up": 25,
                    "chair_squat": 26,
                    "step_test": 50,
                    "forward_fold": 4,
                    "balance": 55
                }
            }
        }