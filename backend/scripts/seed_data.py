from sqlalchemy.orm import Session
from datetime import date, datetime, timezone
import uuid
from app.models.region import State, District, Block
from app.models.crop import Crop, CropSeason
from app.models.market import Mandi, MarketPrice
from app.models.document import KnowledgeDocument, KnowledgeChunk


def run_seed(db: Session) -> None:
    # 1. Seed State: Uttarakhand
    uk_state = db.query(State).filter(State.state_name == "Uttarakhand").first()
    if not uk_state:
        uk_state = State(
            id=str(uuid.uuid4()),
            state_name="Uttarakhand",
            state_code="UK"
        )
        db.add(uk_state)
        db.flush()

    # 2. Seed 13 Districts of Uttarakhand
    districts_data = [
        {
            "name": "Almora",
            "zone": "Sub-temperate Mid-hills",
            "elevation": "1200m - 2200m",
            "rainfall": 1050.0,
            "soils": ["Brown Forest Soil", "Sandy Loam", "Gravelly Loam"],
            "crops": ["Finger Millet (Mandua)", "Barnyard Millet (Jhangora)", "Bhatt (Black Soybean)", "Wheat", "Barley"],
            "blocks": ["Hawalbagh", "Dhaula Devi", "Bhikiyasain", "Chaukhutiya", "Dwarahat", "Sult", "Tarikhet", "Takula", "Lamuagara", "Syaldhey", "Bhaisiya Chhana"]
        },
        {
            "name": "Dehradun",
            "zone": "Sub-tropical Valley & Tarai",
            "elevation": "450m - 1200m",
            "rainfall": 1850.0,
            "soils": ["Alluvial Loam", "Clay Loam"],
            "crops": ["Basmati Rice", "Wheat", "Sugarcane", "Mustard", "Litchi", "Mango"],
            "blocks": ["Chakrata", "Kalsi", "Vikasnagar", "Sahaspur", "Raipur", "Doiwala"]
        },
        {
            "name": "Haridwar",
            "zone": "Sub-tropical Plains (Tarai)",
            "elevation": "250m - 350m",
            "rainfall": 1150.0,
            "soils": ["Deep Alluvial Silty Loam", "Sandy Loam"],
            "crops": ["Sugarcane", "Wheat", "Basmati Rice", "Mustard", "Potato"],
            "blocks": ["Bhagwanpur", "Roorkee", "Narsan", "Bahadrabad", "Laksar", "Khanpur"]
        },
        {
            "name": "Nainital",
            "zone": "Sub-temperate to High Hill Zone",
            "elevation": "600m - 2400m",
            "rainfall": 1400.0,
            "soils": ["Brown Hill Soil", "Rich Organic Forest Loam"],
            "crops": ["Peach", "Plum", "Apple", "Potato", "Soybean", "Maize"],
            "blocks": ["Bhimtal", "Ramgarh", "Dhari", "Betalghat", "Kotabagh", "Okhalkanda", "Haldwani", "Ramnagar"]
        },
        {
            "name": "Pithoragarh",
            "zone": "High Hills & Alpine Valleys",
            "elevation": "1100m - 3200m",
            "rainfall": 1250.0,
            "soils": ["Glacial Loam", "Gravelly Brown Soil"],
            "crops": ["Rajma (Munsyari)", "Finger Millet", "Buckwheat", "Potato", "Garlic"],
            "blocks": ["Munsiari", "Dharchula", "Didihat", "Berinag", "Gangolihat", "Pithoragarh", "Kanalichhina", "Vin"]
        },
        {
            "name": "Chamoli",
            "zone": "High Hills & Inner Himalayan Valleys",
            "elevation": "1200m - 3500m",
            "rainfall": 1300.0,
            "soils": ["Mountain Meadow Soil", "Gravelly Sandy Loam"],
            "crops": ["Apple", "Amaranth (Chaulai)", "Kidney Beans", "Potato", "Barley"],
            "blocks": ["Joshimath", "Ghat", "Dasholi", "Pokhari", "Karnaprayag", "Narayanbagar", "Tharali", "Dewal", "Gairsain"]
        },
        {
            "name": "Tehri Garhwal",
            "zone": "Sub-temperate Mid-hills",
            "elevation": "900m - 2300m",
            "rainfall": 1100.0,
            "soils": ["Brown Forest Soil", "Sandy Loam"],
            "crops": ["Finger Millet", "Barnyard Millet", "Ginger", "Turmeric", "Wheat"],
            "blocks": ["Chamba", "Narendra Nagar", "Devprayag", "Kirtinagar", "Jakhnidhar", "Pratapnagar", "Thauldhar", "Bhilangana", "Jaunpur"]
        },
        {
            "name": "Pauri Garhwal",
            "zone": "Sub-temperate Mid-hills",
            "elevation": "700m - 2100m",
            "rainfall": 1200.0,
            "soils": ["Shallow Rocky Loam", "Sandy Loam"],
            "crops": ["Finger Millet", "Mustard", "Wheat", "Citrus (Malta)", "Lentils"],
            "blocks": ["Kot", "Kaljikhal", "Pauri", "Pabo", "Thalisain", "Bironkhal", "Nainidanda", "Rikhnikhal", "Zahirikhal", "Dugadda", "Dwarikhal", "Ekeshwar", "Khirsu", "Pokhra"]
        },
        {
            "name": "Rudraprayag",
            "zone": "Mid to High Hills",
            "elevation": "850m - 2600m",
            "rainfall": 1350.0,
            "soils": ["Brown Forest Loam", "Colluvial Soil"],
            "crops": ["Mandua", "Chaulai", "Paddy", "Wheat", "Cardamom"],
            "blocks": ["Augustmuni", "Ukhimath", "Jakholi"]
        },
        {
            "name": "Uttarkashi",
            "zone": "High Hills & River Valleys",
            "elevation": "1150m - 3400m",
            "rainfall": 1250.0,
            "soils": ["Sandy Gravelly Loam", "High Organic Carbon Soil"],
            "crops": ["Apple (Harsil)", "Rajma", "Red Rice", "Walnut", "Potato"],
            "blocks": ["Bhatwari", "Dunda", "Chinyalisaur", "Naugaon", "Purola", "Mori"]
        },
        {
            "name": "Bageshwar",
            "zone": "Sub-temperate Mid-hills",
            "elevation": "1000m - 2400m",
            "rainfall": 1180.0,
            "soils": ["Brown Forest Loam", "Sandy Loam"],
            "crops": ["Finger Millet", "Soybean", "Rice", "Wheat", "Vegetables"],
            "blocks": ["Bageshwar", "Garur", "Kapkot"]
        },
        {
            "name": "Champawat",
            "zone": "Sub-temperate Mid-hills",
            "elevation": "1100m - 2100m",
            "rainfall": 1300.0,
            "soils": ["Brown Hill Loam", "Sandy Clay Loam"],
            "crops": ["Ginger", "Tea", "Mandua", "Bhatt", "Potato"],
            "blocks": ["Champawat", "Lohaghat", "Barakot", "Pati"]
        },
        {
            "name": "Udham Singh Nagar",
            "zone": "Sub-tropical Plains (Tarai)",
            "elevation": "200m - 280m",
            "rainfall": 1400.0,
            "soils": ["Fertile Deep Alluvial Clay Loam", "Tarai Muck Soil"],
            "crops": ["Basmati Rice", "Wheat", "Sugarcane", "Mustard", "Poplar", "Mentha"],
            "blocks": ["Jaspur", "Kashipur", "Bajpur", "Gadarpur", "Rudrapur", "Kichha", "Sitarganj", "Khatima"]
        }
    ]

    for d_data in districts_data:
        district = db.query(District).filter(District.district_name == d_data["name"]).first()
        if not district:
            district = District(
                id=str(uuid.uuid4()),
                state_id=uk_state.id,
                district_name=d_data["name"],
                agro_climatic_zone=d_data["zone"],
                elevation_bracket=d_data["elevation"],
                average_annual_rainfall_mm=d_data["rainfall"],
                dominant_soil_types=d_data["soils"],
                primary_crops=d_data["crops"]
            )
            db.add(district)
            db.flush()

            for b_name in d_data["blocks"]:
                block = Block(
                    id=str(uuid.uuid4()),
                    district_id=district.id,
                    block_name=b_name
                )
                db.add(block)

    # 3. Seed Crops Catalog
    crops_catalog = [
        {
            "name": "Finger Millet (Mandua / Ragi)",
            "scientific": "Eleusine coracana",
            "hindi": "मडुआ / रागी",
            "category": "cereal",
            "season": "Kharif",
            "min_ph": 5.0,
            "max_ph": 7.5,
            "water": 450.0,
            "duration": 115,
            "t_min": 15.0,
            "t_max": 33.0,
            "r_min": 400.0,
            "r_max": 900.0,
            "soils": ["Brown Forest Soil", "Sandy Loam", "Gravelly Loam"],
            "yield": 14.5,
            "cost": 14000.0
        },
        {
            "name": "Basmati Rice (Dehraduni Type)",
            "scientific": "Oryza sativa",
            "hindi": "बासमती धान",
            "category": "cereal",
            "season": "Kharif",
            "min_ph": 6.0,
            "max_ph": 7.8,
            "water": 1100.0,
            "duration": 135,
            "t_min": 20.0,
            "t_max": 35.0,
            "r_min": 800.0,
            "r_max": 1800.0,
            "soils": ["Alluvial Loam", "Clay Loam", "Tarai Silt"],
            "yield": 18.0,
            "cost": 22000.0
        },
        {
            "name": "Barnyard Millet (Jhangora)",
            "scientific": "Echinochloa frumentacea",
            "hindi": "झंगोरा",
            "category": "cereal",
            "season": "Kharif",
            "min_ph": 5.2,
            "max_ph": 7.2,
            "water": 350.0,
            "duration": 95,
            "t_min": 14.0,
            "t_max": 32.0,
            "r_min": 350.0,
            "r_max": 800.0,
            "soils": ["Marginal Hill Slope", "Sandy Loam"],
            "yield": 12.0,
            "cost": 11500.0
        },
        {
            "name": "Wheat (VL Gehun 907)",
            "scientific": "Triticum aestivum",
            "hindi": "गेहूं",
            "category": "cereal",
            "season": "Rabi",
            "min_ph": 6.0,
            "max_ph": 7.5,
            "water": 400.0,
            "duration": 140,
            "t_min": 8.0,
            "t_max": 25.0,
            "r_min": 250.0,
            "r_max": 650.0,
            "soils": ["Alluvial Loam", "Brown Forest Soil"],
            "yield": 16.5,
            "cost": 16500.0
        },
        {
            "name": "Rajma (Munsyari Kidney Beans)",
            "scientific": "Phaseolus vulgaris",
            "hindi": "मुनस्यारी राजमा",
            "category": "pulse",
            "season": "Kharif",
            "min_ph": 5.8,
            "max_ph": 7.0,
            "water": 500.0,
            "duration": 105,
            "t_min": 12.0,
            "t_max": 28.0,
            "r_min": 450.0,
            "r_max": 950.0,
            "soils": ["Well-Drained Loam", "Hill Valley Silt"],
            "yield": 8.5,
            "cost": 19000.0
        },
        {
            "name": "Black Soybean (Bhatt)",
            "scientific": "Glycine max (var.)",
            "hindi": "काली भट्ट",
            "category": "pulse",
            "season": "Kharif",
            "min_ph": 5.5,
            "max_ph": 7.2,
            "water": 450.0,
            "duration": 120,
            "t_min": 16.0,
            "t_max": 32.0,
            "r_min": 400.0,
            "r_max": 850.0,
            "soils": ["Sandy Clay Loam", "Brown Hill Soil"],
            "yield": 10.0,
            "cost": 13000.0
        },
        {
            "name": "Mustard / Rapeseed",
            "scientific": "Brassica juncea",
            "hindi": "सरसों / तोरिया",
            "category": "oilseed",
            "season": "Rabi",
            "min_ph": 6.0,
            "max_ph": 7.5,
            "water": 300.0,
            "duration": 110,
            "t_min": 10.0,
            "t_max": 25.0,
            "r_min": 200.0,
            "r_max": 500.0,
            "soils": ["Sandy Loam", "Alluvial Loam"],
            "yield": 7.5,
            "cost": 12500.0
        },
        {
            "name": "Himalayan Hill Potato",
            "scientific": "Solanum tuberosum",
            "hindi": "पहाड़ी आलू",
            "category": "vegetable",
            "season": "Zaid",
            "min_ph": 5.2,
            "max_ph": 6.8,
            "water": 550.0,
            "duration": 100,
            "t_min": 10.0,
            "t_max": 24.0,
            "r_min": 350.0,
            "r_max": 800.0,
            "soils": ["Friable Sandy Loam", "High Organic Carbon Soil"],
            "yield": 75.0,
            "cost": 32000.0
        }
    ]

    for c in crops_catalog:
        crop = db.query(Crop).filter(Crop.crop_name == c["name"]).first()
        if not crop:
            crop = Crop(
                id=str(uuid.uuid4()),
                crop_name=c["name"],
                scientific_name=c["scientific"],
                hindi_name=c["hindi"],
                category=c["category"],
                season=c["season"],
                min_ph=c["min_ph"],
                max_ph=c["max_ph"],
                water_requirement_mm=c["water"],
                growing_duration_days=c["duration"],
                temperature_min_c=c["t_min"],
                temperature_max_c=c["t_max"],
                rainfall_min_mm=c["r_min"],
                rainfall_max_mm=c["r_max"],
                recommended_soil_types=c["soils"],
                average_yield_quintal_per_acre=c["yield"],
                cost_of_cultivation_per_acre=c["cost"]
            )
            db.add(crop)

    db.flush()

    # 4. Seed Mandis & Market Prices
    mandis_data = [
        {"name": "Haldwani Mandi", "district": "Nainital", "phone": "05946-220145"},
        {"name": "Kashipur Mandi", "district": "Udham Singh Nagar", "phone": "05947-274112"},
        {"name": "Dehradun Niranjanpur Mandi", "district": "Dehradun", "phone": "0135-2627889"},
        {"name": "Haridwar Mandi", "district": "Haridwar", "phone": "01334-226500"},
        {"name": "Kotdwar Mandi", "district": "Pauri Garhwal", "phone": "01382-222310"},
        {"name": "Almora Hawalbagh Sub-Yard", "district": "Almora", "phone": "05962-230045"}
    ]

    created_mandis = []
    for m in mandis_data:
        mandi = db.query(Mandi).filter(Mandi.mandi_name == m["name"]).first()
        if not mandi:
            mandi = Mandi(
                id=str(uuid.uuid4()),
                mandi_name=m["name"],
                district_name=m["district"],
                state_name="Uttarakhand",
                contact_number=m["phone"],
                is_operational=True
            )
            db.add(mandi)
            db.flush()
        created_mandis.append(mandi)

    all_crops = db.query(Crop).all()
    today = date.today()

    price_benchmarks = {
        "Finger Millet (Mandua / Ragi)": (3200.0, 3800.0, 3550.0),
        "Basmati Rice (Dehraduni Type)": (3800.0, 4600.0, 4250.0),
        "Barnyard Millet (Jhangora)": (2800.0, 3400.0, 3100.0),
        "Wheat (VL Gehun 907)": (2275.0, 2600.0, 2450.0),
        "Rajma (Munsyari Kidney Beans)": (9500.0, 13500.0, 11800.0),
        "Black Soybean (Bhatt)": (4200.0, 5100.0, 4700.0),
        "Mustard / Rapeseed": (5200.0, 6100.0, 5650.0),
        "Himalayan Hill Potato": (1400.0, 2100.0, 1750.0)
    }

    existing_market_price = db.query(MarketPrice).filter(MarketPrice.arrival_date == today).first()
    if not existing_market_price:
        for crop in all_crops:
            if crop.crop_name in price_benchmarks:
                min_p, max_p, modal_p = price_benchmarks[crop.crop_name]
                for mandi in created_mandis:
                    # Add price variation across mandis
                    adjustment = 50.0 if "Haldwani" in mandi.mandi_name or "Dehradun" in mandi.mandi_name else -40.0
                    mp = MarketPrice(
                        mandi_id=mandi.id,
                        crop_id=crop.id,
                        arrival_date=today,
                        min_price_per_quintal=min_p + adjustment,
                        max_price_per_quintal=max_p + adjustment,
                        modal_price_per_quintal=modal_p + adjustment,
                        arrivals_in_tonnes=12.5
                    )
                    db.add(mp)

    # 5. Seed Knowledge Documents & Chunks for RAG
    docs_data = [
        {
            "title": "ICAR-VPKAS Package of Practices for Hill Millets (Mandua & Jhangora)",
            "source": "ICAR-Vivekananda Parvatiya Krishi Anusandhan Sansthan, Almora",
            "category": "Hill Millets Agronomy",
            "date": "2025-2026",
            "chunks": [
                "Finger millet (Eleusine coracana) or Mandua is the predominant kharif staple in Uttarakhand mid-hills. Ideal sowing time is June 10-25 with pre-monsoon showers. Recommended varieties include VL Mandua 352, VL Mandua 376, and VL Mandua 380, which exhibit genetic resistance to blast pathogen (Magnaporthe oryzae).",
                "Line sowing at 22.5 cm row-to-row spacing yields 25-30% higher than broadcasting. Seed rate is 3-4 kg/acre. Seed treatment with Trichoderma viride @ 5g/kg seed or Azotobacter biofertilizer significantly improves seedling vigor in organic hill soils.",
                "Barnyard millet (Jhangora) requires minimal irrigation and matures in 90-100 days. Intercropping Jhangora with black soybean (Bhatt) in a 2:1 ratio optimizes land equivalent ratio (LER > 1.35) and fixes nitrogen for subsequent rabi wheat."
            ]
        },
        {
            "title": "GBPUAT Agronomic Guide for Basmati Rice Cultivation in Tarai-Bhabhar",
            "source": "G.B. Pant University of Agriculture & Technology, Pantnagar",
            "category": "Cereal Crop Management",
            "date": "2025-2026",
            "chunks": [
                "Basmati rice requires fertile alluvial soils with high organic matter. Transplant 21-25 day old seedlings with 2-3 seedlings per hill at 20x15 cm spacing. Zinc deficiency (Khaira disease) appears 2-3 weeks after transplanting; manage with foliar spray of 0.5% Zinc Sulphate + 0.25% Slaked Lime.",
                "Water management in Basmati: maintain 2-3 cm standing water during transplanting and tillering. Drain field 7-10 days before harvest to ensure uniform grain ripening and preserve aroma."
            ]
        },
        {
            "title": "Integrated Pest & Disease Management in Himalayan Vegetables & Pulses",
            "source": "Krishi Vigyan Kendra (KVK) Matela, Almora",
            "category": "Plant Protection & IPM",
            "date": "2025-2026",
            "chunks": [
                "Munsyari Rajma (Kidney Beans) is susceptible to anthracnose and root rot during continuous overcast days. Apply seed treatment with Trichoderma harzianum @ 4g/kg seed. Maintain terrace drainage channels to prevent root asphyxiation.",
                "Yellow rust in rabi wheat spreads rapidly when daytime temperatures stay between 10-15°C accompanied by heavy dew. Spray cow urine formulation or approved biological bio-agents at first foci sighting."
            ]
        }
    ]

    for d in docs_data:
        doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.title == d["title"]).first()
        if not doc:
            doc = KnowledgeDocument(
                id=str(uuid.uuid4()),
                title=d["title"],
                source_organization=d["source"],
                category=d["category"],
                publication_date=d["date"],
                document_type="Research Bulletin & Package of Practices",
                is_verified=True
            )
            db.add(doc)
            db.flush()

            for idx, c_text in enumerate(d["chunks"]):
                chunk = KnowledgeChunk(
                    id=str(uuid.uuid4()),
                    document_id=doc.id,
                    chunk_text=c_text,
                    chunk_index=idx,
                    metadata_json={"source": d["source"], "category": d["category"]}
                )
                db.add(chunk)

    db.commit()
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    from app.db.session import SessionLocal
    db = SessionLocal()
    run_seed(db)
    db.close()
