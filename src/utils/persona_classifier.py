from typing import Dict


# 6가지 페르소나 타입 정의
PERSONA_TYPES = {
    "balanced_athlete": {
        "name": "운동과 친구 타입",
        "emoji": "💪",
        "description": "모든 체력 요소가 고르게 발달한 균형잡힌 체력을 가진 타입",
        "characteristics": [
            "전반적으로 평균 이상의 체력",
            "꾸준한 운동 습관 보유",
            "다양한 운동을 즐김"
        ],
        "recommendation": "현재 수준을 유지하면서 약한 부분을 집중 보완하세요."
    },
    "strength_focused": {
        "name": "파워 헬창 타입",
        "emoji": "🏋️",
        "description": "근력이 매우 뛰어난 파워형 체력의 소유자",
        "characteristics": [
            "뛰어난 근력과 파워",
            "웨이트 트레이닝 선호",
            "상대적으로 유연성/심폐지구력 부족"
        ],
        "recommendation": "유산소 운동과 스트레칭을 추가하여 균형을 맞추세요."
    },
    "cardio_master": {
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
    "flexibility_king": {
        "name": "부드러운 우연성 타입",
        "emoji": "🧘",
        "description": "유연성이 뛰어난 밸런스형 체력의 소유자",
        "characteristics": [
            "탁월한 유연성",
            "요가/필라테스 적합",
            "부드러운 움직임"
        ],
        "recommendation": "근력과 심폐지구력을 강화하여 전반적인 체력을 향상시키세요."
    },
    "beginner": {
        "name": "파릇파릇 새싹 타입",
        "emoji": "🌱",
        "description": "운동을 이제 막 시작하거나 기초 체력이 필요한 타입",
        "characteristics": [
            "전반적으로 낮은 체력 수준",
            "운동 경험 부족",
            "체계적인 운동 계획 필요"
        ],
        "recommendation": "가벼운 운동부터 시작하여 점진적으로 강도를 높이세요."
    },
    "weak_core": {
        "name": "종이인간 타입",
        "emoji": "📄",
        "description": "근력과 코어가 약한 타입으로 기초 체력 강화가 필요한 타입",
        "characteristics": [
            "약한 근력과 코어",
            "자세 불안정",
            "쉽게 피로감을 느낌"
        ],
        "recommendation": "코어 운동과 기초 근력 운동에 집중하세요."
    }
}


def classify_persona(percentiles: Dict[str, Dict]) -> Dict[str, any]:
    """
    체력 백분위를 기반으로 페르소나 분류
    
    Args:
        percentiles: 6개 체력요소별 백분위 정보
        {
            '근력': {'percentile': 45.2, 'grade': '평균'},
            '심폐지구력': {'percentile': 60.1, 'grade': '평균'},
            ...
        }
    
    Returns:
        dict: {
            'type': 'balanced_athlete',
            'name': '운동과 친구 타입',
            'emoji': '💪',
            'description': '...',
            'characteristics': [...],
            'recommendation': '...'
        }
    """
    # 백분위 점수 추출 (None 값 처리)
    scores = {}
    for component in ['근력', '심폐지구력', '코어', '유연성', '민첩성', '체성분']:
        if component in percentiles and percentiles[component].get('percentile') is not None:
            scores[component] = percentiles[component]['percentile']
        else:
            scores[component] = 0  # 데이터 없으면 0으로 처리
    
    # 전체 평균 계산 (체성분 제외)
    fitness_components = ['근력', '심폐지구력', '코어', '유연성', '민첩성']
    valid_scores = [scores[c] for c in fitness_components if scores[c] > 0]
    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    # 최고 점수 체력요소
    max_component = max(fitness_components, key=lambda c: scores[c])
    max_score = scores[max_component]
    
    # 최저 점수 체력요소
    min_component = min(fitness_components, key=lambda c: scores[c])
    min_score = scores[min_component]
    
    # 분류 로직
    persona_type = None
    
    # 1. 운동과 친구 타입: 전체 평균 60 이상, 하위(30 미만) 항목 1개 이하
    low_count = sum(1 for c in fitness_components if scores[c] < 30)
    if avg_score >= 60 and low_count <= 1:
        persona_type = "balanced_athlete"
    
    # 2. 파워 헬창 타입: 근력 80 이상
    elif scores['근력'] >= 80:
        persona_type = "strength_focused"
    
    # 3. 두 개의 심장 타입: 심폐지구력 80 이상
    elif scores['심폐지구력'] >= 80:
        persona_type = "cardio_master"
    
    # 4. 부드러운 유연성 타입: 유연성 80 이상
    elif scores['유연성'] >= 80:
        persona_type = "flexibility_king"
    
    # 5. 종이인간 타입: 근력과 코어 모두 30 미만
    elif scores['근력'] < 30 and scores['코어'] < 30:
        persona_type = "weak_core"
    
    # 6. 파릇파릇 새싹 타입: 전체 평균 30 미만 또는 하위 항목 3개 이상
    elif avg_score < 30 or low_count >= 3:
        persona_type = "beginner"
    
    # 7. 기본값: 가장 높은 점수 체력요소 기준
    else:
        if max_score >= 70:
            if max_component == '근력':
                persona_type = "strength_focused"
            elif max_component == '심폐지구력':
                persona_type = "cardio_master"
            elif max_component == '유연성':
                persona_type = "flexibility_king"
            else:
                persona_type = "balanced_athlete"
        else:
            # 애매한 경우 약점 기준
            if scores['근력'] < 30 and scores['코어'] < 30:
                persona_type = "weak_core"
            else:
                persona_type = "beginner"
    
    # 페르소나 정보 반환
    persona_info = PERSONA_TYPES[persona_type].copy()
    #persona_info['type'] = persona_type
    persona_info['average_score'] = round(avg_score, 1)
    persona_info['strongest'] = {
        'component': max_component,
        'percentile': round(max_score, 1)
    }
    persona_info['weakest'] = {
        'component': min_component,
        'percentile': round(min_score, 1)
    }
    
    return persona_info