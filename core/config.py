from pydantic_settings import BaseSettings
from pathlib import Path
from typing import ClassVar, Dict, Any

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:NextViet2024@147.93.158.214:3306/student_ai_db"
    EMBEDDING_DIM: int = 512
    # Resolve absolute paths relative to the project root
    _BASE_DIR: Path = Path(__file__).resolve().parents[1]
    FAISS_INDEX_FILE: str = str(_BASE_DIR / "data_storage" / "faiss_index.bin")
    METADATA_FILE: str = str(_BASE_DIR / "data_storage" / "metadata.json")
    UPLOAD_DIR: str = str(_BASE_DIR / "data_storage" / "uploads")
    FAISS_THRESHOLD_COSINE: float = 0.6
    LOGGER_CONFIG: ClassVar[Dict[str, Any]] = {
    'log_dir': 'log'
    }

    # Logging/detail toggles used by fastapi_util
    log_request_body: bool = True
    max_response_length: int = 500
    max_request_body_length: int = 500
    log_response: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
