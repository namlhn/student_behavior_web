from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_code = Column(String(20), unique=True, index=True)  # MSSV
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    gender = Column(String(10))  # Male, Female, Other
    address = Column(Text)
    class_name = Column(String(100))
    academic_level = Column(String(50))
    course = Column(String(50))  # Khóa học
    major = Column(String(100))  # Chuyên ngành
    gpa = Column(Float)
    status = Column(String(20), default="Active")  # Active, Inactive, Graduated
    photo_path = Column(String(512))
    face_embedding_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # No relationships or foreign keys per current design


class StudentPhoto(Base):
    __tablename__ = "student_photos"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    photo_path = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)
