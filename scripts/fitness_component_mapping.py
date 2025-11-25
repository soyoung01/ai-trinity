import pandas as pd
from pathlib import Path

# 6가지 체력요소별 측정항목 매핑
FITNESS_COMPONENTS_MAPPING = {
    '근력': [
        'MESURE_IEM_007_VALUE',  # 악력_좌
        'MESURE_IEM_008_VALUE',  # 악력_우
        'MESURE_IEM_022_VALUE',  # 제자리멀리뛰기 (하지 순발력)
        'MESURE_IEM_023_VALUE',  # 의자에앉았다일어서기 (하지 근지구력)
        'MESURE_IEM_028_VALUE',  # 상대악력
        'MESURE_IEM_052_VALUE',  # 절대악력
    ],
    
    '심폐지구력': [
        'MESURE_IEM_020_VALUE',  # 왕복오래달리기
        'MESURE_IEM_024_VALUE',  # 6분걷기
        'MESURE_IEM_025_VALUE',  # 2분제자리걷기
        'MESURE_IEM_030_VALUE',  # 왕복오래달리기출력(VO₂max)
        'MESURE_IEM_031_VALUE',  # 트레드밀_안정시
        'MESURE_IEM_032_VALUE',  # 트레드밀_3분
        'MESURE_IEM_033_VALUE',  # 트레드밀_6분
        'MESURE_IEM_034_VALUE',  # 트레드밀_9분
        'MESURE_IEM_035_VALUE',  # 트레드밀_계산(VO₂max)
        'MESURE_IEM_036_VALUE',  # 스텝검사_회복시 심박수
        'MESURE_IEM_037_VALUE',  # 스텝검사출력(VO₂max)
    ],
    
    '코어': [
        'MESURE_IEM_009_VALUE',  # 윗몸말아올리기
        'MESURE_IEM_019_VALUE',  # 교차윗몸일으키기
    ],
    
    '유연성': [
        'MESURE_IEM_012_VALUE',  # 앉아윗몸앞으로굽히기
    ],
    
    '민첩성': [
        'MESURE_IEM_010_VALUE',  # 반복점프
        'MESURE_IEM_013_VALUE',  # 일리노이
        'MESURE_IEM_014_VALUE',  # 체공시간
        'MESURE_IEM_015_VALUE',  # 협응력시간
        'MESURE_IEM_016_VALUE',  # 협응력실수횟수
        'MESURE_IEM_017_VALUE',  # 협응력계산결과값
        'MESURE_IEM_021_VALUE',  # 10M 4회 왕복달리기
        'MESURE_IEM_026_VALUE',  # 의자에앉아 3M표적 돌아오기
        'MESURE_IEM_027_VALUE',  # 8자보행
        'MESURE_IEM_040_VALUE',  # 반응시간
        'MESURE_IEM_041_VALUE',  # 성인체공시간
        'MESURE_IEM_043_VALUE',  # 반복옆뛰기
        'MESURE_IEM_044_VALUE',  # 눈-손 협응력(벽패스)
        'MESURE_IEM_050_VALUE',  # 5m 4회 왕복달리기
        'MESURE_IEM_051_VALUE',  # 3×3 버튼누르기
    ],
    
    '체성분': [
        'MESURE_IEM_001_VALUE',  # 신장
        'MESURE_IEM_002_VALUE',  # 체중
        'MESURE_IEM_003_VALUE',  # 체지방률
        'MESURE_IEM_004_VALUE',  # 허리둘레
        'MESURE_IEM_018_VALUE',  # BMI
        'MESURE_IEM_029_VALUE',  # 피부두겹합
        'MESURE_IEM_038_VALUE',  # 허벅지_좌
        'MESURE_IEM_039_VALUE',  # 허벅지_우
        'MESURE_IEM_042_VALUE',  # 허리둘레-신장비(WHtR)
    ],
}


# 역매핑: 컬럼명 → 체력요소
COLUMN_TO_FITNESS_COMPONENT = {}
for component, columns in FITNESS_COMPONENTS_MAPPING.items():
    for col in columns:
        COLUMN_TO_FITNESS_COMPONENT[col] = component


# 컬럼명으로 체력요소 조회
def get_fitness_component(column_name):
    return COLUMN_TO_FITNESS_COMPONENT.get(column_name)


# 체력요소로 해당 측정항목 컬럼 목록 조회
def get_columns_by_component(component):
    return FITNESS_COMPONENTS_MAPPING.get(component, [])


# 데이터프레임에서 실제로 존재하는 체력측정 항목 확인
def check_available_columns(df):
    available_by_component = {}
    
    for component, columns in FITNESS_COMPONENTS_MAPPING.items():
        available_cols = [col for col in columns if col in df.columns]
        available_by_component[component] = available_cols
    
    return available_by_component


# 체력요소 매핑 요약 출력
def print_mapping_summary(df=None):
    print("=" * 80)
    print("체력요소 매핑 시스템")
    print("=" * 80)
    
    for component, columns in FITNESS_COMPONENTS_MAPPING.items():
        print(f"\n🏋️ {component} ({len(columns)}개 항목)")
        print("-" * 80)
        
        for col in columns:
            # 데이터에 존재 여부 확인
            exists = "✅" if df is None or col in df.columns else "❌"
            
            # 컬럼명을 한글 측정항목명으로 변환 (간단히)
            item_code = col.replace('_VALUE', '')
            print(f"  {exists} {col}")
    
    print("\n" + "=" * 80)


# 주요 체력요소만 (핵심 6개 항목)
CORE_FITNESS_ITEMS = {
    '근력': 'MESURE_IEM_008_VALUE',           # 악력_우
    '심폐지구력': 'MESURE_IEM_020_VALUE',     # 왕복오래달리기
    '코어': 'MESURE_IEM_019_VALUE',           # 교차윗몸일으키기
    '유연성': 'MESURE_IEM_012_VALUE',         # 앉아윗몸앞으로굽히기
    '민첩성': 'MESURE_IEM_022_VALUE',         # 제자리멀리뛰기 (순발력)
    '체성분': 'MESURE_IEM_018_VALUE',         # BMI
}


if __name__ == "__main__":
    # 매핑 시스템 요약 출력
    print_mapping_summary()
    
    # 핵심 체력요소 출력
    print("\n" + "=" * 80)
    print("핵심 체력요소 (백분위 계산용)")
    print("=" * 80)
    for component, col in CORE_FITNESS_ITEMS.items():
        print(f"  {component}: {col}")
    print("=" * 80)