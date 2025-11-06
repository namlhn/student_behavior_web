from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    results = relationship("AnalysisResult", back_populates="student")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(255), index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    behavior = Column(String(100))
    emotion = Column(String(100))
    duration_seconds = Column(Float)
    student = relationship("Student", back_populates="results")
