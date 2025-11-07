from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime, date
from . import models

# === Student ===
def get_student_by_name(db: Session, name: str):
    return db.query(models.Student).filter(models.Student.name == name).first()

def get_student_by_code(db: Session, student_code: str):
    return db.query(models.Student).filter(models.Student.student_code == student_code).first()

def get_student_by_email(db: Session, email: str):
    return db.query(models.Student).filter(models.Student.email == email).first()

def get_students(db: Session, skip: int = 0, limit: int = 100, search: str = None, status: str = None):
    query = db.query(models.Student)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Student.name.like(search_term),
                models.Student.student_code.like(search_term),
                models.Student.email.like(search_term),
                models.Student.class_name.like(search_term)
            )
        )
    
    if status:
        query = query.filter(models.Student.status == status)
    
    return query.order_by(models.Student.created_at.desc()).offset(skip).limit(limit).all()

def get_students_count(db: Session, search: str = None, status: str = None):
    query = db.query(models.Student)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Student.name.like(search_term),
                models.Student.student_code.like(search_term),
                models.Student.email.like(search_term),
                models.Student.class_name.like(search_term)
            )
        )
    
    if status:
        query = query.filter(models.Student.status == status)
    
    return query.count()

def create_student(db: Session, **kwargs):
    # Auto generate student code if not provided
    if not kwargs.get('student_code'):
        # Generate format: SV + year + sequential number
        year = datetime.now().year
        last_student = db.query(models.Student).filter(
            models.Student.student_code.like(f"SV{year}%")
        ).order_by(models.Student.student_code.desc()).first()
        
        if last_student and last_student.student_code:
            try:
                last_num = int(last_student.student_code[6:])  # Extract number after "SV2024"
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        kwargs['student_code'] = f"SV{year}{new_num:04d}"
    
    db_student = models.Student(**kwargs)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def update_student(db: Session, student_id: int, **kwargs):
    student = get_student(db, student_id)
    if not student:
        return None
    
    # Handle face_embedding_count_inc separately
    face_embedding_count_inc = kwargs.pop('face_embedding_count_inc', 0)
    if face_embedding_count_inc:
        student.face_embedding_count = (student.face_embedding_count or 0) + face_embedding_count_inc
    
    # Update other fields
    for key, value in kwargs.items():
        if value is not None and hasattr(student, key):
            setattr(student, key, value)
    
    student.updated_at = datetime.utcnow()
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

def delete_student(db: Session, student_id: int):
    student = get_student(db, student_id)
    if not student:
        return False
    db.delete(student)
    db.commit()
    return True

# === StudentPhoto ===
def create_student_photo(db: Session, student_id: int, photo_path: str):
    rec = models.StudentPhoto(student_id=student_id, photo_path=photo_path)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def get_student_photos(db: Session, student_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.StudentPhoto)
        .filter(models.StudentPhoto.student_id == student_id)
        .order_by(models.StudentPhoto.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
