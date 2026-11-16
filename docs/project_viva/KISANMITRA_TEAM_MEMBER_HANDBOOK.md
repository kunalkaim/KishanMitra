# KISANMITRA (किसानमित्र) — TEAM MEMBER VIVA HANDBOOK
**Universal Knowledge Base, Module Specialization Tracks, Code File Mapping & Viva Coordination Strategy**

---

## 1. UNIVERSAL COMMON KNOWLEDGE (MANDATORY FOR ALL TEAM MEMBERS)

Regardless of which module you personally contributed to, **every single team member must know the following baseline facts**:

1. **Project Definition:** KisanMitra is a unified, multi-modal agricultural decision-support system integrating Predictive ML, Multilingual Generative RAG, Microclimate Weather, and Mandi Economics.
2. **The Two AI Engines:**
   - *Predictive ML:* 3-model hybrid ensemble (Fuzzy Logic, Gaussian Naive Bayes, Decision Tree) achieving **99.70% accuracy** on 22 crops with weights $w = [0.00, 0.62, 0.38]$.
   - *Generative RAG:* Bilingual (Hindi/English) assistant using PyTesseract OCR, `paraphrase-multilingual-MiniLM-L12-v2` embeddings (384-dim), ChromaDB vector store (**31 vectors**), and Google Gemini Flash Lite with strict source citations (`[S1]`, `[S2]`).
3. **The Core Tech Stack:** React 19 + TypeScript + Vite + Tailwind CSS on the frontend; FastAPI + Pydantic + SQLAlchemy + Scikit-Learn + ChromaDB on the backend; SQLite for local development (`kisanmitra.db`).
4. **The Rice Bias Elimination:** A major defect where Rice always ranked #1 was diagnosed and resolved across 5 root causes (rainfall unit mismatch, static demo state, fallback heuristics, missing demo farm, and cold-start PyTorch timeouts).
5. **No Computer Vision:** KisanMitra does **not** do leaf image disease classification. We deliberately chose text-based IPM agronomic advisory grounded in university packages to avoid poor camera resolution misdiagnoses.
6. **Key Endpoint:** `POST /api/v1/recommendations/unified` combines soil, weather, ML predictions, and market economics into a single response.

---

## 2. SUGGESTED 6-MEMBER SPECIALIZATION TRACKS

To ensure comprehensive coverage during an examination where evaluators ask deep technical questions, assign each team member to lead one specialization track:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              6 SPECIALIZATION TRACKS                                   │
├──────────────────────────┬─────────────────────────────────────────────────────────────┤
│ Track                    │ Primary Focus & Responsibilities                            │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ Track 1: Frontend Lead   │ React 19, TypeScript, Tailwind, AppContext, Recharts, UI/UX │
│ Track 2: Backend Lead    │ FastAPI, Async endpoints, Pydantic schemas, Unified API     │
│ Track 3: ML Lead         │ Ensemble math, GNB, Decision Tree, Fuzzy XAI, Rice Bias fix │
│ Track 4: RAG & GenAI Lead│ OCR, MiniLM-L12 embeddings, ChromaDB, Gemini, Hallucination│
│ Track 5: Agro-Economics  │ Weather lapse rates, Open-Meteo, APMC mandis, BCR formulas  │
│ Track 6: DB & QA Lead    │ SQLite, SQLAlchemy models, Alembic, 18/18 pytest suite      │
└──────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

### TRACK 1: FRONTEND & UI/UX SPECIALIST

- **Primary Ownership:**
  - Component hierarchy in `src/pages/` and `src/components/`.
  - State management in `src/context/AppContext.tsx`.
  - Responsive design, accessibility, and chart renderings.
- **Key Files to Study:**
  - [App.tsx](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/src/App.tsx) — Main layout, routing, and navigation.
  - [AppContext.tsx](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/src/context/AppContext.tsx) — Centralized state, active farm selection, fallback handling.
  - [Dashboard.tsx](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/src/pages/Dashboard.tsx) — Executive farmer dashboard.
  - [CropRecommendationWizard.tsx](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/src/components/CropRecommendationWizard.tsx) — Multi-step recommendation flow.
  - [AIAssistant.tsx](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/src/pages/AIAssistant.tsx) — Bilingual RAG chat interface.
- **Top Viva Questions You Will Face:**
  - *How does the frontend handle backend disconnection?* $\to$ AppContext catches errors and activates localStorage cached state.
  - *Why React 19 and Vite over CRA?* $\to$ Vite uses native ES modules; React 19 provides enhanced concurrent rendering.
  - *How do the What-If sliders work without lag?* $\to$ Client-side debounced state updates trigger async API calls to `/predict`.

---

### TRACK 2: BACKEND & REST API SPECIALIST

- **Primary Ownership:**
  - FastAPI application structure, routing, and lifespan management.
  - Pydantic validation schemas and HTTP error handling.
  - The unified orchestrator endpoint.
- **Key Files to Study:**
  - [main.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/main.py) — Lifespan startup, CORS middleware, router registration.
  - [unified_recommendations.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/api/v1/endpoints/unified_recommendations.py) — The `/recommendations/unified` pipeline.
  - [recommendation.py (schemas)](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/schemas/recommendation.py) — Pydantic models and field validators.
  - [config.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/core/config.py) — Environment variables and dynamic SQLite path resolution.
- **Top Viva Questions You Will Face:**
  - *How does `/recommendations/unified` coordinate services?* $\to$ Fetches farm soil $\to$ calls weather with elevation $\to$ runs ML ensemble $\to$ joins APMC prices $\to$ returns combined JSON.
  - *How do you validate incoming requests?* $\to$ Pydantic schemas enforce ranges ($N \in [0, 250]$, $\text{pH} \in [3, 10]$).
  - *What is FastAPI's lifespan manager?* $\to$ Pre-loads ML model artifacts and warming up embedding models into RAM during startup to prevent cold-start delays.

---

### TRACK 3: MACHINE LEARNING & ENSEMBLE SPECIALIST

- **Primary Ownership:**
  - The 3-model hybrid ensemble (Fuzzy Logic, GaussianNB, Decision Tree).
  - Probability calibration, SLSQP simplex optimization, and performance metrics.
  - Forensic investigation and resolution of the Phase 5 Rice Bias defect.
  - Explainable AI (XAI) nutrient gap formulations.
- **Key Files to Study:**
  - [hybrid_crop_recommender.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/ml/hybrid_crop_recommender.py) — Core ensemble implementation.
  - [fuzzy_classifier.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/ml/fuzzy_classifier.py) — Membership functions and rule evaluation.
  - [active_model_metadata.json](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/model_artifacts/crop_recommendation/active_model_metadata.json) — Verified weights, metrics, and class schemas.
- **Top Viva Questions You Will Face:**
  - *Why is Fuzzy Logic weight 0.00?* $\to$ Redundant for prediction accuracy ($99.7\%$), but essential for the XAI rule base.
  - *Why GaussianNB over complex Neural Networks?* $\to$ Continuous Gaussian bells match biological crop response curves, training requires only 2,200 rows, and inference runs in <15ms on CPU.
  - *How did you prove the Rice Bias was eliminated?* $\to$ Demonstrated low-water tests (Rain=100mm) where Mandua scores 94% and Rice drops to 0.0001%.

---

### TRACK 4: GENERATIVE AI & RAG SPECIALIST

- **Primary Ownership:**
  - Document OCR, semantic chunking, and embedding generation.
  - ChromaDB vector store indexing and cosine similarity.
  - Hybrid retrieval (Dense + BM25) and Google Gemini prompt grounding.
  - Extractive fallback mechanisms and hallucination suppression.
- **Key Files to Study:**
  - [hybrid_retriever.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/rag/hybrid_retriever.py) — Dense vector + sparse lexical retrieval.
  - [embedding_service.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/rag/embedding_service.py) — Sentence-Transformers integration.
  - [rag_assistant.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/rag/rag_assistant.py) — Gemini prompt augmentation and extractive fallback.
  - [document_manifest.json](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/storage/document_manifest.json) — Catalogued university packages.
- **Top Viva Questions You Will Face:**
  - *What embedding model is used and why?* $\to$ `paraphrase-multilingual-MiniLM-L12-v2` (384 dims); aligns Hindi and English into the same semantic space.
  - *How many vectors are in ChromaDB?* $\to$ 31 verified vectors from 6 official packages.
  - *How do you guarantee the LLM does not invent dosages?* $\to$ Strict context injection, temp=0.2, mandatory `[S1]` citations, and fallback to raw extracted text.

---

### TRACK 5: AGRO-METEOROLOGY & ECONOMICS SPECIALIST

- **Primary Ownership:**
  - 3-tier weather architecture (Open-Meteo, SQLite cache, lapse rate adjustments).
  - APMC mandi tracking across 5 Uttarakhand hubs.
  - Financial modeling: Gross Revenue, Net Margin, BCR, Break-Even Yield & Price.
- **Key Files to Study:**
  - [weather_service.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/services/weather_service.py) — Open-Meteo client and lapse rate math.
  - [mandi_service.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/services/mandi_service.py) — APMC market prices and modal calculations.
  - [economic_calculator.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/services/economic_calculator.py) — Cultivation cost, BCR, and break-even logic.
- **Top Viva Questions You Will Face:**
  - *Why apply an elevation lapse rate?* $\to$ Hill farms at 1,600m are $10.4^\circ\text{C}$ colder than valley weather stations; without lapse rates, frost alerts fail.
  - *What is the Benefit-Cost Ratio (BCR) formula?* $\to$ $\text{BCR} = \text{Gross Revenue} / \text{Cost of Cultivation}$. Values $\ge 1.5$ indicate high profitability.
  - *What is Modal Price?* $\to$ The most frequent daily wholesale transaction price, far more representative than an arithmetic average.

---

### TRACK 6: DATABASE, TESTING & QA SPECIALIST

- **Primary Ownership:**
  - Relational schema modeling and SQLAlchemy ORM relationships.
  - SQLite local dev vs PostgreSQL/PostGIS Docker deployment.
  - Automated regression testing (18/18 test suite) and environment reproducibility.
- **Key Files to Study:**
  - [database.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/db/database.py) — Engine creation and session factories.
  - [farmer.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/models/farmer.py) & [farm.py](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/backend/app/models/farm.py) — Core relational ORM models.
  - [docker-compose.yml](file:///c:/Users/AAKASH/OneDrive/Desktop/farmer/docker-compose.yml) — Production multi-container PostGIS configuration.
  - `backend/tests/` — Automated test suites.
- **Top Viva Questions You Will Face:**
  - *Why use SQLite for local dev and PostgreSQL for Docker?* $\to$ SQLite is zero-setup for evaluation; PostgreSQL/PostGIS provides concurrent production geospatial indexing.
  - *How do you verify backend stability?* $\to$ Running `pytest backend/tests` passes all 18 regression tests covering models, endpoints, and RAG.
  - *How is database portability achieved?* $\to$ `resolve_sqlite_url()` derives paths dynamically from the project root rather than hardcoding Windows usernames.

---

## 3. VIVA EXAMINATION COORDINATION STRATEGY

### How to Present as a Unified Team
1. **Never Contradict a Teammate:** If a teammate makes a slight verbal slip (e.g., says "384-bit embeddings" instead of "384-dimensional floating point"), do not immediately say *"No, they are wrong."* Instead, smoothly add: *"To add to what my teammate mentioned, the MiniLM model generates 384 continuous floating-point dimensions..."*
2. **Smoothly Hand Over Domain Questions:** When the professor asks a deep question outside your primary track, provide a high-level summary and hand over to the specialist:
   > *"At a high level, our weather engine adjusts temperatures for elevation. I'll let [Teammate Name], who led the agro-meteorology module, explain the exact lapse rate calculations."*
3. **Be Completely Honest About Scope:**
   - If asked: *"Can a farmer upload a photo of a diseased leaf?"*
   - Say: *"No, professor. We made a deliberate engineering decision not to implement leaf image uploads. In Indian fields, low camera resolution and sunlight variations cause high misclassification. Instead, we use a text-based RAG assistant grounded in official university IPM packages."* Evaluators respect this scientific honesty far more than fabricated claims.
4. **Anchor Answers in Real Evidence:** Reference real file names, exact metrics (99.70% F1, 31 ChromaDB vectors, 0.0178 log loss), and real institutions (ICAR-VPKAS Almora, GBPUAT Pantnagar).
