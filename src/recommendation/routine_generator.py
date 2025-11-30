import json
from openai import OpenAI
from src.config import settings
from src.api.models.routine import WeeklyRoutineResponse

class RoutineGeneratorService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE

    def generate_weekly_routine(
        self, 
        user_profile: dict, 
        candidates: list, 
        strategy: str
    ) -> WeeklyRoutineResponse:
        """
        [입력]
        - user_profile: 사용자 기본 정보 (장소, 숙련도 등)
        - candidates: 필터링된 운동 후보군 리스트 (ID, 이름 포함)
        - strategy: 체력 진단 기반 가중치 전략 텍스트 ("심폐지구력 위주로...")
        
        [출력]
        - Pydantic 모델로 검증된 7일치 루틴 객체
        """
        
        # 1. 시스템 프롬프트: 페르소나 및 절대 규칙 설정
        system_prompt = """
        당신은 사용자의 체력 데이터와 환경을 분석하여 최적의 '7일 운동 루틴'을 설계하는 AI 전문가입니다.
        
        [절대 규칙]
        1. 반드시 제공된 'Available Exercises' 목록에 있는 운동만 사용해야 합니다. (Exercise ID 필수 매칭)
        2. 제공되지 않은 운동을 창조하거나 ID를 임의로 지어내면 안 됩니다.
        3. 하루 운동 루틴은 30분~40분 내외로 구성하세요.
        4. 루틴 구성 시 'Warm-up -> Main Workout -> Cool-down' 흐름을 고려하세요.
        5. 특정 부위에 부하가 쏠리지 않도록 적절한 분할(Split)을 적용하세요.
        """

        # 2. 사용자 프롬프트: 실제 데이터 주입
        # 후보군 리스트를 JSON 문자열로 변환하여 프롬프트에 삽입
        candidates_json = json.dumps(candidates, ensure_ascii=False)
        
        user_prompt = f"""
        [User Information]
        - Place: {user_profile.get('place')}
        - Proficiency: {user_profile.get('proficiency')}
        - Injuries/Restricts: {user_profile.get('injuries', 'None')}

        [Strategic Focus]
        {strategy}
        (위 전략에 맞춰 운동 빈도와 강도를 조절해주세요.)

        [Available Exercises (Candidates)]
        {candidates_json}

        위 정보를 바탕으로 7일간의 주간 루틴을 JSON 포맷으로 생성해주세요.
        """

        try:
            # 3. OpenAI API 호출 (Structured Output)
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=WeeklyRoutineResponse,
                temperature=self.temperature,
            )

            # 4. 결과 파싱 및 반환
            # 거절(refusal) 여부 체크
            if completion.choices[0].message.refusal:
                raise ValueError("AI가 루틴 생성을 거절했습니다.")

            return completion.choices[0].message.parsed

        except Exception as e:
            print(f"🔴 LLM Generation Error: {e}")
            raise e