import os
import cv2
import torch
from collections import defaultdict
from sqlalchemy.orm import Session
from app.db import models, crud
from app.db.vector_db import vector_db_instance
from app.services.ai_loader import ai_engine
from app.core.database import SessionLocal


def run_analysis_pipeline(video_path: str, video_id: str):
    print(f"[{video_id}] Pipeline started for: {video_path}")
    db: Session = SessionLocal()
    try:
        if ai_engine.behavior_model is None:
            print(f"[{video_id}] YOLO model unavailable. Skipping processing.")
            return
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 0
        frame_interval = int(fps) if fps > 0 else 1
        frame_count = 0

        student_behavior_time = defaultdict(lambda: defaultdict(float))
        student_emotion_time = defaultdict(lambda: defaultdict(float))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_interval != 0:
                continue

            behavior_results = ai_engine.behavior_model(frame, device=ai_engine.device, verbose=False)
            for result in behavior_results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls_id = int(box.cls[0])
                    behavior_name = ai_engine.behavior_model.names[cls_id]

                    student_crop = frame[y1:y2, x1:x2]
                    if student_crop.size == 0:
                        continue

                    student_id = None
                    emotion_name = "unknown"

                    faces = []
                    if ai_engine.identity_model is not None:
                        faces = ai_engine.identity_model.get(student_crop)
                    if faces and len(faces) > 0:
                        face = sorted(
                            faces,
                            key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]),
                            reverse=True
                        )[0]

                        if getattr(face, 'embedding', None) is not None:
                            embedding = face.embedding.reshape(1, -1)
                            student_id, similarity = vector_db_instance.search_embedding(embedding)

                        fx1, fy1, fx2, fy2 = map(int, face.bbox)
                        face_crop = student_crop[max(0, fy1):min(fy2, student_crop.shape[0]), max(0, fx1):min(fx2, student_crop.shape[1])]

                        if face_crop.size > 0 and ai_engine.emotion_model is not None:
                            with torch.no_grad():
                                rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
                                img_tensor = ai_engine.emotion_transform(rgb).unsqueeze(0).to(ai_engine.device)
                                logits = ai_engine.emotion_model(img_tensor)
                                emotion_idx = logits.argmax(1).item()
                                emotion_name = ai_engine.emotion_classes[emotion_idx]

                    if student_id is not None:
                        student_behavior_time[student_id][behavior_name] += 1.0
                        student_emotion_time[student_id][emotion_name] += 1.0

        cap.release()

        for sid, behaviors in student_behavior_time.items():
            for behavior, duration in behaviors.items():
                crud.create_analysis_result(db, video_id, sid, behavior, "N/A", duration)
        for sid, emotions in student_emotion_time.items():
            for emotion, duration in emotions.items():
                crud.create_analysis_result(db, video_id, sid, "N/A", emotion, duration)

        print(f"[{video_id}] Pipeline finished and insights saved.")
    except Exception as e:
        print(f"[{video_id}] Pipeline FAILED: {e}")
    finally:
        try:
            db.close()
        except Exception:
            pass
        # Optionally: os.remove(video_path)
