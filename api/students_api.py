from typing import List, Optional
from datetime import datetime
import os
from fastapi import Depends, UploadFile, File, Request
from core.fastapi_util import AppRouter, api_response_data
from core.database import get_db
from sqlalchemy.orm import Session
from db import crud
from db.models import Student
from services.ai_loader import ai_engine
from db.vector_db import vector_db_instance
from core.config import settings
from core.constants import Result

router = AppRouter()


def student_to_dict(s: Student):
    return {
        "id": s.id,
        "student_code": s.student_code,
        "name": s.name,
        "email": s.email,
        "phone": s.phone,
        "date_of_birth": s.date_of_birth.isoformat() if s.date_of_birth else None,
        "gender": s.gender,
        "address": s.address,
        "class_name": s.class_name,
        "academic_level": s.academic_level,
        "course": s.course,
        "major": s.major,
        "gpa": s.gpa,
        "status": s.status,
        "photo_path": s.photo_path,
        "face_embedding_count": s.face_embedding_count,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }


@router.get("/students")
async def list_students(skip: int = 0, limit: int = 100, search: str = None, status: str = None, db: Session = Depends(get_db)):
    items = crud.get_students(db, skip=skip, limit=limit, search=search, status=status)
    total = crud.get_students_count(db, search=search, status=status)
    return api_response_data(Result.SUCCESS.value, {
        "items": [student_to_dict(s) for s in items],
        "total": total,
        "skip": skip,
        "limit": limit
    })


@router.get("/students/{student_id}")
async def get_student_detail(student_id: int, db: Session = Depends(get_db)):
    s = crud.get_student(db, student_id)
    if not s:
        return api_response_data(Result.ERROR_NOT_FOUND.value)
    return api_response_data(Result.SUCCESS.value, student_to_dict(s))


@router.get("/students/{student_id}/photos")
async def list_student_photos(student_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    s = crud.get_student(db, student_id)
    if not s:
        return api_response_data(Result.ERROR_NOT_FOUND.value)
    items = crud.get_student_photos(db, student_id, skip=skip, limit=limit)
    reply = [
        {
            "id": p.id,
            "student_id": p.student_id,
            "photo_path": p.photo_path,
            "created_at": p.created_at.isoformat() if getattr(p, "created_at", None) else None,
        }
        for p in items
    ]
    return api_response_data(Result.SUCCESS.value, reply)


@router.post("/students")
async def create_student(request: Request, db: Session = Depends(get_db)):
    ctype = request.headers.get("content-type", "")
    if "application/json" in ctype:
        data = await request.json() or {}
    else:
        form = await request.form()
        data = dict(form)
    
    # Extract and validate required fields
    name = data.get("name")
    if not name:
        return api_response_data(Result.ERROR_PARAMS.value, message="Name is required")
    
    # Check for existing student
    student_code = data.get("student_code")
    email = data.get("email")
    
    if student_code and crud.get_student_by_code(db, student_code):
        return api_response_data(Result.ERROR_EXIST.value, message="Student code already exists")
    
    if email and crud.get_student_by_email(db, email):
        return api_response_data(Result.ERROR_EXIST.value, message="Email already exists")
    
    # Parse date if provided
    date_of_birth = None
    if data.get("date_of_birth"):
        try:
            from datetime import datetime
            date_of_birth = datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date()
        except ValueError:
            return api_response_data(Result.ERROR_PARAMS.value, message="Invalid date format. Use YYYY-MM-DD")
    
    # Parse GPA if provided
    gpa = None
    if data.get("gpa"):
        try:
            gpa = float(data["gpa"])
        except ValueError:
            return api_response_data(Result.ERROR_PARAMS.value, message="Invalid GPA format")
    
    # Create student with all fields
    student_data = {
        "student_code": student_code,
        "name": name,
        "email": email,
        "phone": data.get("phone"),
        "date_of_birth": date_of_birth,
        "gender": data.get("gender"),
        "address": data.get("address"),
        "class_name": data.get("class_name"),
        "academic_level": data.get("academic_level"),
        "course": data.get("course"),
        "major": data.get("major"),
        "gpa": gpa,
        "status": data.get("status", "Active")
    }
    
    s = crud.create_student(db, **student_data)
    return api_response_data(Result.SUCCESS.value, student_to_dict(s))


@router.put("/students/{student_id}")
async def update_student(student_id: int, request: Request, db: Session = Depends(get_db)):
    ctype = request.headers.get("content-type", "")
    if "application/json" in ctype:
        data = await request.json() or {}
    else:
        form = await request.form()
        data = dict(form)
    
    # Check if student exists
    existing_student = crud.get_student(db, student_id)
    if not existing_student:
        return api_response_data(Result.ERROR_NOT_FOUND.value)
    
    # Check for conflicts with other students
    student_code = data.get("student_code")
    email = data.get("email")
    
    if student_code and student_code != existing_student.student_code:
        if crud.get_student_by_code(db, student_code):
            return api_response_data(Result.ERROR_EXIST.value, message="Student code already exists")
    
    if email and email != existing_student.email:
        if crud.get_student_by_email(db, email):
            return api_response_data(Result.ERROR_EXIST.value, message="Email already exists")
    
    # Parse date if provided
    date_of_birth = None
    if data.get("date_of_birth"):
        try:
            from datetime import datetime
            date_of_birth = datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date()
        except ValueError:
            return api_response_data(Result.ERROR_PARAMS.value, message="Invalid date format. Use YYYY-MM-DD")
    
    # Parse GPA if provided
    gpa = None
    if data.get("gpa"):
        try:
            gpa = float(data["gpa"]) if data["gpa"] else None
        except ValueError:
            return api_response_data(Result.ERROR_PARAMS.value, message="Invalid GPA format")
    
    # Prepare update data (only include fields that are provided)
    update_data = {}
    for field in ["student_code", "name", "email", "phone", "gender", "address", 
                  "class_name", "academic_level", "course", "major", "status"]:
        if field in data:
            update_data[field] = data[field]
    
    if date_of_birth is not None:
        update_data["date_of_birth"] = date_of_birth
    if gpa is not None:
        update_data["gpa"] = gpa
    
    s = crud.update_student(db, student_id, **update_data)
    return api_response_data(Result.SUCCESS.value, student_to_dict(s))


@router.delete("/students/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_student(db, student_id)
    if not ok:
        return api_response_data(Result.ERROR_NOT_FOUND.value)
    return api_response_data(Result.SUCCESS.value, {"success": True})


@router.post("/students/{student_id}/face")
async def upload_student_face(student_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    s = crud.get_student(db, student_id)
    if not s:
        return api_response_data(Result.ERROR_NOT_FOUND.value)

    data = await file.read()
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    base_name = f"{student_id}_{ts}_{file.filename}"
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(settings.UPLOAD_DIR, base_name)
    with open(save_path, "wb") as f:
        f.write(data)
    web_photo_path = f"/uploads/{base_name}"
    try:
        crud.create_student_photo(db, student_id, web_photo_path)
    except Exception:
        pass

    if ai_engine.identity_model is not None:
        import cv2
        import numpy as np
        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None:
            faces = ai_engine.identity_model.get(img)
            if faces and len(faces) == 1:
                embedding = getattr(faces[0], "embedding", None)
                if embedding is not None:
                    vector_db_instance.add_embedding(student_id, embedding.reshape(1, -1))
                    s = crud.update_student(db, student_id, photo_path=web_photo_path, face_embedding_count_inc=1)
                    return api_response_data(Result.SUCCESS.value, student_to_dict(s))
    # Fallback: save photo only
    s = crud.update_student(db, student_id, photo_path=web_photo_path)
    return api_response_data(Result.SUCCESS.value, student_to_dict(s))


@router.post("/students/{student_id}/faces/batch")
async def upload_student_faces_batch(student_id: int, files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    s = crud.get_student(db, student_id)
    if not s:
        return api_response_data(Result.ERROR_NOT_FOUND.value)

    if not files or len(files) == 0:
        return api_response_data(Result.ERROR_FILE_NONE.value)

    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    added = []
    embed_added = 0

    for i, file in enumerate(files):
        data = await file.read()
        base_name = f"{student_id}_{ts}_{i}_{file.filename}"
        save_path = os.path.join(settings.UPLOAD_DIR, base_name)
        with open(save_path, "wb") as f:
            f.write(data)
        web_photo_path = f"/uploads/{base_name}"
        try:
            rec = crud.create_student_photo(db, student_id, web_photo_path)
        except Exception:
            rec = None
        added.append({
            "photo_path": web_photo_path,
            "id": getattr(rec, "id", None)
        })

        if ai_engine.identity_model is not None:
            try:
                import cv2
                import numpy as np
                nparr = np.frombuffer(data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is not None:
                    faces = ai_engine.identity_model.get(img)
                    if faces and len(faces) == 1:
                        embedding = getattr(faces[0], "embedding", None)
                        if embedding is not None:
                            vector_db_instance.add_embedding(student_id, embedding.reshape(1, -1))
                            embed_added += 1
            except Exception:
                pass

    if embed_added:
        s = crud.update_student(db, student_id, face_embedding_count_inc=embed_added)

    reply = {
        "student": student_to_dict(s),
        "added": added,
        "embeddings_added": embed_added,
    }
    return api_response_data(Result.SUCCESS.value, reply)
