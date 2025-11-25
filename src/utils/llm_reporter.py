from openai import OpenAI
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# 체력 진단 텍스트 생성기
class FitnessReportGenerator:
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """초기화"""
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"FitnessReportGenerator 초기화 완료 (model: {model})")
    
    def create_prompt(self, data: dict) -> str:
        
        source_data = data.get('data', data)
        
        user_info = source_data.get('user_info', {})
        percentiles = source_data.get('percentiles', {})
        persona = source_data.get('persona', {})
        
        cardio = percentiles.get('심폐지구력', {'percentile': 0, 'grade': '정보없음'})
        strength = percentiles.get('근력', {'percentile': 0, 'grade': '정보없음'})
        agility = percentiles.get('민첩성', {'percentile': 0, 'grade': '정보없음'})
        flexibility = percentiles.get('유연성', {'percentile': 0, 'grade': '정보없음'})
        composition = percentiles.get('체성분', {'percentile': 0, 'grade': '정보없음'})
        core = percentiles.get('코어', {'percentile': 0, 'grade': '정보없음'})
        
        prompt = f"""당신은 친근하고 전문적인 피트니스 트레이너이자 건강 분석가입니다. 아래 사용자의 운동 능력 측정 결과를 바탕으로, 친절하지이고 날카로운 전문적인 피드백 리포트를 작성해주세요.

[사용자 정보]
- 성별: {user_info.get('gender', '알 수 없음')}
- 연령대: {user_info.get('age_group', '알 수 없음')}
- bmi: {user_info.get('bmi', '알 수 없음')}

[측정 결과 및 상위 백분위(높을수록 좋음)]
- 심폐지구력: {cardio['percentile']}% ({cardio['grade']})
- 근력: {strength['percentile']}% ({strength['grade']})
- 민첩성: {agility['percentile']}% ({agility['grade']})
- 유연성: {flexibility['percentile']}% ({flexibility['grade']})
- 체성분: {composition['percentile']}% ({composition['grade']})
- 코어: {core['percentile']}% ({core['grade']})

- 전체에서 백분위 : {persona.get('average_score', 'None')}

[분석된 페르소나]
- 타입: {persona.get('name', '분석 중')}
- 특징: {persona.get('description', '특징 정보 없음')}
- 추천: {persona.get('recommendation', '추천 정보 없음')}

다음 규칙으로 체력 진단 리포트를 작성해주세요:

1. 존댓말로 정중하게 작성
2. 바로 본론으로 들어가기
3. 긍정적이고 동기부여가 되는 톤
4. 약점은 "개선 기회"로 표현. 개선해야할 부분 확실하게 안내해주기
5. 총 400-500자 분량
6. 이모지 적절히 사용

형식:
- 첫 문장: 페르소나 소개(첫 문장: @@@ 타입인 당신!, @@@안에는 페르소나 타입을 넣어서) 및 전체에서 백분위 기반으로 평균 상위 or 하위 nn% 알려주기 (50 <= average_score: 상위 100-(average_score)%, 50 > average_score: 하위 (average_score)%)
- 2-3문장: 강점 칭찬
- 2-3문장: 개선점
- 마지막: 격려 메시지

의학적 진단이나 처방은 절대 금지입니다."""

        return prompt
    
    def generate_report(
        self, 
        data: Dict[str, Any], 
        max_tokens: int = 800,
        temperature: float = 0.7
    ) -> str:
        
        try:
            prompt = self.create_prompt(data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 친근하고 전문적인 체력 트레이너입니다. 사용자에게 동기부여가 되는 체력 진단 리포트를 작성합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=10.0  # 10초 타임아웃
            )
            
            report = response.choices[0].message.content.strip()
            
            # 토큰 사용량 로깅
            logger.info(f"OpenAI 토큰 사용: {response.usage.total_tokens} tokens")
            
            return report
            
        except Exception as e:
            logger.error(f"LLM 리포트 생성 실패: {str(e)}")
            # Fallback: 기본 메시지
            return self._get_fallback_report(data)
    
    def _get_fallback_report(self, data: Dict[str, Any]) -> str:
        """OpenAI 실패 시 기본 리포트 (안전하게 수정)"""
        
        persona = data.get('persona', {})
        average_score = data.get('average_score', 0)
        user_info = data.get('user_info', {})
        
        persona_name = persona.get('name', '체력 테스트')
        persona_emoji = persona.get('emoji', '💪')
        age = user_info.get('age', '')
        
        return f"""체력 측정이 완료되었어요!

{age}세의 너는 '{persona_name}' {persona_emoji}
종합 점수는 {average_score:.1f}점입니다!

너만의 강점을 살리면서 약한 부분도 조금씩 개선해나가면 
더욱 균형 잡힌 체력을 가질 수 있을 거예요.

Mofit과 함께 꾸준한 운동을 시작해 볼까요? 화이팅! 💪"""