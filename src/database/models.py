from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, DateTime, Boolean, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Exercise(Base):
    __tablename__ = "exercise"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(6))
    updated_at = Column(DateTime(6))

    # 2. Basic Info
    exercise_name = Column(String(100), nullable=False)
    intro = Column(String(255))
    image = Column(String(255))
    reps = Column(Integer, nullable=False)
    sets = Column(Integer, nullable=False)
    duration_sec = Column(Integer, nullable=False)
    rest_sec = Column(Integer, nullable=False)
    mets = Column(Float, nullable=False)
    difficulty = Column(String(20)) 
    equipment = Column(String(50))
    target_area = Column(String(50))
    primary_muscle = Column(String(50))
    type = Column(String(50))
    
    restricts = relationship("ExerciseRestrict", back_populates="exercise")


class ExerciseRestrict(Base):
    __tablename__ = "exercise_restricts"
    
    exercise_id = Column(BigInteger, ForeignKey("exercise.id"), primary_key=True) 
    exercise_restrict = Column(String(50), primary_key=True)
    
    exercise = relationship("Exercise", back_populates="restricts")


class Health(Base):
    __tablename__ = "health"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(6))
    updated_at = Column(DateTime(6))
    user_id = Column(BigInteger, ForeignKey("user.id"))
    birth = Column(String(10))
    gender = Column(String(10))
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    place = Column(String(20))
    proficiency = Column(String(20))
    restrict_area = Column(String(50))

    # Relations
    restricts = relationship("UserRestrict", back_populates="health", cascade="all, delete-orphan")


class UserRestrict(Base):
    __tablename__ = "user_restricts"
    
    health_id = Column(BigInteger, ForeignKey("health.id"), primary_key=True)
    user_restrict = Column(String(50), primary_key=True)

    health = relationship("Health", back_populates="restricts")


class ExercisePlan(Base):
    __tablename__ = "exercise_plan"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(6))
    updated_at = Column(DateTime(6))
    
    user_id = Column(BigInteger, ForeignKey("user.id"))
    day = Column(Integer, nullable=False)
    title = Column(String(255))
    description = Column(String(255))
    image = Column(String(255))
    progress = Column(Boolean, nullable=False)

    exercise_list = relationship("ExerciseList", back_populates="plan", cascade="all, delete-orphan") 



class ExerciseList(Base):
    __tablename__ = "exercise_list"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(6))
    updated_at = Column(DateTime(6))
    
    exercise_plan_id = Column(BigInteger, ForeignKey("exercise_plan.id"))
    exercise_id = Column(BigInteger, ForeignKey("exercise.id"))
    sequence = Column(Integer, nullable=False)

    plan = relationship("ExercisePlan", back_populates="exercise_list")
    exercise = relationship("Exercise")
    

# 추후 수정 필요
class AnalyzeResult(Base):
    __tablename__ = "analyze_result"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(6))
    updated_at = Column(DateTime(6))
    
    user_id = Column(BigInteger, ForeignKey("user.id"), unique=True) # UK 설정 확인
    
    # Text Data
    name = Column(String(255))
    description = Column(String(255))
    emoji = Column(String(255))
    llm_report = Column(String(255))
    type = Column(String(255))
    
    # Numeric Data (Scores & Percentiles)
    average_score = Column(Float, nullable=False)
    strongest_component = Column(String(255))
    strongest_percentile = Column(Integer, nullable=False)
    weakest_component = Column(String(255))
    weakest_percentile = Column(Integer, nullable=False)
    
    # Percentiles (DDL 컬럼명 그대로 유지 - 오타 주의: flexbility, peragility 등)
    per_body_composition = Column(Integer, nullable=False)
    per_cardio = Column(Integer, nullable=False)
    per_core = Column(Integer, nullable=False)
    per_flexbility = Column(Integer, nullable=False) # DDL: flexbility
    per_strength = Column(Integer, nullable=False)
    peragility = Column(Integer, nullable=False)     # DDL: peragility
    
    # Grades
    grade_agility = Column(String(255))
    grade_body_composition = Column(String(255))
    grade_cardio = Column(String(255))
    grade_core = Column(String(255))
    grade_flexibility = Column(String(255))
    grade_strength = Column(String(255))
    
    # Snapshots (측정 당시 기록)
    snap_age = Column(Integer, nullable=False)
    snapbmi = Column(Float, nullable=False)          # DDL: snapbmi
    snap_balance = Column(Float, nullable=False)
    snap_chair_squat = Column(Integer, nullable=False)
    snap_forward_fold = Column(Integer, nullable=False)
    snap_height = Column(Float, nullable=False)
    snap_plank = Column(Integer, nullable=False)
    snap_push_up = Column(Integer, nullable=False)
    snap_step_test = Column(Integer, nullable=False)
    snap_weight = Column(Float, nullable=False)