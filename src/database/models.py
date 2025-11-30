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
    

class AnalyzeResult(Base):
    __tablename__ = "analyze_result"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(6))
    updated_at = Column(DateTime(6))
    
    user_id = Column(BigInteger, ForeignKey("user.id"), unique=True)
    
    average_score = Column(Float, nullable=False)
    llm_report = Column(String(255))
    
    per_agility = Column(Integer, nullable=False)
    per_body_composition = Column(Integer, nullable=False)
    per_cardio = Column(Integer, nullable=False)
    per_core = Column(Integer, nullable=False)
    per_flexibility = Column(Integer, nullable=False)
    per_strength = Column(Integer, nullable=False)

    persona = Column(String(50)) 
    
    # user = relationship("User", back_populates="analyze_result") 