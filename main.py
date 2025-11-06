from fastapi import FastAPI, Depends, Request, Form, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import shutil
import os
import uuid
from pathlib import Path

from app.core.database import engine, Base, get_db
from app.core.config import settings
from app.db import models, crud
from app.services import enrollment, pipeline
from app.services.ai_loader import ai_engine  # ensure models are loaded

# Create tables
try:
    # ensure models are imported before create_all
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully (if not exist).")
except Exception as e:
    print(f"Error creating database tables: {e}")
    print("Please ensure MySQL server is running and database is created.")

app = FastAPI(title="Student Behavior AI Web")

base_dir = Path(__file__).resolve().parents[1]
templates_dir = str(base_dir / "templates")
templates = Jinja2Templates(directory=templates_dir)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def get_main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/enroll")
async def api_enroll_student(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    file: UploadFile = File(...),
):
    image_bytes = await file.read()
    db_student, message = enrollment.enroll_new_student(db, name, image_bytes)
    if not db_student:
        raise HTTPException(status_code=400, detail=message)
    headers = {"HX-Trigger": "studentEnrolled"}
    students = crud.get_students(db)
    return templates.TemplateResponse(
        "partials/student_list.html", {"request": request, "students": students}, headers=headers
    )


@app.get("/api/students", response_class=HTMLResponse)
async def api_get_students(request: Request, db: Session = Depends(get_db)):
    students = crud.get_students(db)
    return templates.TemplateResponse(
        "partials/student_list.html", {"request": request, "students": students}
    )


@app.post("/api/upload-video")
async def api_upload_video(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(...),
):
    video_id = str(uuid.uuid4())
    file_extension = os.path.splitext(video_file.filename)[1]
    video_filename = f"{video_id}{file_extension}"
    video_path = os.path.join(settings.UPLOAD_DIR, video_filename)

    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    print(f"Adding video {video_id} to background tasks...")
    background_tasks.add_task(pipeline.run_analysis_pipeline, video_path, video_id)

    return HTMLResponse(
        f'<p class="text-green-600 font-semibold">Đã nhận video! ID Buổi học: {video_id}</p>'
        f'<p class="text-sm text-gray-600">Hệ thống đang xử lý, vui lòng tải báo cáo ở Cột 3 sau vài phút.</p>'
    )


@app.get("/api/insights", response_class=HTMLResponse)
async def api_get_insights(request: Request, video_id: str, db: Session = Depends(get_db)):
    results_db = crud.get_analysis_results(db, video_id=video_id)
    if not results_db:
        return templates.TemplateResponse(
            "partials/dashboard.html",
            {"request": request, "video_id": video_id, "status": "pending", "results": []},
        )

    students_map = {s.id: s.name for s in crud.get_students(db)}
    results_formatted = [
        {
            "student_name": students_map.get(res.student_id, "Unknown"),
            "behavior": res.behavior,
            "emotion": res.emotion,
            "duration_seconds": res.duration_seconds,
        }
        for res in results_db
    ]

    return templates.TemplateResponse(
        "partials/dashboard.html",
        {
            "request": request,
            "video_id": video_id,
            "status": "success",
            "results": results_formatted,
        },
    )
