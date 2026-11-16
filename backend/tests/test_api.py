import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "kisanmitra-backend"


def test_login_and_me():
    # Login with seeded demo farmer
    login_resp = client.post("/api/v1/auth/login", json={
        "phone_number": "9876543210",
        "password": "FarmerPassword123!"
    })
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # Call /me with bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["phone_number"] == "9876543210"
    assert me_data["full_name"] == "Surendra Singh Negi"


def test_districts_list():
    resp = client.get("/api/v1/regions/districts?state_name=Uttarakhand")
    assert resp.status_code == 200
    districts = resp.json()
    assert len(districts) == 13
    district_names = [d["district_name"] for d in districts]
    assert "Almora" in district_names
    assert "Dehradun" in district_names
    assert "Haridwar" in district_names


def test_crops_catalog():
    resp = client.get("/api/v1/crops/")
    assert resp.status_code == 200
    crops = resp.json()
    assert len(crops) >= 8
    crop_names = [c["crop_name"] for c in crops]
    assert any("Finger Millet" in name for name in crop_names)


def test_text_based_advisory():
    # Login first
    login_resp = client.post("/api/v1/auth/login", json={
        "phone_number": "9876543210",
        "password": "FarmerPassword123!"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Submit text-based pest & disease inquiry
    advisory_payload = {
        "crop_name": "Finger Millet (Mandua / Ragi)",
        "crop_growth_stage": "Tillering",
        "observed_symptoms": "Spindle-shaped brown lesions with greyish centres on leaf blades and neck.",
        "farming_conditions": "Heavy intermittent monsoon rains and damp morning terrace fog.",
        "affected_area_percentage": 12.0
    }
    resp = client.post("/api/v1/advisory/cases", json=advisory_payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "Blast" in data["suspected_pest_or_pathogen"]
    assert data["diagnostic_category"] == "Fungal Disease"
    assert len(data["recommended_interventions"]) > 0
    assert data["is_demo"] is True


def test_weather_endpoint():
    resp = client.get("/api/v1/weather/?district=Almora")
    assert resp.status_code == 200
    data = resp.json()
    assert data["district_name"] == "Almora"
    assert len(data["forecast"]) == 7
    assert "IMD" in data["agricultural_alert"]


def test_mandi_prices():
    resp = client.get("/api/v1/market/prices")
    assert resp.status_code == 200
    prices = resp.json()
    assert len(prices) > 0


def test_profitability_calculation():
    # Fetch a crop ID
    crops_resp = client.get("/api/v1/crops/")
    crop_id = crops_resp.json()[0]["id"]

    calc_payload = {
        "crop_id": crop_id,
        "area_acres": 2.0,
        "expected_yield_per_acre": 15.0,
        "expected_sale_price_per_quintal": 3500.0,
        "seed_cost": 2000.0,
        "fertilizer_cost": 3500.0,
        "pesticide_cost": 1500.0,
        "irrigation_cost": 1000.0,
        "labor_cost": 5000.0,
        "machinery_cost": 2500.0,
        "miscellaneous_cost": 800.0
    }
    resp = client.post("/api/v1/economics/calculate", json=calc_payload)
    assert resp.status_code == 200
    econ = resp.json()
    # 2 acres * 15 quintal/acre * 3500 ₹/quintal = 105,000
    assert econ["gross_income"] == 105000.0
    assert econ["total_expenses"] > 0
    assert econ["net_profit"] == round(105000.0 - econ["total_expenses"], 2)
    assert econ["benefit_cost_ratio"] > 1.0


def test_assistant_rag_chat():
    login_resp = client.post("/api/v1/auth/login", json={
        "phone_number": "9876543210",
        "password": "FarmerPassword123!"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    chat_payload = {
        "message": "What is the recommended sowing time and varieties for Mandua in Almora?",
        "district_context": "Almora"
    }
    resp = client.post("/api/v1/assistant/chat", json=chat_payload, headers=headers)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert chat_data["sender_role"] == "assistant"
    assert len(chat_data["content"]) > 20
    assert len(chat_data["retrieved_sources"]) > 0
