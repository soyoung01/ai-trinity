import json
import numpy as np
from pathlib import Path
from datetime import datetime


# 백분위 계산기
class PercentileCalculator:
    
    def __init__(self, reference_json_path):
        self.reference_data = self._load_reference_data(reference_json_path)
    
    # 참조 백분위 데이터 로드    
    def _load_reference_data(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_age_group(self, age, with_suffix=True):
        if age < 10:
            age_range = "10-19"
        elif age < 20:
            age_range = "10-19"
        elif age < 30:
            age_range = "20-29"
        elif age < 40:
            age_range = "30-39"
        elif age < 50:
            age_range = "40-49"
        elif age < 60:
            age_range = "50-59"
        elif age < 70:
            age_range = "60-69"
        elif age < 80:
            age_range = "70-79"
        elif age < 90:
            age_range = "80-89"
        else:
            age_range = "90+"
        
        return f"{age_range}세" if with_suffix else age_range
    
    def calculate_percentile(self, value, reference_stats):
        """
        선형보간으로 백분위 계산
        
        Args:
            value: 사용자 측정값 (float)
            reference_stats: 참조 통계 (dict with p5, p10, ..., p95)
        
        Returns:
            float: 백분위 (0-100)
        """
        if not reference_stats:
            return None
        
        # 백분위 포인트
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        values = [reference_stats[f'p{p}'] for p in percentiles]
        
        # 범위 밖 처리
        if value <= values[0]:
            return 5
        if value >= values[-1]:
            return 95
        
        # 선형보간
        percentile = np.interp(value, values, percentiles)
        return round(percentile)
    
    def get_reference_group(self, gender, age):
        # 먼저 "세" 붙은 형식 시도
        age_group_with_suffix = self.get_age_group(age, with_suffix=True)
        key_with_suffix = f"{gender}_{age_group_with_suffix}"
        
        if key_with_suffix in self.reference_data:
            return key_with_suffix
        
        # 없으면 "세" 없는 형식 시도
        age_group_without_suffix = self.get_age_group(age, with_suffix=False)
        key_without_suffix = f"{gender}_{age_group_without_suffix}"
        
        return key_without_suffix
    
    def get_component_percentile(self, gender, age, component, value):
        # 참조 그룹 조회
        group_key = self.get_reference_group(gender, age)
        
        if group_key not in self.reference_data:
            return {
                'percentile': None,
                'grade': None,
                'reference_group': group_key,
                'error': '참조 데이터 없음'
            }
        
        group_data = self.reference_data[group_key]
        
        if component not in group_data:
            return {
                'percentile': None,
                'grade': None,
                'reference_group': group_key,
                'error': f'{component} 데이터 없음'
            }
        
        # 백분위 계산
        percentile = self.calculate_percentile(value, group_data[component])
        
        # 등급 판정
        if percentile is None:
            grade = None
        elif percentile < 30:
            grade = '하위'
        elif percentile < 70:
            grade = '평균'
        else:
            grade = '상위'
        
        return {
            'percentile': percentile,
            'grade': grade
        }


# 사용자 테스트
USER_TEST_CONVERSIONS = {
    'plank': {
        'target_component': '코어',
        'description': '플랭크 (초) → 교차윗몸일으키기 (회)',
        # 플랭크 1초 ≈ 윗몸일으키기 0.4~0.5회
        'conversion_factors': {
            'M_10-19': 0.48,
            'M_20-29': 0.45,
            'M_30-39': 0.42,
            'M_40-49': 0.38,
            'M_50-59': 0.35,
            'M_60-69': 0.30,
            'M_70-79': 0.25,
            'M_80-89': 0.20,
            'M_90+': 0.15,
            'F_10-19': 0.40,
            'F_20-29': 0.38,
            'F_30-39': 0.35,
            'F_40-49': 0.32,
            'F_50-59': 0.28,
            'F_60-69': 0.24,
            'F_70-79': 0.20,
            'F_80-89': 0.15,
            'F_90+': 0.10,
        }
    },
    'push_up': {
        'target_component': '근력',
        'description': '푸쉬업 (회) → 악력 (kg) 간접 추정',
        'conversion_factors': {
            'M_10-19': 1.6,
            'M_20-29': 1.5,
            'M_30-39': 1.4,
            'M_40-49': 1.3,
            'M_50-59': 1.2,
            'M_60-69': 1.1,
            'M_70-79': 1.0,
            'M_80-89': 0.9,
            'M_90+': 0.8,
            'F_10-19': 1.3,
            'F_20-29': 1.2,
            'F_30-39': 1.1,
            'F_40-49': 1.0,
            'F_50-59': 0.9,
            'F_60-69': 0.85,
            'F_70-79': 0.8,
            'F_80-89': 0.75,
            'F_90+': 0.7,
        }
    },
    'chair_squat': {
        'target_component': '민첩성',
        'description': '의자 스쿼트 (30초, 회) → 제자리멀리뛰기 (cm)',
        'conversion_factors': {
            'M_10-19': 8.0,
            'M_20-29': 7.5,
            'M_30-39': 7.0,
            'M_40-49': 6.5,
            'M_50-59': 6.0,
            'M_60-69': 5.5,
            'M_70-79': 5.0,
            'M_80-89': 4.5,
            'M_90+': 4.0,
            'F_10-19': 6.5,
            'F_20-29': 6.0,
            'F_30-39': 5.5,
            'F_40-49': 5.0,
            'F_50-59': 4.5,
            'F_60-69': 4.0,
            'F_70-79': 3.5,
            'F_80-89': 3.0,
            'F_90+': 2.5,
        }
    },
    'step_test': {
        'target_component': '심폐지구력',
        'description': 'Step 테스트 (1분, 회) → 왕복오래달리기 (회)',
        'conversion_factors': {
            'M_10-19': 1.3,
            'M_20-29': 1.2,
            'M_30-39': 1.15,
            'M_40-49': 1.1,
            'M_50-59': 1.05,
            'M_60-69': 1.0,
            'M_70-79': 0.95,
            'M_80-89': 0.9,
            'M_90+': 0.85,
            'F_10-19': 1.25,
            'F_20-29': 1.2,
            'F_30-39': 1.15,
            'F_40-49': 1.1,
            'F_50-59': 1.05,
            'F_60-69': 1.0,
            'F_70-79': 0.95,
            'F_80-89': 0.9,
            'F_90+': 0.85,
        }
    },
    'forward_fold': {
        'target_component': '유연성',
        'description': '유연성 점수 (1-5) → 앉아윗몸앞으로굽히기 (cm)',
        # 점수 → cm 변환 (고정값)
        'score_to_cm': {
            1: -5,   # 무릎 위
            2: 0,    # 종아리 중간
            3: 5,    # 발목
            4: 10,   # 발끝
            5: 18,   # 발끝 이상
        }
    },
    'balance': {
        'target_component': '민첩성',
        'description': '한발서기 (초) → 제자리멀리뛰기 (cm) 간접 추정',
        'conversion_factors': {
            'M_10-19': 2.8,
            'M_20-29': 2.5,
            'M_30-39': 2.3,
            'M_40-49': 2.0,
            'M_50-59': 1.8,
            'M_60-69': 1.5,
            'M_70-79': 1.3,
            'M_80-89': 1.0,
            'M_90+': 0.8,
            'F_10-19': 2.3,
            'F_20-29': 2.0,
            'F_30-39': 1.8,
            'F_40-49': 1.6,
            'F_50-59': 1.4,
            'F_60-69': 1.2,
            'F_70-79': 1.0,
            'F_80-89': 0.8,
            'F_90+': 0.6,
        }
    }
}


def convert_user_test_to_national(test_name, test_value, gender, age):
    if test_name not in USER_TEST_CONVERSIONS:
        return {'error': f'알 수 없는 테스트: {test_name}'}
    
    conversion_info = USER_TEST_CONVERSIONS[test_name]
    
    # 연령대 계산 ("세" 없는 형식)
    calculator = PercentileCalculator.__new__(PercentileCalculator)
    age_group = calculator.get_age_group(age, with_suffix=False)
    group_key = f"{gender}_{age_group}"
    
    # 유연성은 특별 처리 (점수 → cm)
    if test_name == 'forward_fold':
        if test_value not in conversion_info['score_to_cm']:
            return {'error': f'유효하지 않은 유연성 점수: {test_value}'}
        converted_value = conversion_info['score_to_cm'][test_value]
    else:
        # 일반 변환 (계수 곱하기)
        if group_key not in conversion_info['conversion_factors']:
            return {'error': f'변환 계수 없음: {group_key}'}
        factor = conversion_info['conversion_factors'][group_key]
        converted_value = test_value * factor
    
    return {
        'converted_value': round(converted_value, 2),
        'target_component': conversion_info['target_component']
    }


def create_user_fitness_profile(user_data, calculator):
    gender = user_data['gender']
    age = user_data['age']
    bmi = user_data['bmi']
    stamina = user_data['stamina']
    
    profile = {
        'user_info': {
            'gender': gender,
            'age': age,
            'bmi': bmi,
            'age_group': calculator.get_age_group(age)
        },
        'percentiles': {},
        'timestamp': datetime.now().isoformat()
    }
    
    # 6가지 테스트 각각 처리
    test_mapping = {
        'plank': '코어',
        'push_up': '근력',
        'chair_squat': '민첩성',
        'step_test': '심폐지구력',
        'forward_fold': '유연성',
        'balance': '민첩성'
    }
    
    for test_name, component in test_mapping.items():
        if test_name not in stamina or stamina[test_name] is None:
            continue
        
        # 사용자 측정값 → 국민체력100 값 변환
        conversion = convert_user_test_to_national(
            test_name, stamina[test_name], gender, age
        )
        
        # 백분위 계산
        percentile_result = calculator.get_component_percentile(
            gender, age, component, conversion['converted_value']
        )
        
        profile['percentiles'][component] = percentile_result
    
    # 체성분 (BMI) 추가
    if 'bmi' in user_data and user_data['bmi']:
        bmi_percentile = calculator.get_component_percentile(
            gender, age, '체성분', user_data['bmi']
        )
        profile['percentiles']['체성분'] = bmi_percentile
    
    # 종합 점수 계산 (민첩성은 chair_squat 우선)
    valid_percentiles = []
    for comp in ['근력', '심폐지구력', '코어', '유연성', '민첩성']:
        if comp in profile['percentiles']:
            p_val = profile['percentiles'][comp].get('percentile')
            if p_val is not None:
                valid_percentiles.append(p_val)
    
    if valid_percentiles:
        average_score = round(sum(valid_percentiles) / len(valid_percentiles), 1)
    else:
        average_score = None
    
    profile['average_score'] = average_score
    
    return profile