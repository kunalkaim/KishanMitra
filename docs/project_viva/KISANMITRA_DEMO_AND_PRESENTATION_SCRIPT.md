# KISANMITRA (किसानमित्र) — LIVE DEMO & PRESENTATION SCRIPT
**Step-by-Step Viva Demonstration Walkthrough: Actions, Verbal Cues, Expected Outputs & Technical Highlights**

---

## DEMONSTRATION SETUP CHECKLIST (5 MINUTES BEFORE VIVA)

Before inviting the evaluation panel to observe the screen, ensure:
1. **Backend Server Running:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   *Verify:* Open `http://localhost:8000/docs` in a browser tab to ensure Swagger UI is live and responsive.
2. **Frontend Development Server Running:**
   ```bash
   npm run dev
   ```
   *Verify:* Open `http://localhost:5173` in a full-screen browser window.
3. **Database & Knowledge Base Verified:**
   - SQLite `kisanmitra.db` present in root.
   - ChromaDB `backend/app/storage/vector_index/chroma.sqlite3` contains 31 active vectors.
4. **Browser Zoom:** Set browser zoom to 100% or 110% for projector/large screen clarity.

---

## STEP-BY-STEP 7-STAGE PRESENTATION SCRIPT

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          DEMO WALKTHROUGH FLOW                                  │
│                                                                                 │
│   STAGE 1: Dashboard Overview                                                   │
│      │                                                                          │
│      ▼                                                                          │
│   STAGE 2: Farm & Soil Profile Inspection                                       │
│      │                                                                          │
│      ▼                                                                          │
│   STAGE 3: Crop Recommendation Wizard Execution                                 │
│      │                                                                          │
│      ▼                                                                          │
│   STAGE 4: Interactive What-If Simulation & Nutrient Sliders                     │
│      │                                                                          │
│      ▼                                                                          │
│   STAGE 5: Multilingual RAG Assistant (Hindi/English Chat)                      │
│      │                                                                          │
│      ▼                                                                          │
│   STAGE 6: APMC Mandi Economics & Break-Even Analysis                           │
│      │                                                                          │
│      ▼                                                                          │
│   STAGE 7: Text IPM Advisory & Project Conclusion                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### STAGE 1: EXECUTIVE DASHBOARD & WEATHER TICKER
- **Screen to Open:** `http://localhost:5173` (Home Dashboard).
- **Action:** Point the mouse to the top weather banner, the active farmer card (Ramesh Chandra Joshi), and the quick-action cards.
- **Verbal Script for Presenter:**
  > *"Respected evaluators, this is the main KisanMitra dashboard. It acts as an executive cockpit for the farmer. At the top, you can see live microclimate weather for our pilot location in Almora, Uttarakhand. Notice that the temperature shows 18.6°C despite the regional base station reporting 29°C. This is because our 3-tier weather engine automatically applies an environmental lapse rate adjustment of 6.5°C per 1,000 meters based on the farm's 1,600m elevation. The dashboard also aggregates recent crop recommendations, pending soil test updates, and real-time APMC mandi market alerts."*
- **Technical Highlight to Mention:**
  - 3-tier weather architecture (Open-Meteo $\to$ SQLite cache $\to$ Lapse rate calculation).
  - React 19 concurrent UI rendering with Framer Motion transitions.

---

### STAGE 2: FARM & SOIL PROFILE INSPECTION
- **Screen to Open:** Navigate to **"Farm Management"** via the sidebar.
- **Action:** Click on **"Terrace Field #2 (Almora)"** to display its soil chemistry and geospatial characteristics.
- **Values to Highlight on Screen:**
  - Elevation: **1,600 meters**
  - Soil Type: **Mountain Terrace / Loamy**
  - Nitrogen ($N$): **35 kg/ha** *(Low)*
  - Phosphorus ($P$): **25 kg/ha** *(Medium)*
  - Potassium ($K$): **30 kg/ha** *(Medium)*
  - Soil pH: **6.2** *(Slightly Acidic)*
- **Verbal Script for Presenter:**
  > *"Here we see the registered farm parcel. Rather than using generic village averages, KisanMitra ties recommendations to specific soil chemistry test values and topographic elevation. A farmer can manage multiple distinct parcels—such as valley bottom land versus steep terrace slopes. Notice that Nitrogen is low at 35 kg/ha and pH is 6.2, which is typical for Himalayan rainfed soils."*
- **Technical Highlight to Mention:**
  - One-to-many SQLAlchemy relational model linking `Farmer` to multiple `Farm` profiles.
  - Strict Pydantic boundary validation preventing invalid physiological entries.

---

### STAGE 3: CROP RECOMMENDATION WIZARD EXECUTION
- **Screen to Open:** Navigate to **"Crop Recommendation"** $\to$ Click **"New Recommendation"**.
- **Action:**
  1. Select **"Terrace Field #2"** from the farm dropdown.
  2. Confirm the auto-populated soil values ($N=35, P=25, K=30, \text{pH}=6.2$).
  3. Select Target Season: **Kharif (Monsoon)**.
  4. Click the primary button: **"Run Recommendation Engine"**.
- **Expected Output to Show the Evaluators:**
  - **Rank 1:** **Finger Millet (Mandua)** — Suitability: **94.4%**
  - **Rank 2:** **Maize** — Suitability: **61.2%**
  - **Rank 3:** **Lentil / Pulses** — Suitability: **58.6%**
  - **Crucial Negative Proof:** Point out that **Rice is ranked at the very bottom (~0.006%)**.
- **Verbal Script for Presenter:**
  > *"When I click 'Run Recommendation Engine', the frontend dispatches a request to our FastAPI backend. In under 15 milliseconds, our 3-model hybrid ensemble executes. The top recommended crop is Finger Millet (Mandua) at 94.4% suitability, followed by Maize.
  >
  > Crucially, notice that Rice is NOT recommended—it ranks near zero. Previously, our system suffered from a 'Rice Bias' where Rice appeared first under all conditions. As you can see, our root-cause fix normalized seasonal rainfall inputs and eliminated static mocks, ensuring the model is genuinely sensitive to low rainfall (145mm) and high altitude."*
- **Technical Highlight to Mention:**
  - Hybrid ensemble combining GaussianNB ($w=0.62$) and Decision Tree ($w=0.38$).
  - Macro F1-score: 99.70%, Log Loss: 0.0178.

---

### STAGE 4: INTERACTIVE WHAT-IF SIMULATION & NUTRIENT SLIDERS
- **Screen to Open:** Scroll to the **"Interactive What-If Simulator"** section below the recommendation results.
- **Action:**
  1. Locate the **Nitrogen ($N$)** slider (currently at 35 kg/ha).
  2. Drag the slider to the right to increase Nitrogen to **90 kg/ha**.
  3. Drag the **Rainfall / Irrigation** slider to **200 mm**.
  4. Observe the real-time probability shift on the screen.
- **Expected Output to Show the Evaluators:**
  - **Maize** suitability immediately surges from **61.2% to 91.5%**.
  - Finger Millet suitability adjusts as nitrogen-demanding cereals become viable.
  - The Explainable AI (XAI) text updates: *"Nitrogen augmentation eliminates previous nutrient deficiency for high-yield Maize."*
- **Verbal Script for Presenter:**
  > *"Farmers often ask: 'What happens if I apply more fertilizer?' KisanMitra includes an interactive Explainable AI What-If Simulator. Watch as I increase Nitrogen from 35 to 90 kg/ha. In real time, Maize jumps to 91.5% suitability. The XAI engine contrasts the farmer's soil values against the biological centroid of the crop and highlights exactly how nutrient management changes agricultural viability."*
- **Technical Highlight to Mention:**
  - Real-time client-side debouncing and asynchronous endpoint execution.
  - Active role of Fuzzy Logic membership functions in generating qualitative XAI explanations.

---

### STAGE 5: MULTILINGUAL AI ASSISTANT (RAG IN HINDI & ENGLISH)
- **Screen to Open:** Navigate to **"AI Assistant"** via the sidebar.
- **Action 1 (Hindi Query):**
  - Type or click the quick prompt:
    ```text
    मंडुवा (फिंगर मिलेट) की बुवाई का सही समय और खाद की मात्रा क्या है?
    ```
  - Click **Send**.
- **Expected Output:**
  - Assistant responds in fluent, grammatically correct Devanagari Hindi.
  - Contains exact sowing dates (May–June) and fertilizer dosages (40 kg N, 20 kg P2O5 per ha).
  - Explicitly displays citation pills: `[S1] ICAR-VPKAS Package of Practices for Hill Millets`.
- **Action 2 (Click Citation):**
  - Click on the `[S1]` citation pill to expand the verified university source chunk.
- **Verbal Script for Presenter:**
  > *"Now we move to our Multilingual AI Assistant. I have typed an agronomic question in Hindi regarding Finger Millet fertilization. Unlike standard ChatGPT or generic chatbots that might invent chemical dosages, KisanMitra uses Retrieval-Augmented Generation (RAG).
  >
  > The system vectorized the Hindi query using our 384-dimensional multilingual sentence-transformer, retrieved the top matching chunks from our 31 ChromaDB vectors, and instructed Google Gemini Flash Lite to generate an answer grounded strictly in ICAR-VPKAS research bulletins. Notice the [S1] citation. When I click it, the farmer can inspect the exact university bulletin source."*
- **Technical Highlight to Mention:**
  - `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` cross-lingual semantic alignment.
  - Persistent ChromaDB collection `kisanmitra_kb`.
  - Hallucination prevention via temperature=0.2 and extractive fallback mode.

---

### STAGE 6: MANDI PRICE INTELLIGENCE & PROFITABILITY ECONOMICS
- **Screen to Open:** Navigate to **"Mandi Prices & Economics"** via the sidebar.
- **Action:** Select **Almora Mandi** and choose **Finger Millet (Mandua)**.
- **Values to Highlight on Screen:**
  - Modal Mandi Price: **₹3,500 / Quintal**
  - Expected Yield: **8 Quintals / Acre**
  - Gross Revenue: **₹28,000 / Acre**
  - Cost of Cultivation: **₹11,200 / Acre**
  - Net Profit: **₹16,800 / Acre**
  - **Benefit-Cost Ratio (BCR):** **2.50** *(High Viability Badge)*
  - **Break-Even Yield:** **3.20 Quintals / Acre**
- **Verbal Script for Presenter:**
  > *"Agronomic suitability is only half the battle—a crop must also be economically viable. Here, KisanMitra connects production to market reality. For Almora Mandi, the modal price for Finger Millet is ₹3,500 per quintal.
  >
  > Our economic calculator evaluates the Benefit-Cost Ratio (BCR). At 2.50, the crop is highly profitable. Furthermore, we compute the Break-Even Yield: the farmer only needs to harvest 3.2 quintals per acre to recover all production costs. Any yield above 3.2 quintals is pure profit."*
- **Technical Highlight to Mention:**
  - APMC 5-hub regional tracking.
  - Mathematical formulation of BCR, Break-Even Yield, and Break-Even Price.

---

### STAGE 7: TEXT IPM ADVISORY & CONCLUSION
- **Screen to Open:** Navigate to **"Pest & Disease Advisory"**.
- **Action:** Type in the symptom box: *"Paddy leaf yellowing and stem borer attack"*.
- **Expected Output:**
  - University-verified Integrated Pest Management (IPM) recommendations appear with biological controls (Trichogramma egg parasitoids) and safe chemical options with withholding periods.
- **Verbal Script for Presenter:**
  > *"Finally, we demonstrate our Text-Based Pest and Disease Advisory. Note that KisanMitra intentionally avoids leaf photo uploads because low smartphone camera resolution and lighting variations cause severe misclassification in real fields. Instead, our text-based IPM system retrieves certified agronomic protocols from GBPUAT bulletins.
  >
  > In conclusion, KisanMitra successfully bridges the gap between scientific agricultural research, microclimate meteorology, predictive machine learning, and market economics. Thank you, respected professors. We are now open for your questions."*

---

## PRESENTATION TROUBLESHOOTING & EMERGENCY CHEATS

| Problem During Demo | Instant Fix / Defense |
| :--- | :--- |
| **Internet Fails Suddenly** | Frontend will seamlessly activate cached state; explain: *"As you can see, our offline caching architecture instantly kicked in to preserve usability without internet."* |
| **Gemini API Key Rate Limit** | RAG assistant automatically switches to **Extractive Fallback Mode**; point out: *"Notice that when external LLM APIs fail, KisanMitra safely falls back to displaying the raw extracted university chunks directly, completely preventing downtime."* |
| **UI Stalls on First Query** | Explain calmly: *"The backend is loading the PyTorch multilingual sentence-transformer into RAM during the initial turn; subsequent queries respond in under 1.5 seconds."* |
