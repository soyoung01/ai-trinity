from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.api.deps import get_current_user_id
from src.database.models import AnalyzeResult
from src.api.models.request import PercentileRequest
from src.api.models.response import PercentileResponse
from src.utils.percentile_calculator import PercentileCalculator, create_user_fitness_profile
from src.utils.persona_classifier import classify_persona
from src.utils.llm_reporter import FitnessReportGenerator
from src.config import settings
from pathlib import Path
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

calculator = None
report_generator = None

#백분위 계산기 인스턴스 반환
def get_calculator():
    global calculator
    if calculator is None:
        reference_path = Path(settings.REFERENCE_DATA_PATH)
        if not reference_path.exists():
            logger.error(f"참조 데이터 파일을 찾을 수 없습니다: {reference_path}")
            raise FileNotFoundError(f"참조 데이터 파일을 찾을 수 없습니다: {reference_path}")
        calculator = PercentileCalculator(str(reference_path))
        logger.info(f"백분위 계산기 초기화 완료: {reference_path}")
    return calculator

def get_report_generator():
    global report_generator
    if report_generator is None:
        report_generator = FitnessReportGenerator(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
    return report_generator


@router.post(
    "/score",
    response_model=PercentileResponse,
    status_code=status.HTTP_200_OK
)
async def calculate_percentile(
    request: PercentileRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"체력 분석 시작")
        
        calc = get_calculator()
        
        user_data = {
            'gender': request.gender,
            'age': request.age,
            'bmi': request.bmi,
            'stamina': {
                'plank': request.stamina.plank,
                'pushUp': request.stamina.pushUp,
                'chairSquat': request.stamina.chairSquat,
                'stepTest': request.stamina.stepTest,
                'forwardFold': request.stamina.forwardFold,
                'balance': request.stamina.balance
            }
        }
        
        # 프로필 생성
        profile = create_user_fitness_profile(user_data, calc)
        
        # 페르소나 분류
        persona = classify_persona(profile['percentiles'])
        profile['persona'] = persona
        
        api_percentiles = {}
        for component, data in profile['percentiles'].items():
            api_percentiles[component] = {
                'percentile': data['percentile']
                # grade 제거
            }
        
        api_persona = {
            'name': persona['name'],
            'emoji': persona['emoji'],
            'description': persona['description'],
            'characteristics': persona['characteristics'],
            'recommendation': persona['recommendation']
        }
        
        response_data = {
            "user_info": profile['user_info'],
            "average_score": profile.get('average_score'),
            "percentiles": api_percentiles,
            "persona": api_persona
        }
        
        try:
            logger.info("LLM 리포트 생성 시작")
            report_gen = get_report_generator()
                
            llm_data = {
                'user_info': profile['user_info'],
                'percentiles': profile['percentiles'],
                'persona': persona
            }
                
            llm_report = report_gen.generate_report(
                data=llm_data,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE
            )
                
            response_data["llm_report"] = llm_report
            logger.info(f"LLM 리포트 생성 완료 ({len(llm_report)}자)")
                
        except Exception as e:
            logger.error(f"LLM 생성 실패 (백분위는 정상): {str(e)}")
            response_data["llm_report"] = "체력 측정을 완료했어요! 💪\n\n꾸준히 운동하면 더 좋아질 거예요. 화이팅!"
            logger.info("기본 리포트로 대체")
        
        logger.info("=== 체력 분석 완료 ===")
        
        # DB 저장
        try:
            db.query(AnalyzeResult).filter(AnalyzeResult.user_id == user_id).delete()
            
            def get_p_val(key):
                return int(profile['percentiles'].get(key, {}).get('percentile', 0) or 0)

            new_analysis = AnalyzeResult(
                user_id=user_id,
                average_score=profile.get('average_score', 0) or 0,
                llm_report=llm_report,
                
                # 백분위 매핑 (한글 키 -> DB 컬럼)
                per_strength=get_p_val('근력'),
                per_cardio=get_p_val('심폐지구력'),
                per_core=get_p_val('코어'),
                per_flexibility=get_p_val('유연성'),
                per_agility=get_p_val('민첩성'),
                per_body_composition=get_p_val('체성분'),
                
                persona=persona.get('type', 'BEGINNER') 
            )
            
            db.add(new_analysis)
            db.commit()
            logger.info(f"DB 저장 완료 (User ID: {user_id})")
            
        except Exception as db_e:
            db.rollback()
            logger.error(f"DB 저장 중 오류 발생: {str(db_e)}")
            raise HTTPException(status_code=500, detail="결과 저장 중 오류가 발생했습니다.")
        
        return PercentileResponse(
            status="success",
            data=response_data,
            message="백분위 계산이 완료되었습니다."
        )
        
        
    except FileNotFoundError as e:
        logger.error(f"파일을 찾을 수 없습니다: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="참조 데이터를 로드할 수 없습니다."
        )
    
    except ValueError as e:
        logger.error(f"입력값 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="백분위 계산 중 오류가 발생했습니다."
        )