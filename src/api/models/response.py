from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


#체력요소별 백분위 정보
class ComponentPercentile(BaseModel):
    
    percentile: Optional[float] = Field(None, description="백분위 점수 (0-100)")
    grade: Optional[str] = Field(None, description="등급 (하위/평균/상위)")
    reference_group: str = Field(..., description="참조 그룹")
    error: Optional[str] = Field(None, description="에러 메시지")


# 사용자 기본 정보
class UserInfo(BaseModel):
    
    gender: str = Field(..., description="성별")
    age: int = Field(..., description="나이")
    age_group: str = Field(..., description="연령대")
    reference_group: str = Field(..., description="참조 그룹")


class PercentileResponse(BaseModel):
    """백분위 계산 응답"""
    
    status: str
    data: Dict[str, Any]
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "user_info": {
                    "gender": "M",
                    "age": 25,
                    "bmi": 23.5,
                    "age_group": "20-29세"
                    },
                    "average_score": 31.6,
                    "percentiles": {
                    "코어": {
                        "percentile": 7
                    },
                    "근력": {
                        "percentile": 15
                    },
                    "민첩성": {
                        "percentile": 5
                    },
                    "심폐지구력": {
                        "percentile": 82
                    },
                    "유연성": {
                        "percentile": 49
                    },
                    "체성분": {
                        "percentile": 36
                    }
                    },
                    "persona": {
                    "name": "두 개의 심장 타입",
                    "emoji": "🏃",
                    "description": "심폐지구력이 탁월한 지구력형 타입",
                    "characteristics": [
                        "뛰어난 심폐지구력",
                        "장거리 운동에 강함",
                        "러닝/사이클링 등 유산소 운동 선호"
                    ],
                    "recommendation": "근력 운동을 추가하여 부상을 예방하세요."
                    },
                    "llm_report": "..."
                },
                "message": "백분위 계산이 완료되었습니다."
                }
            }

class ReportRequest(BaseModel):
    user_info: dict = Field(..., description="사용자 기본 정보")
    percentiles: dict = Field(..., description="백분위 결과")
    persona: dict = Field(..., description="페르소나 정보")
    average_score: float = Field(..., description="종합 점수")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_info": {
                    "gender": "M",
                    "age": 25,
                    "bmi": 23.5
                },
                "percentiles": {
                    "근력": {"percentile": 45, "grade": "평균"},
                    # ...
                },
                "persona": {
                    "type": "flexibility",
                    "name": "유연왕 타입",
                    "emoji": "🧘"
                },
                "average_score": 52.3
            }
        }


class HealthCheckResponse(BaseModel):
    """헬스체크 응답"""
    
    status: str = Field(..., description="상태")
    version: str = Field(..., description="버전")
    message: str = Field(..., description="메시지")