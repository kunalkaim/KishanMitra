// KisanMitra Core Types

export type Language = 'en' | 'hi';

export interface FarmerProfile {
  id: string;
  name: string;
  age?: number;
  phone: string;
  preferredLanguage: Language;
  state: string;
  district: string;
  village: string;
  farmingExperienceYears: number;
  farmingPractices: 'organic' | 'conventional' | 'natural' | 'integrated';
  soilHealthCardNumber?: string;
  avatarUrl?: string;
}

export interface Farm {
  id: string;
  name: string;
  size: number; // in acres
  sizeUnit: 'acres' | 'hectares';
  state: string;
  district: string;
  block: string;
  village: string;
  latitude?: number;
  longitude?: number;
  elevation?: number; // in meters
  soilType: 'alluvial' | 'mountain' | 'red' | 'black' | 'sandy' | 'clayey' | 'loamy';
  soilPh: number;
  nitrogen: number; // kg/ha
  phosphorus: number; // kg/ha
  potassium: number; // kg/ha
  organicCarbon: number; // %
  electricalConductivity: number; // dS/m
  irrigationType: 'drip' | 'sprinkler' | 'canal' | 'borewell' | 'rainfed';
  waterAvailability: 'abundant' | 'moderate' | 'scarce';
  previousCrops: string[];
  currentSeason: 'Kharif' | 'Rabi' | 'Zaid';
  availableBudget: number; // in INR
  isPrimary?: boolean;
}

export interface CropRecommendationInput {
  farmId?: string;
  state: string;
  district: string;
  block?: string;
  village?: string;
  elevation: number;
  soilType: string;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  soilPh: number;
  organicCarbon: number;
  electricalConductivity: number;
  temperature: number;
  humidity: number;
  rainfall: number;
  season: 'Kharif' | 'Rabi' | 'Zaid';
  farmSize: number;
  irrigationAvailability: 'abundant' | 'moderate' | 'scarce';
  availableBudget: number;
  previousCrop: string;
  farmingMethod: 'organic' | 'conventional' | 'natural' | 'integrated';
}

export interface AIModelPrediction {
  modelName: string;
  topCrop: string;
  confidence: number;
  weight: number;
  keyFactors: string[];
  logicSummary: string;
}

export interface RAGCitation {
  documentTitle: string;
  publisher: string;
  pageStart: number;
  pageEnd?: number;
  snippet: string;
  retrievalScore: number;
}

export interface RecommendedCrop {
  id: string;
  rank?: number;
  name: string;
  hindiName: string;
  suitabilityScore: number; // 0 - 100
  image: string;
  waterRequirement: 'Low' | 'Medium' | 'High';
  growingDurationDays: number;
  season: 'Kharif' | 'Rabi' | 'Zaid' | 'Annual';
  soilCompatibility: 'High' | 'Moderate' | 'Good';
  expectedYieldQuintalsPerAcre: number;
  estimatedNetProfitPerAcre: number;
  shortExplanation: string;
  whyRecommended?: string;
  modelScores?: {
    fuzzyLogic: number;
    gaussianNb: number;
    decisionTree: number;
  };
  primaryFavorableFactors?: string[];
  limitingFactors?: string[];
  xaiInfluences: {
    factor: string;
    impact: number; // -100 to +100
    description: string;
  }[];
  // Layer 2: RAG Knowledge Evidence
  verifiedPackageOfPractices?: string[];
  ragCitations?: RAGCitation[];
  // Layer 3: APMC Market Economics
  mandiName?: string;
  modalPricePerQuintal?: number;
  minPricePerQuintal?: number;
  maxPricePerQuintal?: number;
  estimatedCostPerAcre?: number;
  estimatedGrossRevenuePerAcre?: number;
  benefitCostRatio?: number;
  breakevenYieldPerAcre?: number;
  breakevenPricePerQuintal?: number;
  economicDisclaimer?: string;
  // Layer 4: Agromet Risk Flags
  weatherRiskFlags?: string[];
  districtElevationAlert?: string;
}

export interface EnsembleRecommendationResult {
  id: string;
  timestamp: string;
  input: CropRecommendationInput;
  recommendedCrops: RecommendedCrop[];
  ensembleConfidence: number;
  modelAgreement: 'Very High' | 'High' | 'Moderate';
  ensembleBreakdown: AIModelPrediction[];
  summaryExplanation: string;
  generalAgriculturalAdvisory?: string;
  resolvedFeatures?: Record<string, number>;
  aiEngineInfo?: any;
}

export interface WeatherData {
  location: string;
  state: string;
  temperature: number;
  tempMin: number;
  tempMax: number;
  humidity: number;
  rainfall: number; // mm
  rainfallProbability: number; // %
  windSpeed: number; // km/h
  windDirection: string;
  condition: string;
  icon: string;
  uvIndex: number;
  sowingWindowStatus: 'Optimal' | 'Favorable' | 'Delay Sowing';
  advisory: string;
  alerts: string[];
  forecast7Day: {
    day: string;
    date: string;
    tempMin: number;
    tempMax: number;
    rainfallProb: number;
    rainfallMm: number;
    humidity: number;
    condition: string;
    icon: string;
  }[];
}

export interface MandiPrice {
  id: string;
  state: string;
  district: string;
  mandiName: string;
  commodity: string;
  variety: string;
  minPrice: number; // INR/Quintal
  maxPrice: number;
  modalPrice: number;
  priceDate: string;
  dailyChangePercentage: number;
  arrivalVolumeQuintals: number;
  priceTrend: 'up' | 'down' | 'stable';
}

export interface PlantDiseaseDiagnosis {
  id: string;
  cropType: string;
  imageUrl: string;
  diseaseName: string;
  scientificName: string;
  status: 'Infected' | 'Healthy' | 'Nutrient Deficiency';
  confidenceScore: number;
  severity: 'Mild' | 'Moderate' | 'Severe';
  symptoms: string[];
  possibleCauses: string[];
  preventiveMeasures: string[];
  organicTreatment: string[];
  recommendedAction: string;
  disclaimer: string;
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  answerMode?: string;
  providerName?: string;
  citations?: {
    sourceId?: string;
    title: string;
    source: string;
    page?: string;
    url?: string;
    snippet?: string;
  }[];
  suggestedFollowUps?: string[];
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  category: 'Crop Advisory' | 'Government Scheme' | 'Soil Health' | 'Disease Management' | 'Irrigation';
  cropTag: string;
  language: string;
  region: string;
  fileSize: string;
  uploadDate: string;
  status: 'Indexed & Ready' | 'Processing' | 'Failed';
  vectorChunksCount: number;
}

export interface FarmerFeedback {
  id: string;
  farmId: string;
  farmName: string;
  cropCultivated: string;
  followedRecommendation: 'Yes' | 'Partially' | 'No';
  sowingDate: string;
  harvestDate: string;
  actualYield: number; // quintals/acre
  predictedYield: number;
  actualCost: number; // INR
  estimatedCost: number;
  actualSellingPrice: number; // INR/quintal
  estimatedSellingPrice: number;
  problemsEncountered: string[];
  rating: number; // 1-5
  notes: string;
  status: 'Pending Review' | 'Validated' | 'Used in Model Retraining Backlog';
  createdAt: string;
}
