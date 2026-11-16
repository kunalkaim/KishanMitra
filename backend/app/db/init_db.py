from sqlalchemy.orm import Session
from app.db.session import engine, Base
from app.models import (
    User, FarmerProfile, State, District, Block, Farm, SoilTest, Crop, CropSeason,
    Mandi, MarketPrice, KnowledgeDocument, KnowledgeChunk, Notification
)
from app.core.security import hash_password
from datetime import date, datetime, timezone
import uuid


def init_db(db: Session) -> None:
    """Creates database tables and seeds base records if empty."""
    Base.metadata.create_all(bind=engine)

    # Check if default demo farmer exists
    demo_farmer = db.query(User).filter(User.phone_number == "9876543210").first()
    if not demo_farmer:
        demo_farmer = User(
            id=str(uuid.uuid4()),
            phone_number="9876543210",
            email="farmer@kisanmitra.in",
            hashed_password=hash_password("FarmerPassword123!"),
            full_name="Surendra Singh Negi",
            preferred_language="hi",
            role="farmer",
            is_active=True,
            is_verified=True
        )
        db.add(demo_farmer)
        db.flush()

        profile = FarmerProfile(
            user_id=demo_farmer.id,
            experience_years=14,
            primary_irrigation_source="Canal / Gravity Watercourse (Gul)",
            has_kisan_credit_card=True,
            kcc_limit=150000.0,
            soil_health_card_number="UK-ALM-2025-08942",
            annual_income_bracket="₹2,50,000 - ₹4,00,000"
        )
        db.add(profile)

        # Seed sample farm
        sample_farm = Farm(
            id="farm-demo-01",
            farmer_id=demo_farmer.id,
            farm_name="Nanda Devi Valley Terrace Orchard",
            state="Uttarakhand",
            district="Almora",
            block="Hawalbagh",
            village="Dhaula Devi",
            pincode="263601",
            total_area_acres=3.5,
            cultivated_area_acres=3.0,
            irrigation_type="Canal / Gravity Channel",
            soil_type="Brown Forest Soil",
            ownership_type="Owned",
            latitude=29.5992,
            longitude=79.6586,
            elevation_meters=1650.0,
            is_active=True
        )
        db.add(sample_farm)
        db.flush()

        # Seed sample soil test
        sample_soil = SoilTest(
            farm_id=sample_farm.id,
            test_date=date(2025, 10, 15),
            soil_ph=6.4,
            organic_carbon_percent=0.82,
            nitrogen_kg_ha=295.0,
            phosphorus_kg_ha=22.4,
            potassium_kg_ha=240.0,
            sulphur_ppm=12.5,
            zinc_ppm=0.9,
            iron_ppm=6.2,
            electrical_conductivity=0.42,
            testing_lab_name="ICAR-VPKAS Almora Soil Testing Lab"
        )
        db.add(sample_soil)

        # Seed sample notifications
        n1 = Notification(
            farmer_id=demo_farmer.id,
            notification_type="weather_alert",
            title="IMD Yellow Alert: Rain in Higher Valleys",
            message="Light to moderate orographic rain predicted for Almora ridge areas over 48 hours. Secure harvested millet stocks.",
            severity="warning"
        )
        n2 = Notification(
            farmer_id=demo_farmer.id,
            notification_type="price_alert",
            title="Mandi Price Spike: Finger Millet (Mandua)",
            message="Modal price for certified Organic Mandua at Haldwani Mandi touched ₹3,600/quintal today (+8.2%).",
            severity="info"
        )
        db.add_all([n1, n2])
        db.commit()
