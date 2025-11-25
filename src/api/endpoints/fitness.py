from fastapi import APIRouter, HTTPException, status, Query
from src.api.models.request import PercentileRequest
from src.api.models.response import PercentileResponse, ReportRequest
from src.utils.percentile_calculator import PercentileCalculator, create_user_fitness_profile
from src.utils.persona_classifier import classify_persona
from src.utils.llm_reporter import FitnessReportGenerator
from src.config import settings
from pathlib import Path
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# 전역 계산기 인스턴스 (서버 시작 시 한 번만 로드)
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
    status_code=status.HTTP_200_OK,
    tags=["Fitness"]
)
async def calculate_percentile(
    request: PercentileRequest,
    include_llm: bool = Query(True, description="LLM 리포트 생성 여부")):
    try:
        logger.info(f"=== 체력 분석 시작 (include_llm={include_llm}) ===")
        
        # 계산기 인스턴스 가져오기
        calc = get_calculator()
        
        # 사용자 데이터 변환
        user_data = {
            'gender': request.gender,
            'age': request.age,
            'bmi': request.bmi,
            'stamina': {
                'plank': request.stamina.plank,
                'push_up': request.stamina.push_up,
                'chair_squat': request.stamina.chair_squat,
                'step_test': request.stamina.step_test,
                'forward_fold': request.stamina.forward_fold,
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
        
        if include_llm:
            try:
                logger.info("LLM 리포트 생성 시작...")
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
        

@router.post(
    "/report",
    summary="LLM 기반 체력 진단 텍스트 생성"
)
async def generate_fitness_report(request: ReportRequest):
    
    try:
        # 디버깅: 실제 데이터 구조 확인
        logger.info("=== 받은 데이터 구조 ===")
        logger.info(f"user_info: {request.user_info}")
        logger.info(f"percentiles keys: {request.percentiles.keys()}")
        logger.info(f"persona keys: {request.persona.keys()}")
        logger.info(f"average_score: {request.average_score}")
        
        # 첫 번째 percentile 샘플 출력
        if request.percentiles:
            first_key = list(request.percentiles.keys())[0]
            logger.info(f"percentiles 샘플 [{first_key}]: {request.percentiles[first_key]}")
        
        logger.info(f"persona 내용: {request.persona}")
        logger.info("======================")
        
        report_gen = get_report_generator()
        
        llm_data = {
            'user_info': request.user_info,
            'percentiles': request.percentiles,
            'persona': request.persona,
            'average_score': request.average_score
        }
        
        llm_report = report_gen.generate_report(
            data=llm_data,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE
        )
        
        return {
            "status": "success",
            "data": {
                "llm_report": llm_report
            },
            "message": "AI 리포트가 생성되었습니다."
        }
        
    except Exception as e:
        logger.error(f"리포트 생성 중 오류: {str(e)}", exc_info=True)
        
        # 최후의 fallback
        return {
            "status": "success",
            "data": {
                "llm_report": "체력 측정을 완료했어요! 💪\n\n꾸준히 운동하면 더 좋아질 거예요. 화이팅!"
            },
            "message": "기본 리포트가 생성되었습니다."
        }