from fastapi import FastAPI
import os
from pathlib import Path
from core.database import engine, Base
from core.config import settings
from api import routers as app_router_api
from web.router import router_web
from fastapi.staticfiles import StaticFiles
from core.middleware import apply_middlewares
from db import models as db_models  # noqa: F401

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully (if not exist).")
except Exception as e:
    print(f"Error creating database tables: {e}")
    print("Please ensure MySQL server is running and database is created.")

app = FastAPI(title="Student Behavior AI Web", docs_url="/docs", redoc_url="/redoc")

# Middlewares (CORS, Request ID)
apply_middlewares(app, settings)

# Routers
app.include_router(app_router_api.router_api, prefix="/api")
app.include_router(router_web)

# Static and uploads
base_dir = Path(__file__).resolve().parent
web_static = base_dir / "web" / "static"
static_dir = web_static if web_static.exists() else (base_dir / "static")
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


