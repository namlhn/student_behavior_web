from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:NextViet2024@147.93.158.214:3306/student_ai_db"
    EMBEDDING_DIM: int = 512
    # Resolve absolute paths relative to the project root
    # app/core/config.py -> app -> project_root
    _BASE_DIR: Path = Path(__file__).resolve().parents[2]
    FAISS_INDEX_FILE: str = str(_BASE_DIR / "data_storage" / "faiss_index.bin")
    METADATA_FILE: str = str(_BASE_DIR / "data_storage" / "metadata.json")
    UPLOAD_DIR: str = str(_BASE_DIR / "data_storage" / "uploads")
    FAISS_THRESHOLD_COSINE: float = 0.6

    class Config:
        env_file = ".env"

settings = Settings()
