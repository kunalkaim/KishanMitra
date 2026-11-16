import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_token():
    login_resp = client.post("/api/v1/auth/login", json={
        "phone_number": "9876543210",
        "password": "FarmerPassword123!"
    })
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


def test_unified_recommendation_pipeline():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch farmer's farm
    farms_resp = client.get("/api/v1/farms/", headers=headers)
    assert farms_resp.status_code == 200
    farms = farms_resp.json()
    assert len(farms) > 0
    test_farm = farms[0]
    farm_id = test_farm["id"]

    # 2. Call Unified Recommendation endpoint
    payload = {
        "farm_id": farm_id,
        "season": "Kharif",
        "target_market": "Local Mandi",
        "budget_per_acre": 30000.0,
        "irrigation_available": True,
        # Feature overrides (optional)
        "N": 95.0,
        "P": 45.0,
        "K": 42.0,
        "temperature": 23.5,
        "humidity": 72.0,
        "ph": 6.4,
        "rainfall": 195.0
    }

    resp = client.post("/api/v1/recommendations/unified", json=payload, headers=headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()

    # 3. Verify Top-Level Structure
    assert "request_id" in data
    assert data["farm_id"] == farm_id
    assert data["district"] == test_farm["district"]
    assert data["season"] == "Kharif"
    assert "elevation_meters" in data
    assert "soil_source" in data
    assert "weather_source" in data
    assert "resolved_features" in data
    assert len(data["recommended_crops"]) == 3

    # 4. Verify Crop Item Layers
    assert data["recommended_crops"][0]["suitability_score"] > 0
    for rank_idx, crop in enumerate(data["recommended_crops"], 1):
        assert crop["rank"] == rank_idx
        assert "crop_name" in crop
        assert "hindi_name" in crop
        assert crop["suitability_score"] >= 0

        # Layer 1: ML Model Breakdown
        assert "model_scores" in crop
        assert "fuzzy_logic" in crop["model_scores"]
        assert "gaussian_nb" in crop["model_scores"]
        assert "decision_tree" in crop["model_scores"]
        assert crop["why_recommended"] != ""

        # Layer 2: RAG Knowledge Evidence
        assert isinstance(crop["verified_package_of_practices"], list)
        assert len(crop["verified_package_of_practices"]) > 0
        assert isinstance(crop["rag_citations"], list)
        for cit in crop["rag_citations"]:
            assert "document_title" in cit
            assert "publisher" in cit
            assert "page_start" in cit
            assert cit["retrieval_score"] > 0

        # Layer 3: APMC Market Economics
        assert "mandi_name" in crop
        assert crop["modal_price_per_quintal"] > 0
        assert crop["expected_yield_per_acre"] > 0
        assert crop["estimated_cost_per_acre"] > 0
        assert crop["estimated_gross_revenue"] > 0
        assert crop["benefit_cost_ratio"] > 0
        assert crop["breakeven_yield_per_acre"] > 0
        assert "non-guaranteed" in crop["economic_disclaimer"].lower()

        # Layer 4: Agro-Meteorological & Risks
        assert crop["weather_suitability_flag"] in ["Optimal", "Watch Alert", "Moisture Deficit"]
        assert len(crop["agronomic_risks"]) > 0
        assert len(crop["cultivation_steps"]) >= 4


def test_unified_recommendation_unauthorized():
    resp = client.post(
        "/api/v1/recommendations/unified",
        json={"farm_id": "dummy"},
        headers={"Authorization": "Bearer invalid-token-xyz"}
    )
    assert resp.status_code == 401



def test_unified_recommendation_farm_not_found():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/api/v1/recommendations/unified", json={"farm_id": "non-existent-farm-id"}, headers=headers)
    assert resp.status_code == 404


def test_unified_recommendation_invalid_nutrients_returns_422():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    farms_resp = client.get("/api/v1/farms/", headers=headers)
    assert farms_resp.status_code == 200
    farm_id = farms_resp.json()[0]["id"]

    # Scenario 11: Negative Nitrogen nutrient value must return HTTP 422, not HTTP 500
    payload = {
        "farm_id": farm_id,
        "N": -50.0,
        "P": 40.0,
        "K": 40.0
    }
    resp = client.post("/api/v1/recommendations/unified", json=payload, headers=headers)
    assert resp.status_code == 422
    err_data = resp.json()
    assert "detail" in err_data
    assert "Invalid feature inputs" in err_data["detail"] or "Soil nutrients" in err_data["detail"]

