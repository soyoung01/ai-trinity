import json
import random
from sqlalchemy.orm import Session
from redis import Redis
from src.recommendation.routine_preparation import RoutinePreparationService

class RecommendationService:
    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.redis = redis
        self.prep_service = RoutinePreparationService(db)

    def get_instant_recommendations(self, user_id: int):
        cache_key = f"recommend:user:{user_id}"

        cached_data = self.redis.get(cache_key)
        if cached_data:
            print("Cache HIT by Redis)")
            return json.loads(cached_data)

        print("Cache MISS... Creating")
        new_recommendations = self._generate_new_recommendations(user_id)

        # Redis에 저장 (TTL: 1800초 = 30분)
        self.redis.set(
            name=cache_key,
            value=json.dumps(new_recommendations, ensure_ascii=False),
            ex=1800 
        )

        return new_recommendations

    def _generate_new_recommendations(self, user_id: int):
        """
        1. 안전한 운동 후보군 추출
        2. 약점 보완 / 유산소 / 랜덤 섞어서 3개 선정
        """
        user_data = self.prep_service.get_user_data(user_id)
        candidates = self.prep_service.get_candidate_exercises(user_data)
        
        if len(candidates) < 3:
            return candidates

        selected_exercises = []
        
        # 약점 반영 (없으면 기본값 '코어')
        analysis = user_data.get("analysis")
        weakest_part = "코어" # 기본값
        
        if analysis:
            # 가장 낮은 점수 찾기 
            scores = {
                "근력": analysis.per_strength,
                "심폐지구력": analysis.per_cardio,
                "유연성": analysis.per_flexibility,
                "코어": analysis.per_core
            }
            weakest_part = min(scores, key=scores.get)

        # 1번 운동: 약점 보완 운동
        weakness_candidates = [ex for ex in candidates if weakest_part in str(ex.get('part', ''))]
        if weakness_candidates:
            pick = random.choice(weakness_candidates)
            selected_exercises.append(pick)
            candidates.remove(pick) # 중복 방지

        # 2번 운동: 유산소성 운동
        cardio_candidates = [ex for ex in candidates if ex.get('type') == 'CARDIO' or ex.get('type') == '유산소']
        if cardio_candidates:
            pick = random.choice(cardio_candidates)
            selected_exercises.append(pick)
            candidates.remove(pick)

        # 3번 운동: 남은 것 중 완전 랜덤
        while len(selected_exercises) < 3 and candidates:
            pick = random.choice(candidates)
            selected_exercises.append(pick)
            candidates.remove(pick)

        return [ex["id"] for ex in selected_exercises]