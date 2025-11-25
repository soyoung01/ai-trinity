import pandas as pd
import numpy as np
import json
from pathlib import Path

# 파일 경로 설정
DATA_PATH = Path('data/processed/fitness_cleaned_2022_2025.csv')  # 실제 파일 경로로 변경 필요
OUTPUT_JSON = Path('outputs/reference_percentiles_real.json')
OUTPUT_CSV = Path('outputs/reference_percentiles_real.csv')

# 데이터 로드
print("\n데이터 로드 중...")
if not DATA_PATH.exists():
    print(f"오류: 파일을 찾을 수 없습니다 - {DATA_PATH}")
    print("   파일 경로를 확인해주세요.")
    exit(1)

df = pd.read_csv(DATA_PATH)
print(f"로드 완료: {len(df):,}건")

# 6가지 핵심 체력요소 매핑
FITNESS_COMPONENTS = {
    '근력': 'MESURE_IEM_008_VALUE',           # 악력_우
    '심폐지구력': 'MESURE_IEM_020_VALUE',     # 왕복오래달리기
    '코어': 'MESURE_IEM_019_VALUE',           # 교차윗몸일으키기
    '유연성': 'MESURE_IEM_012_VALUE',         # 앉아윗몸앞으로굽히기
    '민첩성': 'MESURE_IEM_022_VALUE',         # 제자리멀리뛰기
    '체성분': 'MESURE_IEM_018_VALUE',         # BMI
}

# 필요한 컬럼 확인
required_cols = ['GENDER_AGE_GROUP'] + list(FITNESS_COMPONENTS.values())
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    print(f"오류: 필요한 컬럼이 없습니다 - {missing_cols}")
    exit(1)

print("\n백분위 계산 중...")

# 백분위 리스트
percentiles = [5, 10, 25, 50, 75, 90, 95]

# 결과 저장용 딕셔너리
result_dict = {}
result_rows = []

# GENDER_AGE_GROUP으로 그룹화
groups = df.groupby('GENDER_AGE_GROUP')

total_groups = len(groups)
current = 0

for group_key, group_df in groups:
    current += 1
    
    # 성별과 연령대 추출 (예: "M_60-69세" → gender="M", age_group="60-69세")
    parts = group_key.split('_', 1)
    gender = parts[0]
    age_group = parts[1] if len(parts) > 1 else ""
    
    # 진행률 표시
    print(f"   처리 중: {group_key} ({current}/{total_groups}) - {len(group_df):,}건", end='\r')
    
    # 그룹별 데이터 저장
    result_dict[group_key] = {}
    
    # 각 체력요소별 백분위 계산
    for component_name, column_name in FITNESS_COMPONENTS.items():
        # 결측치 제거
        valid_data = group_df[column_name].dropna()
        
        if len(valid_data) < 10:  # 데이터가 너무 적으면 스킵
            print(f"\n경고: {group_key} - {component_name} 데이터 부족 ({len(valid_data)}건)")
            continue
        
        # 백분위 계산
        percentile_values = {}
        for p in percentiles:
            percentile_values[f'p{p}'] = float(np.percentile(valid_data, p))
        
        # 평균 및 표준편차
        percentile_values['mean'] = float(valid_data.mean())
        percentile_values['std'] = float(valid_data.std())
        percentile_values['count'] = int(len(valid_data))
        
        # 결과 저장
        result_dict[group_key][component_name] = percentile_values
        
        # CSV용 row 추가
        row = {
            'gender': gender,
            'age_group': age_group,
            'component': component_name,
            'column_name': column_name,
            **percentile_values
        }
        result_rows.append(row)

print("\n백분위 계산 완료!")

# JSON 저장
print("\n3️JSON 파일 저장 중...")
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result_dict, f, ensure_ascii=False, indent=2)
print(f"JSON 저장 완료: {OUTPUT_JSON}")

# CSV 저장
print("\n4️CSV 파일 저장 중...")
result_df = pd.DataFrame(result_rows)
result_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
print(f"CSV 저장 완료: {OUTPUT_CSV}")

# 통계 요약
print("생성 결과 요약")
print("=" * 80)

print(f"\n총 그룹 수: {len(result_dict)}")
print(f"총 레코드 수: {len(result_rows)}")

# 그룹별 데이터 개수 확인
print("\n그룹별 데이터 현황:")
print("-" * 80)
print(f"{'그룹':<15} {'근력':<8} {'심폐지구력':<10} {'코어':<8} {'유연성':<8} {'민첩성':<8} {'체성분':<8}")
print("-" * 80)

for group_key in sorted(result_dict.keys()):
    counts = []
    for component in ['근력', '심폐지구력', '코어', '유연성', '민첩성', '체성분']:
        if component in result_dict[group_key]:
            counts.append(f"{result_dict[group_key][component]['count']:,}")
        else:
            counts.append("-")
    
    print(f"{group_key:<15} {counts[0]:<8} {counts[1]:<10} {counts[2]:<8} {counts[3]:<8} {counts[4]:<8} {counts[5]:<8}")

# 샘플 데이터 출력 (M_20-29세 근력)
if 'M_20-29세' in result_dict and '근력' in result_dict['M_20-29세']:
    print("\n" + "=" * 80)
    print("샘플 데이터 (20대 남성 - 근력/악력)")
    print("=" * 80)
    sample = result_dict['M_20-29세']['근력']
    print(f"데이터 개수: {sample['count']:,}건")
    print(f"평균: {sample['mean']:.2f} kg")
    print(f"표준편차: {sample['std']:.2f} kg")
    print("\n백분위:")
    for p in percentiles:
        print(f"  p{p:>2}: {sample[f'p{p}']:>6.2f} kg")

print("\n" + "=" * 80)
print("백분위 테이블 생성 완료!")
print("=" * 80)
print(f"\n생성된 파일:")
print(f"  1. {OUTPUT_JSON}")
print(f"  2. {OUTPUT_CSV}")