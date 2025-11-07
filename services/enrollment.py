import cv2
import numpy as np
from sqlalchemy.orm import Session
from db import crud
from db.vector_db import vector_db_instance
from services.ai_loader import ai_engine

def enroll_new_student(db: Session, name: str, image_bytes: bytes):
    db_student = crud.get_student_by_name(db, name=name)
    if not db_student:
        db_student = crud.create_student(db, name=name)

    student_id = db_student.id

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None, "Invalid image file."

    if ai_engine.identity_model is None:
        return None, "Identity model unavailable. Please ensure InsightFace is installed and configured."
    faces = ai_engine.identity_model.get(img)
    if not faces or len(faces) == 0:
        return None, "No face found in the image."
    if len(faces) > 1:
        return None, "Multiple faces found. Please upload a clear portrait."

    embedding = faces[0].embedding
    if embedding is None:
        return None, "Could not extract embedding."

    vector_db_instance.add_embedding(student_id, embedding.reshape(1, -1))
    return db_student, "Enrollment successful."
