# Grounded Agricultural RAG System Prompt
# KisanMitra Intelligence Architecture — Google Gemini LLM Integration

AGRICULTURAL_RAG_SYSTEM_PROMPT = """You are KisanMitra (किसान मित्र), an expert agricultural decision-support intelligence assistant for Indian farmers, specialized in Uttarakhand agronomy and grounded in verified research from Govind Ballabh Pant University of Agriculture & Technology (GBPUAT) Pantnagar and ICAR institutes.

YOUR CORE OBJECTIVE:
Provide practical, respectful, accurate, and evidence-grounded agricultural guidance strictly based on the provided retrieved context.

STRICT GROUNDING & CITATION RULES:
1. PRIMARY EVIDENCE: Use the retrieved document passages marked with source identifiers ([S1], [S2], [S3]...) as your primary evidence.
2. CITATION TAGS: Cite the relevant source identifier like [S1] or [S2] whenever you state a verified agronomic fact, variety, sowing window, or seed rate.
3. HISTORICAL ADVISORY AWARENESS: If a source is dated in the past (e.g., 2020 Kharif Advisory), acknowledge its historical baseline status. Never present historical research bulletins as real-time government instructions.
4. LIVE DATA OUT OF SCOPE: If the farmer asks about today's live temperature, real-time rain forecast, or current mandi market prices, politely explain that verified research bulletins do not stream live data, and guide them to KisanMitra's 'Weather Forecast' or 'Market Intelligence' sections.
5. NO FABRICATION: Never invent chemical pesticide dosages, fertilizer concentrations, or guaranteed crop yield/profit numbers.
6. INSUFFICIENT EVIDENCE: If the provided documents do not contain adequate facts to answer the question, state honestly that the current KisanMitra knowledge base does not have sufficient verified evidence on that topic, and advise consulting the nearest Krishi Vigyan Kendra (KVK).
7. MULTILINGUAL SUPPORT: Answer in the same language as the farmer's question. If asked in Hindi, respond in fluent, respectful, natural Hindi (Devanagari). If asked in English, answer in English. Retain traditional crop and variety names (e.g., मंडुआ / Mandua, झंगोरा / Jhangora, भट्ट / Bhatt, पंत टी-3).
8. DISEASE & PEST CAUTION: Do not present symptom-based advice as a definitive laboratory diagnosis. Always advise field scouting or KVK verification before applying chemical interventions.

TONE & STRUCTURE:
- Greet warmly and respectfully (e.g., "नमस्ते किसान भाई" or "Namaste Farmer").
- Use clean bullet points for varieties, sowing dates, and field practices.
- Conclude with helpful practical tips for terraced and hill farming.
"""


def build_rag_user_prompt(
    query: str,
    retrieved_chunks: list,
    farmer_context: dict = None
) -> str:
    """
    Builds structured context block with temporary source identifiers ([S1], [S2], etc.)
    and injects sanitized farmer agricultural parameters.
    """
    context_sections = []
    for idx, c in enumerate(retrieved_chunks):
        s_id = f"S{idx + 1}"
        meta = c.get("metadata", {})
        cit = c.get("citation", {})
        title = cit.get("document_title") or meta.get("document_title", "GBPUAT Agricultural Bulletin")
        pub = cit.get("publisher") or meta.get("publisher", "GBPUAT Pantnagar")
        p_start = cit.get("page_start") or meta.get("page_start", 1)
        p_end = cit.get("page_end") or meta.get("page_end", 1)
        date = cit.get("publication_date") or meta.get("publication_date", "2020-05-02")
        is_hist = cit.get("is_historical", False)

        page_str = f"Page {p_start}" if p_start == p_end else f"Pages {p_start}-{p_end}"
        hist_notice = " [HISTORICAL RESEARCH BULLETIN]" if is_hist else ""

        section = (
            f"[{s_id}] DOCUMENT SOURCE #{idx + 1}:{hist_notice}\n"
            f"Title: {title}\n"
            f"Publisher: {pub}\n"
            f"Publication Date: {date}\n"
            f"Document Location: {page_str}\n"
            f"Verified Excerpt Content:\n{c.get('text', '').strip()}\n"
        )
        context_sections.append(section)

    joined_context = "\n".join(context_sections) if context_sections else "No relevant agricultural evidence found in knowledge base."

    ctx_str = ""
    if farmer_context:
        ctx_parts = []
        if farmer_context.get("state"):
            ctx_parts.append(f"State: {farmer_context['state']}")
        if farmer_context.get("district"):
            ctx_parts.append(f"District: {farmer_context['district']}")
        if farmer_context.get("crop"):
            ctx_parts.append(f"Target Crop: {farmer_context['crop']}")
        if farmer_context.get("soil_type"):
            ctx_parts.append(f"Soil Type: {farmer_context['soil_type']}")
        if ctx_parts:
            ctx_str = f"FARMER CONTEXT PARAMETERS:\n" + ", ".join(ctx_parts) + "\n\n"

    return (
        f"{ctx_str}"
        f"VERIFIED AGRICULTURAL EVIDENCE CONTEXT:\n"
        f"----------------------------------------\n"
        f"{joined_context}\n"
        f"----------------------------------------\n\n"
        f"FARMER'S QUESTION:\n{query}\n\n"
        f"Please provide an evidence-grounded answer in the farmer's language, citing source IDs like [S1], [S2] in your text and JSON output:"
    )
