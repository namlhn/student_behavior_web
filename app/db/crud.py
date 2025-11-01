from sqlalchemy.orm import Session
from . import models

# === Student ===
def get_student_by_name(db: Session, name: str):
    return db.query(models.Student).filter(models.Student.name == name).first()

def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).offset(skip).limit(limit).all()

def create_student(db: Session, name: str):
    db_student = models.Student(name=name)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# === AnalysisResult ===
def create_analysis_result(db: Session, video_id: str, student_id: int, behavior: str, emotion: str, duration: float):
    db_result = models.AnalysisResult(
        video_id=video_id,
        student_id=student_id,
        behavior=behavior,
        emotion=emotion,
        duration_seconds=duration
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def get_analysis_results(db: Session, video_id: str):
    return db.query(models.AnalysisResult).filter(models.AnalysisResult.video_id == video_id).all()
