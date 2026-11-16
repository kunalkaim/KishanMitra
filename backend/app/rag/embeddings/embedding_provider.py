import os
import abc
import numpy as np
from typing import List, Optional


class BaseEmbeddingProvider(abc.ABC):
    """Abstract interface for RAG embedding providers."""

    @abc.abstractmethod
    def encode_documents(self, texts: List[str]) -> np.ndarray:
        """Encodes a batch of document texts into normalized vectors."""
        pass

    @abc.abstractmethod
    def encode_query(self, query: str) -> np.ndarray:
        """Encodes a single query text into a normalized vector."""
        pass

    @property
    @abc.abstractmethod
    def dimension(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        pass


class SentenceTransformersEmbeddingProvider(BaseEmbeddingProvider):
    """
    Multilingual Dense Embedding Provider using Sentence Transformers.
    Default model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (384 dimensions)
    Supports English, Hindi, and regional agronomic terminology.
    """

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self._model_name = model_name
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()

    def encode_documents(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(embeddings, dtype=np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        embedding = self.model.encode(query, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(embedding, dtype=np.float32)

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_name(self) -> str:
        return self._model_name


class FastAgriculturalVectorEmbeddingProvider(BaseEmbeddingProvider):
    """
    High-reliability, deterministic local vector provider using character & word n-grams
    with L2-normalized dense projection. Guaranteed zero external network dependence,
    instant startup, and full multilingual (English + Hindi Devanagari) support.
    """

    def __init__(self, dimension: int = 384):
        self._dimension = dimension
        self._model_name = "kisanmitra-multilingual-dense-v1"
        from sklearn.feature_extraction.text import HashingVectorizer
        # 384-dimensional multilingual character & word ngram projection
        self.vectorizer = HashingVectorizer(
            n_features=dimension,
            analyzer="char_wb",
            ngram_range=(3, 5),
            norm="l2",
            alternate_sign=False
        )

    def encode_documents(self, texts: List[str]) -> np.ndarray:
        matrix = self.vectorizer.transform(texts).toarray()
        # Ensure row-wise L2 normalization
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (matrix / norms).astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        vec = self.vectorizer.transform([query]).toarray()[0]
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.astype(np.float32)

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_name(self) -> str:
        return self._model_name


def get_embedding_provider(preferred: Optional[str] = None) -> BaseEmbeddingProvider:
    """
    Factory function returning the active embedding provider.
    Tries SentenceTransformers first, with graceful fallback to FastAgriculturalVector.
    """
    provider_type = (preferred or os.getenv("RAG_EMBEDDING_PROVIDER", "auto")).lower()
    
    if provider_type in ["sentence-transformers", "local", "auto"]:
        try:
            return SentenceTransformersEmbeddingProvider()
        except Exception as e:
            print(f"[RAG] SentenceTransformers not initialized ({e}). Using FastAgriculturalVectorEmbeddingProvider.")
            return FastAgriculturalVectorEmbeddingProvider()
    elif provider_type == "fast":
        return FastAgriculturalVectorEmbeddingProvider()
    else:
        return FastAgriculturalVectorEmbeddingProvider()
