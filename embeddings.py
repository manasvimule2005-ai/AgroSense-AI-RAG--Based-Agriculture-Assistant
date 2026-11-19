"""
AgroSense AI - Unified Embeddings Manager
Provides vector embeddings across Google Gemini, Sentence-Transformers, and an instant offline Dense TF-IDF engine.
"""

import os
import numpy as np
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from src.config import AppConfig


class DenseTfidfEmbeddings:
    """Fast, zero-download, 100% offline dense embedding engine compatible with FAISS IndexFlatIP."""

    def __init__(self, max_features: int = 512):
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self._is_fitted = False

    def fit_corpus(self, texts: List[str]):
        """Fits TF-IDF vocabulary on domain text."""
        if texts:
            self.vectorizer.fit(texts)
            self._is_fitted = True

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self._is_fitted:
            self.fit_corpus(texts)
        matrix = self.vectorizer.transform(texts).toarray().astype("float32")
        # Normalize vectors for cosine similarity in FAISS
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = (matrix / norms).tolist()
        return normalized

    def embed_query(self, text: str) -> List[float]:
        if not self._is_fitted:
            # Fallback uniform vector
            return [0.0] * self.max_features
        vec = self.vectorizer.transform([text]).toarray().astype("float32")
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec[0].tolist()


def get_embedding_engine(texts_for_fitting: List[str] = None):
    """Factory to retrieve the best available embedding model."""
    provider = AppConfig.get_embedding_provider()
    gemini_key = AppConfig.get_gemini_api_key()

    # 1. Google Gemini Embeddings if requested and key is set
    if (provider == "gemini" or provider == "auto") and gemini_key:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=gemini_key
            )
        except Exception:
            pass

    # 2. Sentence-Transformers if available
    if provider == "huggingface":
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        except Exception:
            pass

    # 3. Dense TF-IDF Embeddings (Reliable, fast, offline)
    engine = DenseTfidfEmbeddings(max_features=512)
    if texts_for_fitting:
        engine.fit_corpus(texts_for_fitting)
    return engine
