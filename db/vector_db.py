import os
import json
import faiss
import numpy as np
from core.config import settings

class VectorDB:
    def __init__(self):
        self.dim = settings.EMBEDDING_DIM
        self.index_file = settings.FAISS_INDEX_FILE
        self.metadata_file = settings.METADATA_FILE

        self.index = faiss.IndexIDMap(faiss.IndexFlatIP(self.dim))
        self.metadata = {}

        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            print("Loading existing FAISS index...")
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                try:
                    self.metadata = json.load(f)
                except Exception:
                    self.metadata = {}
        else:
            print("Creating new FAISS index...")
            self._ensure_parent_dirs()
            self._save()

    def _ensure_parent_dirs(self):
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)

    def _save(self):
        self._ensure_parent_dirs()
        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f)

    def add_embedding(self, student_id: int, vector: np.ndarray):
        vec = vector.astype('float32')
        faiss.normalize_L2(vec)
        faiss_id = np.array([student_id], dtype=np.int64)
        self.index.add_with_ids(vec, faiss_id)
        sid = str(student_id)
        self.metadata[sid] = self.metadata.get(sid, 0) + 1
        self._save()
        print(f"Added embedding for student {student_id}. Total vectors: {self.index.ntotal}")

    def search_embedding(self, vector: np.ndarray, k: int = 1):
        if self.index.ntotal == 0:
            return None, 0.0
        vec = vector.astype('float32')
        faiss.normalize_L2(vec)
        distances, faiss_ids = self.index.search(vec, k)
        if faiss_ids.size == 0:
            return None, 0.0
        student_id = int(faiss_ids[0][0])
        similarity = float(distances[0][0])
        if similarity < settings.FAISS_THRESHOLD_COSINE:
            return None, similarity
        return student_id, similarity

vector_db_instance = VectorDB()
