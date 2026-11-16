import os
import re
from typing import Dict, Any, List, Optional
from app.rag.retrieval.hybrid_retriever import HybridAgriculturalRetriever
from app.rag.generation.rag_prompt import AGRICULTURAL_RAG_SYSTEM_PROMPT, build_rag_user_prompt
from app.rag.generation.llm_provider import (
    BaseLLMProvider,
    get_llm_provider,
    RetrievalOnlyLLMProvider,
    GeminiLLMProvider
)
from app.rag.generation.gemini_provider import (
    GeminiAuthError,
    GeminiQuotaError,
    GeminiTransientError,
    GeminiProviderError
)


class AgriculturalAnswerGenerator:
    """
    Evidence-grounded RAG answer generator for KisanMitra.
    Coordinates hybrid retrieval, evidence grounding, temporary source identifiers ([S1], [S2]),
    strict backend citation verification, and resilient transparent fallback.
    """

    def __init__(
        self,
        retriever: Optional[HybridAgriculturalRetriever] = None,
        llm_provider: Optional[BaseLLMProvider] = None
    ):
        self.retriever = retriever or HybridAgriculturalRetriever()
        self.llm_provider = llm_provider or get_llm_provider()

    def generate_answer(
        self,
        query: str,
        farmer_context: Optional[Dict[str, Any]] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        q_clean = query.strip()
        q_lower = q_clean.lower()

        # 1. Guard against queries expecting live real-time streams
        live_triggers = [
            "live weather", "today's temperature", "current weather", "live rainfall", "today's rainfall",
            "current temperature", "live mandi", "today's mandi", "mandi price today", "market price today",
            "आज का मौसम", "आज का तापमान", "आज का मंडी भाव", "आज की बारिश"
        ]
        if any(w in q_lower for w in live_triggers) or (("today" in q_lower or "current" in q_lower) and any(w in q_lower for w in ["weather", "temperature", "rainfall", "mandi", "price"])):
            return {
                "answer": (
                    "Namaste Farmer! Please note that the Agricultural Knowledge Base indexes verified static research bulletins "
                    "from GBPUAT Pantnagar (such as seasonal advisories and package of practices) and does not provide dynamic, live-streaming data. "
                    "For real-time local weather forecasts, please check the 'Weather Forecast' section, and for live mandi auction prices across Uttarakhand, "
                    "please visit the 'Market Intelligence' tab on your KisanMitra dashboard."
                ),
                "answer_mode": "live_data_disclaimer",
                "retrieval_status": "live_data_out_of_scope",
                "generation_status": "direct_guardrail",
                "sources": [],
                "has_historical_warning": False,
                "provider_name": self.llm_provider.provider_name
            }

        # 2. Hybrid Evidence Retrieval
        crop_hint = farmer_context.get("crop") if farmer_context else None
        district_hint = farmer_context.get("district") if farmer_context else None

        chunks = self.retriever.retrieve(
            query=q_clean,
            top_k=top_k,
            crop_filter=crop_hint,
            district_filter=district_hint
        )

        # 3. Check for Insufficient Evidence
        if not chunks or (chunks and chunks[0]["hybrid_score"] < 0.32):
            return {
                "answer": (
                    f"Namaste Farmer. The current KisanMitra knowledge base does not contain sufficient verified evidence "
                    f"to answer your question regarding '{q_clean}'.\n\n"
                    "Our verified knowledge corpus currently indexes GBPUAT Pantnagar agricultural publications covering "
                    "Kharif season cereals (Rice, Maize), hill millets (Mandua, Jhangora), pulses (Bhatt, Arhar), and seasonal vegetables. "
                    "Please consult your local Krishi Vigyan Kendra (KVK) or Block Agriculture Officer for specific unlisted guidance."
                ),
                "answer_mode": "insufficient_evidence",
                "retrieval_status": "insufficient_evidence",
                "generation_status": "insufficient_evidence",
                "sources": [],
                "has_historical_warning": False,
                "provider_name": self.llm_provider.provider_name
            }

        # Map chunks into source identifiers [S1], [S2] ...
        source_map = {}
        has_historical = False
        all_sources = []
        for idx, c in enumerate(chunks):
            s_id = f"S{idx + 1}"
            cit = c["citation"]
            if cit.get("is_historical"):
                has_historical = True
            
            src_obj = {
                "source_id": s_id,
                "document_title": cit["document_title"],
                "publisher": cit["publisher"],
                "publication_date": cit["publication_date"],
                "page_start": cit["page_start"],
                "page_end": cit["page_end"],
                "source_url": cit.get("source_url"),
                "retrieval_score": round(c["hybrid_score"] * 100, 1),
                "snippet": c["text"][:280] + ("..." if len(c["text"]) > 280 else ""),
                "is_historical": cit["is_historical"]
            }
            source_map[s_id] = src_obj
            all_sources.append(src_obj)

        # 4. Answer Generation (Gemini LLM vs. Retrieval-Only Mode)
        user_prompt = build_rag_user_prompt(q_clean, chunks, farmer_context)

        answer_text = ""
        answer_mode = "rag"
        generation_status = "llm_generated"
        suggested_follow_ups = []
        verified_sources = []

        if isinstance(self.llm_provider, RetrievalOnlyLLMProvider):
            answer_text = self._format_retrieval_only_answer(q_clean, chunks, has_historical)
            answer_mode = "retrieval_only"
            generation_status = "retrieval_only"
            verified_sources = all_sources
        else:
            try:
                llm_res = self.llm_provider.generate(
                    system_prompt=AGRICULTURAL_RAG_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    max_tokens=850
                )

                if isinstance(llm_res, dict):
                    answer_text = llm_res.get("answer", "")
                    suggested_follow_ups = llm_res.get("follow_up_questions", [])
                    raw_cits = llm_res.get("citation_ids", [])
                else:
                    answer_text = str(llm_res).strip()
                    raw_cits = []

                # Extract inline citation tags e.g. [S1], [S2]
                inline_tags = re.findall(r'\[S(\d+)\]', answer_text)
                combined_cits = set(raw_cits) | {f"S{t}" for t in inline_tags}

                # Verify each citation against actual source map (rejecting hallucinated references)
                for s_id in sorted(combined_cits):
                    if s_id in source_map:
                        verified_sources.append(source_map[s_id])

                # If model failed to tag citations explicitly, attach verified retrieved sources
                if not verified_sources:
                    verified_sources = all_sources

            except (GeminiAuthError, GeminiQuotaError, GeminiTransientError, GeminiProviderError, Exception) as e:
                sanitized_err = str(e)
                print(f"[AgriculturalAnswerGenerator] Gemini generation unavailable: {sanitized_err[:150]}. Falling back to verified retrieval-only mode.")
                answer_text = self._format_retrieval_only_answer(q_clean, chunks, has_historical)
                answer_mode = "retrieval_only"
                generation_status = "provider_error_fallback"
                verified_sources = all_sources

        return {
            "answer": answer_text,
            "answer_mode": answer_mode,
            "retrieval_status": "success",
            "generation_status": generation_status,
            "sources": verified_sources,
            "has_historical_warning": has_historical,
            "provider_name": self.llm_provider.provider_name,
            "follow_up_questions": suggested_follow_ups
        }

    def _format_retrieval_only_answer(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        has_historical: bool
    ) -> str:
        """
        Formats an evidence-grounded synthesized answer directly from verified retrieved passages.
        Clearly labels retrieval-only mode and cites exact documents and pages.
        """
        top_chunk = chunks[0]
        cit = top_chunk["citation"]
        
        hist_disclaimer = ""
        if has_historical:
            hist_disclaimer = (
                "\n\n*(Note: Sourced from Uttarakhand Kharif Season Advisory (02.05.2020) by GBPUAT Pantnagar. "
                "This serves as verified baseline research; please confirm current seasonal input distribution with your local Block ADO or KVK.)*"
            )

        bullet_points = []
        for idx, c in enumerate(chunks[:3]):
            s_id = f"S{idx + 1}"
            c_cit = c["citation"]
            c_page = f"p. {c_cit['page_start']}"
            snippet = c["text"].strip().replace("\n", " ")
            if len(snippet) > 350:
                snippet = snippet[:350] + "..."
            bullet_points.append(f"• **[{s_id}] {c_cit['document_title']}, {c_page}**: {snippet}")

        joined_bullets = "\n\n".join(bullet_points)

        return (
            f"**Verified Evidence from GBPUAT Agricultural Bulletins:**\n\n"
            f"Based on retrieved agronomic guidance from **{cit['document_title']}** ({cit['publisher']}, {cit['publication_date']}) "
            f"for your question *'{query}'*:\n\n"
            f"{joined_bullets}"
            f"{hist_disclaimer}"
        )
