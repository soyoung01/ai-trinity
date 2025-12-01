from sqlalchemy.orm import Session
from sqlalchemy import not_, or_, and_
from typing import List, Dict, Any

# 우리가 만든 모델들 임포트
from src.database.models import User, Health, AnalyzeResult, Exercise, ExerciseRestrict, UserRestrict

class RoutinePreparationService:
    def __init__(self, db: Session):
        self.db = db


    # 1. Data Aggregation (데이터 수집)
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        사용자의 건강 정보, 체력 진단 결과, 제한 사항을 한 번에 묶어서 반환합니다.
        """
        # Health 정보 (장소, 숙련도 등)
        health = self.db.query(Health).filter(Health.user_id == user_id).first()
        if not health:
            raise ValueError(f"User {user_id}의 건강 정보(Health)가 없습니다. 먼저 설문을 진행해주세요.")

        # User Restricts
        user_injuries = [r.user_restrict for r in health.restricts]

        # AnalyzeResult
        analysis = self.db.query(AnalyzeResult).filter(AnalyzeResult.user_id == user_id).first()
        
        return {
            "profile": {
                "place": health.place,
                "proficiency": health.proficiency,
                "gender": health.gender
            },
            "injuries": user_injuries,
            "analysis": analysis
        }

    # 2. Candidate Filtering (후보군 필터링 - SQL)
    # 사용자가 수행 가능한 운동만 필터링
    def get_candidate_exercises(self, user_data: Dict[str, Any]) -> List[Dict]:
        profile = user_data["profile"]
        injuries = user_data["injuries"]
        
        query = self.db.query(Exercise)

        if profile["place"] == "HOME":
            query = query.filter(
                not_(Exercise.equipment.like("%MACHINE%")),
                not_(Exercise.equipment.like("%PULL_UP_BAR%")),
                not_(Exercise.equipment.like("%BARBELL%")),
                not_(Exercise.equipment.like("%BENCH%")) 
            )

        # 부상 부위 제외
        if injuries:
            bad_exercises = self.db.query(ExerciseRestrict.exercise_id)\
                .filter(ExerciseRestrict.exercise_restrict.in_(injuries))\
                .all()
            
            bad_exercise_ids = [row[0] for row in bad_exercises]

            if bad_exercise_ids:
                query = query.filter(Exercise.id.notin_(bad_exercise_ids))

        # 숙련도
        if profile["proficiency"] == "BEGINNER":
            query = query.filter(Exercise.difficulty != "HARD")
        
        candidates = query.all()
        
        return [
            {
                "id": ex.id,
                "name": ex.exercise_name,
                "part": ex.target_area,
                "difficulty": ex.difficulty,
                "equipment": ex.equipment,
                "type": ex.type,
                "image": ex.image
            }
            for ex in candidates
        ]

    # 3. Strategy Weighing (가중치 설정)
    # stamina 백분위 기준 분석
    def determine_strategy(self, user_data: Dict[str, Any]) -> str:
        analysis = user_data["analysis"]
        
        # 분석 데이터가 없거나, 아직 분석 전일 경우 방어 로직
        if not analysis:
            return "전신 균형 발달 및 기초 체력 증진" 

        scores = {
            "근력 강화": analysis.per_strength,
            "심폐지구력 향상": analysis.per_cardio,
            "코어 안정성 강화": analysis.per_core,
            "유연성 증진": analysis.per_flexibility,  
            "민첩성 훈련": analysis.per_agility    
        }
        
        weakest_area = min(scores, key=scores.get)
        weakest_score = scores[weakest_area]

        strategy = f"사용자의 분석 결과, '{weakest_area}'(상위 {weakest_score}%)가 가장 취약합니다. 이번 주 루틴은 {weakest_area} 훈련의 비중을 높여 구성해주세요."
        
        return strategy