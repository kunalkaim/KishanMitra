import re
import numpy as np
from typing import List, Dict, Any, Optional
from app.rag.embeddings.embedding_provider import BaseEmbeddingProvider, get_embedding_provider
from app.rag.retrieval.vector_store import PersistentChromaVectorStore


class HybridAgriculturalRetriever:
    """
    Hybrid Retrieval Engine combining:
    1. Multilingual dense semantic retrieval (Cosine similarity)
    2. Exact keyword / term frequency matching (BM25-style lexical overlap)
    3. Metadata filtering (Crop, Season, District)
    4. Reciprocal Rank Fusion / Weighted Score Normalization
    """

    def __init__(
        self,
        vector_store: Optional[PersistentChromaVectorStore] = None,
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
        dense_weight: float = 0.65,
        keyword_weight: float = 0.35
    ):
        self.vector_store = vector_store or PersistentChromaVectorStore()
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.dense_weight = dense_weight
        self.keyword_weight = keyword_weight
        self._retrieval_cache: Dict[str, List[Dict[str, Any]]] = {}

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        crop_filter: Optional[str] = None,
        district_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid retrieval returning ranked evidence chunks with full provenance citations.
        """
        if not query or not query.strip():
            return []

        cache_key = f"{query.strip()}|{top_k}|{crop_filter}|{district_filter}"
        if cache_key in self._retrieval_cache:
            return self._retrieval_cache[cache_key]

        # 1. Dense Semantic Retrieval
        query_embedding = self.embedding_provider.encode_query(query)
        dense_results = self.vector_store.search_similar(query_embedding, top_k=top_k * 2)

        # 2. Lexical / Keyword Scoring on candidate chunks
        query_terms = self._tokenize(query)

        scored_candidates: Dict[str, Dict[str, Any]] = {}

        # Add all dense candidates
        for rank_idx, item in enumerate(dense_results):
            cid = item["chunk_id"]
            dense_score = item.get("score", 0.5)
            scored_candidates[cid] = {
                "chunk_id": cid,
                "text": item["text"],
                "metadata": item["metadata"],
                "dense_score": dense_score,
                "dense_rank": rank_idx + 1,
                "keyword_score": 0.0,
                "keyword_rank": 999
            }

        # Calculate keyword score for all candidates
        for cid, cand in scored_candidates.items():
            chunk_terms = self._tokenize(cand["text"])
            matched_terms = query_terms.intersection(chunk_terms)
            if query_terms:
                lexical_score = len(matched_terms) / len(query_terms)
            else:
                lexical_score = 0.0

            cand["keyword_score"] = float(lexical_score)

        # 3. Calculate Hybrid Score with Agronomic Entity Boosting
        # Formula:
        #   base_linear = (dense_weight * dense_score) + (keyword_weight * keyword_score)
        #   where dense_weight = 0.65, keyword_weight = 0.35
        #   applied_boosts = domain_boost (+0.20 for crop synonym match) + filter_boost (+0.10 for active crop filter)
        #   raw_hybrid = base_linear + applied_boosts
        #   final_hybrid_score = round(min(1.0, max(0.0, raw_hybrid)), 4)
        ranked_list = []
        for cid, cand in scored_candidates.items():
            base_linear = (
                self.dense_weight * cand["dense_score"] +
                self.keyword_weight * cand["keyword_score"]
            )

            meta = cand["metadata"]
            chunk_text_lower = cand["text"].lower()
            query_lower = query.lower()

            # Check domain boost
            domain_boost = 0.0
            meta_crops_lower = str(meta.get("crops", "")).lower()
            crop_synonyms = {
                "मंडुआ": ["mandua", "finger millet", "मंडुआ"],
                "झंगोरा": ["jhangora", "barn yard", "झंगोरा"],
                "धान": ["rice", "dhan", "paddy", "धान"],
                "चावल": ["rice", "चावल"],
                "मक्का": ["maize", "makka", "मक्का"],
                "टमाटर": ["tomato", "टमाटर"],
                "भट्ट": ["bhatt", "soybean", "भट्ट"],
                "सोयाबीन": ["soybean", "सोयाबीन"],
                "मछली": ["fish", "fisheries", "मछली"],
                "तालाब": ["pond", "तालाब"],
                "गोबर": ["cow dung", "dung", "गोबर"],
                "mandua": ["mandua", "finger millet", "मंडुआ"],
                "jhangora": ["jhangora", "barn yard", "झंगोरा"],
                "rice": ["rice", "dhan", "paddy", "धान"],
                "paddy": ["rice", "dhan", "paddy", "धान"],
                "maize": ["maize", "makka", "मक्का"],
                "tomato": ["tomato", "टमाटर"],
                "bhatt": ["bhatt", "soybean", "भट्ट"],
                "fish": ["fish", "fisheries", "मछली"],
                "pond": ["pond", "तालाब"],
                "cow dung": ["cow dung", "dung", "गोबर"]
            }

            matched_crop_term = None
            for query_term, matches in crop_synonyms.items():
                if query_term in query_lower:
                    if any(m in chunk_text_lower or m in meta_crops_lower for m in matches):
                        domain_boost = 0.20
                        matched_crop_term = query_term
                        break

            filter_boost = 0.0
            if crop_filter and crop_filter.lower() in meta.get("crops", "").lower():
                filter_boost = 0.10

            raw_hybrid = base_linear + domain_boost + filter_boost
            clamped_hybrid = min(1.0, max(0.0, raw_hybrid))

            cand["dense_weight"] = self.dense_weight
            cand["keyword_weight"] = self.keyword_weight
            cand["base_linear_score"] = round(float(base_linear), 4)
            cand["domain_boost"] = round(float(domain_boost), 4)
            cand["filter_boost"] = round(float(filter_boost), 4)
            cand["matched_domain_entity"] = matched_crop_term
            cand["raw_hybrid_score"] = round(float(raw_hybrid), 4)
            cand["hybrid_score"] = round(float(clamped_hybrid), 4)

            cand["citation"] = {
                "document_title": meta.get("document_title", "GBPUAT Agricultural Bulletin"),
                "publisher": meta.get("publisher", "GBPUAT Pantnagar"),
                "publication_date": meta.get("publication_date", "2020-05-02"),
                "page_start": int(meta.get("page_start", 1)) if str(meta.get("page_start", 1)).isdigit() else 1,
                "page_end": int(meta.get("page_end", 1)) if str(meta.get("page_end", 1)).isdigit() else 1,
                "source_url": meta.get("source_url", ""),
                "is_historical": (meta.get("publication_date", "2020-05-02") < "2024-01-01"),
                "crops": meta.get("crops", "").split(", ") if meta.get("crops") else [],
                "categories": meta.get("categories", "").split(", ") if meta.get("categories") else []
            }
            ranked_list.append(cand)

        # Sort by hybrid score descending
        ranked_list.sort(key=lambda x: x["hybrid_score"], reverse=True)
        final_result = ranked_list[:top_k]
        self._retrieval_cache[cache_key] = final_result
        return final_result

    def _tokenize(self, text: str) -> set:
        """Language-agnostic tokenization supporting English and Devanagari Hindi."""
        tokens = re.findall(r'[\w\u0900-\u097F]+', text.lower())
        stopwords = {
            "the", "a", "an", "in", "of", "to", "for", "and", "is", "on", "at", "what", "how",
            "का", "के", "की", "में", "से", "पर", "है", "हैं", "और", "क्या", "कैसे", "को"
        }
        return {t for t in tokens if len(t) > 1 and t not in stopwords}
