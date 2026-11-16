import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple


class PersistentChromaVectorStore:
    """
    Persistent ChromaDB vector store adapter.
    Persists vectors and metadata into backend/storage/vector_index.
    Keeps vector IDs strictly linked to PostgreSQL/SQLite KnowledgeChunk IDs.
    """

    def __init__(self, persist_dir: Optional[str] = None, collection_name: str = "kisanmitra_kb"):
        self.persist_dir = persist_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "storage", "vector_index"
        )
        os.makedirs(self.persist_dir, exist_ok=True)
        self.collection_name = collection_name
        self._init_db()

    def _init_db(self):
        import chromadb
        from chromadb.config import Settings
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "KisanMitra Multilingual Agricultural Knowledge Base"}
        )

    def add_chunks(
        self,
        chunk_ids: List[str],
        embeddings: np.ndarray,
        texts: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        """Adds or updates chunks idempotently."""
        # Clean metadata values to primitive types for ChromaDB
        cleaned_metas = []
        for meta in metadatas:
            clean = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean[k] = v
                elif isinstance(v, list):
                    clean[k] = ", ".join(str(item) for item in v)
                elif v is None:
                    clean[k] = ""
                else:
                    clean[k] = str(v)
            cleaned_metas.append(clean)

        emb_list = embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings
        self.collection.upsert(
            ids=chunk_ids,
            embeddings=emb_list,
            documents=texts,
            metadatas=cleaned_metas
        )

    def search_similar(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Dense similarity retrieval returning chunk metadata and distance/score."""
        q_emb = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding
        
        where_clause = None
        if filter_dict:
            # Simple Chroma where clause
            if len(filter_dict) == 1:
                k, v = list(filter_dict.items())[0]
                where_clause = {k: v}
            elif len(filter_dict) > 1:
                where_clause = {"$and": [{k: v} for k, v in filter_dict.items()]}

        results = self.collection.query(
            query_embeddings=[q_emb],
            n_results=top_k,
            where=where_clause
        )

        output = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(ids)

            for i in range(len(ids)):
                dist = distances[i]
                # Convert cosine distance to similarity score in [0.0, 1.0]
                score = max(0.0, 1.0 - (dist / 2.0))
                output.append({
                    "chunk_id": ids[i],
                    "text": docs[i],
                    "metadata": metas[i],
                    "score": round(float(score), 4),
                    "distance": round(float(dist), 4)
                })
        return output

    def delete_document_chunks(self, document_id: str):
        """Removes all vector embeddings belonging to a specific document."""
        self.collection.delete(where={"document_id": document_id})

    def count(self) -> int:
        return self.collection.count()
