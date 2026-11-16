import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.schemas.advisory import AdvisoryInput, AdvisoryResponse, AdvisoryIntervention


class PestDiseaseAdvisoryService:
    """
    Expert Agronomic Advisory Engine for Pest & Disease Inquiries (Text-Based).
    Analyzes farmer-reported symptoms, growth stage, and microclimate conditions
    using verified ICAR-VPKAS and GBPUAT Pantnagar hill agriculture pest knowledge.
    """

    ADVISORY_RULES = [
        {
            "keywords": ["spindle", "blast", "lesion", "grey centre", "brown border", "neck"],
            "crops": ["rice", "paddy", "finger millet", "mandua", "ragi"],
            "disease": "Blast (Magnaporthe oryzae / Pyricularia grisea)",
            "category": "Fungal Disease",
            "confidence": "High (Characteristic Spindle Lesion Match)",
            "advisory": "Symptoms indicate foliar or neck blast, promoted by persistent cloudiness, high humidity (>90%), and heavy morning dew in terrace valleys.",
            "interventions": [
                AdvisoryIntervention(
                    type="Organic / Bio-control",
                    remedy_name="Trichoderma viride or Pseudomonas fluorescens",
                    dosage_per_liter="5-10 g / litre of water",
                    application_method="Foliar spray during early morning or evening hours",
                    precaution="Do not mix with synthetic copper fungicides."
                ),
                AdvisoryIntervention(
                    type="Botanical Extract",
                    remedy_name="Neem Seed Kernel Extract (NSKE 5%) or Azadirachtin 1500 ppm",
                    dosage_per_liter="3 ml / litre of water",
                    application_method="Thorough foliar coverage targeting lower and upper canopy",
                    precaution="Ensure uniform spraying on both leaf surfaces."
                ),
                AdvisoryIntervention(
                    type="Cultural Practice",
                    remedy_name="Canopy Aeration & Nitrogen Regulation",
                    dosage_per_liter="N/A",
                    application_method="Avoid excessive top-dressing of quick-release urea; maintain clean drainage channels to reduce terrace humidity.",
                    precaution="Excessive nitrogen exacerbates cell wall softening and pathogen penetration."
                )
            ],
            "preventives": [
                "Seed treatment with Trichoderma viride @ 5g/kg seed before future sowings",
                "Maintain optimal plant spacing to promote sunlight penetration in hill terraces",
                "Collect and burn infected stubble post-harvest to disrupt fungal overwintering"
            ]
        },
        {
            "keywords": ["yellow", "rust", "stripe", "pustule", "powder"],
            "crops": ["wheat", "barley"],
            "disease": "Yellow Rust / Stripe Rust (Puccinia striiformis)",
            "category": "Fungal Disease",
            "confidence": "High (Stripe Rust Symptom Profile)",
            "advisory": "Yellow pustules arranged in linear stripes on leaf veins are typical of Stripe Rust, commonly triggered by cool temperatures (10-15°C) and high moisture in Uttarakhand mid and high hills.",
            "interventions": [
                AdvisoryIntervention(
                    type="Bio-fungicide",
                    remedy_name="Bacillus subtilis bio-formulation",
                    dosage_per_liter="4 g / litre of water",
                    application_method="Spray at the first appearance of solitary yellow foci in the field",
                    precaution="Ensure sprayer nozzle is cleaned prior to application."
                ),
                AdvisoryIntervention(
                    type="Botanical Formulation",
                    remedy_name="Cow Urine + Fermented Neem Leaf Extract (Dashaparni Arka)",
                    dosage_per_liter="10% aqueous solution",
                    application_method="Foliar spray at 7-day intervals",
                    precaution="Filter thoroughly to avoid clogging sprayer nozzles."
                )
            ],
            "preventives": [
                "Cultivate resistant wheat cultivars recommended for Northern Hill Zone (e.g., VL Gehun 892, VL Gehun 907)",
                "Avoid late sowing in vulnerable valley pockets",
                "Monitor boundary rows weekly during December-February"
            ]
        },
        {
            "keywords": ["borer", "dead heart", "stem", "frass", "white ear"],
            "crops": ["rice", "paddy", "maize"],
            "disease": "Stem Borer (Scirpophaga incertulas / Chilo partellus)",
            "category": "Insect Pest",
            "confidence": "High (Dead-heart & Frass Diagnostic)",
            "advisory": "Larval boring inside the central stem blocks vascular nutrient flow, producing 'dead hearts' in vegetative stage and 'white ears' in reproductive stage.",
            "interventions": [
                AdvisoryIntervention(
                    type="Pheromone Monitoring",
                    remedy_name="Yellow Stem Borer Pheromone Traps",
                    dosage_per_liter="5 traps / acre",
                    application_method="Install traps at canopy height across the field",
                    precaution="Replace septa every 21 days for sustained attractant efficacy."
                ),
                AdvisoryIntervention(
                    type="Biological Control",
                    remedy_name="Trichogramma japonicum egg parasitoid cards (Trichocards)",
                    dosage_per_liter="2 cards (approx. 50,000 parasitoids) / acre",
                    application_method="Staple pieces of cards beneath leaf surfaces at 7-day intervals",
                    precaution="Release during late afternoon to prevent predator bird feeding."
                ),
                AdvisoryIntervention(
                    type="Botanical Spray",
                    remedy_name="Neem Oil (10,000 ppm)",
                    dosage_per_liter="2.5 ml / litre of water with mild soap",
                    application_method="Target stem base and leaf axils where young larvae wander",
                    precaution="Spray before sunset."
                )
            ],
            "preventives": [
                "Clip seedling leaf tips before transplanting to destroy egg masses",
                "Promote natural spider and dragonfly populations by avoiding non-selective chemical spraying",
                "Deep summer ploughing to expose pupae to predatory birds"
            ]
        },
        {
            "keywords": ["khaira", "chlorosis", "zinc", "bronze", "rusty", "stunted"],
            "crops": ["rice", "paddy", "wheat", "maize"],
            "disease": "Khaira Disease (Zinc Deficiency Physiological Disorder)",
            "category": "Nutrient Deficiency",
            "confidence": "High (Zinc Induced Foliar Bronzing)",
            "advisory": "Bronze pigmentation, reddish-brown spotting on older leaves, and stunted seedling growth denote severe Zinc deficiency, common in high-calcium or continuously waterlogged terrace soils.",
            "interventions": [
                AdvisoryIntervention(
                    type="Micronutrient Correction",
                    remedy_name="Zinc Sulphate (Heptahydrate 21%) + Slaked Lime Solution",
                    dosage_per_liter="5 g Zinc Sulphate + 2.5 g Slaked Lime per litre of water",
                    application_method="Foliar spray twice at 10-day intervals",
                    precaution="Neutralize zinc sulphate with lime to prevent foliar scorching."
                )
            ],
            "preventives": [
                "Basal soil application of 10 kg/acre Zinc Sulphate during field preparation",
                "Incorporate green manure (Dhaincha/Sunn hemp) to enhance micronutrient bioavailability",
                "Avoid excessive phosphorus application which inhibits zinc uptake"
            ]
        }
    ]

    DEFAULT_ADVISORY = {
        "disease": "Foliar Leaf Spot Complex & Microclimate Stress",
        "category": "Fungal / Environmental Complex",
        "confidence": "Moderate (Agronomic Rule Evaluation)",
        "advisory": "Reported symptoms reflect foliar pathogen activity exacerbated by damp microclimate conditions, poor terrace air circulation, or localized nutrient imbalance.",
        "interventions": [
            AdvisoryIntervention(
                type="Broad-Spectrum Bio-fungicide",
                remedy_name="Trichoderma harzianum + Pseudomonas fluorescens consortium",
                dosage_per_liter="5 g / litre of water",
                application_method="Thorough foliar spray wetting both leaf surfaces",
                precaution="Apply during calm weather with no rainfall forecast for 4 hours."
            ),
            AdvisoryIntervention(
                type="Organic Botanical Protection",
                remedy_name="Azadirachtin 3000 ppm (Neem Formulation)",
                dosage_per_liter="2 ml / litre of water",
                application_method="Spray evenly across the crop canopy at dusk",
                precaution="Mix with 0.5 ml liquid soap per litre as wetting agent."
            )
        ],
        "preventives": [
            "Ensure effective drainage in terrace steps to prevent root asphyxiation",
            "Remove and compost weed hosts growing along terrace bunds",
            "Submit soil sample for testing to rule out micronutrient deficiencies"
        ]
    }

    def generate_advisory(self, input_data: AdvisoryInput) -> AdvisoryResponse:
        symptoms_lower = input_data.observed_symptoms.lower()
        crop_lower = input_data.crop_name.lower()
        matched = None

        for rule in self.ADVISORY_RULES:
            # Check crop match
            crop_match = any(c in crop_lower for c in rule["crops"])
            # Check keyword match
            keyword_match = any(kw in symptoms_lower for kw in rule["keywords"])
            
            if crop_match and keyword_match:
                matched = rule
                break
            elif keyword_match:
                matched = rule

        if not matched:
            matched = self.DEFAULT_ADVISORY

        return AdvisoryResponse(
            id=str(uuid.uuid4()),
            crop_name=input_data.crop_name,
            crop_growth_stage=input_data.crop_growth_stage,
            suspected_pest_or_pathogen=matched["disease"],
            diagnostic_category=matched["category"],
            confidence_level=matched["confidence"],
            advisory_response=matched["advisory"],
            recommended_interventions=matched["interventions"],
            preventive_measures=matched["preventives"],
            disclaimer="Advisory generated on the basis of reported agronomic symptoms. For severe infestations or chemical pesticide usage, please consult your Block Technology Manager (ATMA) or Krishi Vigyan Kendra specialist.",
            is_demo=True,
            created_at=datetime.now(timezone.utc)
        )


advisory_service = PestDiseaseAdvisoryService()
