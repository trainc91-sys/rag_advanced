"""
embeddings.py
-------------
Bọc mô hình sentence-transformers tiếng Việt để chuyển câu hỏi thành vector,
dùng cho bước tìm kiếm vector trong Neo4j (Bước 2).
"""

from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

import config


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Nạp mô hình embedding một lần duy nhất (cache) để tránh load lại nhiều lần."""
    print(f"[embeddings] Đang nạp mô hình: {config.EMBEDDING_MODEL_NAME} ...")
    model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
    print("[embeddings] Nạp mô hình thành công.")
    return model


def embed_text(text: str) -> List[float]:
    """Chuyển một chuỗi văn bản thành vector embedding (list[float])."""
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return np.asarray(vector, dtype=float).tolist()


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Chuyển một danh sách văn bản thành danh sách vector embedding."""
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vectors, dtype=float).tolist()
