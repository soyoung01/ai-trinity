from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.api.deps import get_current_user_id
from src.recommendation.routine_preparation import RoutinePreparationService
from src.recommendation.routine_generator import RoutineGeneratorService
from src.database.models import ExercisePlan, ExerciseList
from src.api.models.routine import SimpleRoutineResponse

router = APIRouter()

@router.post("/routine", response_model=SimpleRoutineResponse, status_code=status.HTTP_201_CREATED)
def create_new_routine(
    user_id: int = Depends(get_current_user_id),  
    db: Session = Depends(get_db)
):
    prep_service = RoutinePreparationService(db)
    gen_service = RoutineGeneratorService()

    try:
        user_data = prep_service.get_user_data(user_id)
        candidates = prep_service.get_candidate_exercises(user_data)
        
        if not candidates:
            raise HTTPException(status_code=400, detail="수행 가능한 운동이 하나도 없습니다. 설정(부상 부위 등)을 확인해주세요.")

        strategy_text = prep_service.determine_strategy(user_data)
        
        weekly_routine_data = gen_service.generate_weekly_routine(
            user_profile=user_data["profile"],
            candidates=candidates,
            strategy=strategy_text
        )
        
        image_map = {c["id"]: c["image"] for c in candidates}
        
        DEFAULT_IMAGE_URL = "https://mofit-image.s3.ap-northeast-2.amazonaws.com/exercises/1.png"

        # DB 저장
        existing_plans = db.query(ExercisePlan).filter(ExercisePlan.user_id == user_id).all()
        
        if existing_plans:
            plan_ids = [p.id for p in existing_plans]
            
            # 자식 테이블 먼저 삭제
            db.query(ExerciseList).filter(ExerciseList.exercise_plan_id.in_(plan_ids)).delete(synchronize_session=False)
            
            # 부모 테이블 삭제
            db.query(ExercisePlan).filter(ExercisePlan.user_id == user_id).delete(synchronize_session=False)
        
        for daily in weekly_routine_data.routines:
            
            thumbnail_url = None
            for ex_item in daily.exercises:
                img = image_map.get(ex_item.exercise_id)
                if img:
                    thumbnail_url = img
                    break
                if not thumbnail_url:
                    thumbnail_url = DEFAULT_IMAGE_URL
            
            new_plan = ExercisePlan(
                user_id=user_id,
                day=daily.day,
                title=daily.title,
                description=daily.description,
                progress=False,
                image=thumbnail_url
            )
            db.add(new_plan)
            db.flush()
            
            for ex_item in daily.exercises:
                new_list = ExerciseList(
                    exercise_plan_id=new_plan.id,
                    exercise_id=ex_item.exercise_id,
                    sequence=ex_item.order
                )
                db.add(new_list)
        
        db.commit()
        print("루틴 저장 완료")
        
        return SimpleRoutineResponse(
        status="success",
        message="새로운 7일 맞춤 루틴이 생성되었습니다."
        )

    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"루틴 생성 실패: {str(e)}")