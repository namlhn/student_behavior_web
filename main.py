from fastapi import FastAPI
import os
from pathlib import Path
from core.fastapi_logger import log_data
from core.database import engine, Base
from core.config import settings
from app import routers as app_router_api
# Create tables
try:
    # ensure models are imported before create_all
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully (if not exist).")
except Exception as e:
    print(f"Error creating database tables: {e}")
    print("Please ensure MySQL server is running and database is created.")

app = FastAPI(title="Student Behavior AI Web", docs_url="/docs", redoc_url="/redoc")

app.include_router(app_router_api.router_api, prefix="/api")

base_dir = Path(__file__).resolve().parents[1]
#templates_dir = str(base_dir / "templates")
#templates = Jinja2Templates(directory=templates_dir)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

from datetime import datetime
log_data.data('begin data start %s', datetime.now().isoformat())
log_data.info('begin info start %s', datetime.now().isoformat())

