import { apiClient } from './apiClient';

export interface Crop {
  id: string;
  crop_name: string;
  scientific_name?: string;
  hindi_name: string;
  category: string;
  season: string;
  min_ph: number;
  max_ph: number;
  water_requirement_mm: number;
  growing_duration_days: number;
  average_yield_quintal_per_acre: number;
  cost_of_cultivation_per_acre: number;
}

export interface RecommendationResultItem {
  crop_id: string;
  crop_name: string;
  hindi_name: string;
  category: string;
  suitability_score: number;
  fuzzy_score: number;
  bayesian_probability: number;
  decision_tree_score: number;
  rank: number;
  reasoning_summary: string;
  agronomic_justification: string;
  expected_yield_per_acre: number;
  estimated_revenue_per_acre: number;
  estimated_cost_per_acre: number;
  net_profit_per_acre: number;
  risk_factors: string[];
  cultivation_steps: Array<{
    phase: string;
    timeline: string;
    action: string;
    inputs: string;
  }>;
}

export interface RecommendationResponse {
  request_id: string;
  farm_id: string;
  district: string;
  season: string;
  is_demo: boolean;
  recommended_crops: RecommendationResultItem[];
  created_at: string;
}

export const cropService = {
  listCrops: async (season?: string, category?: string): Promise<Crop[]> => {
    let query = '';
    const params = new URLSearchParams();
    if (season) params.append('season', season);
    if (category) params.append('category', category);
    if (params.toString()) query = `?${params.toString()}`;
    return apiClient.get<Crop[]>(`/crops/${query}`);
  },

  getCropById: async (id: string): Promise<Crop> => {
    return apiClient.get<Crop>(`/crops/${id}`);
  },

  getRecommendations: async (payload: {
    farm_id: string;
    season: string;
    target_market?: string;
    budget_per_acre?: number;
    irrigation_available?: boolean;
    soil_ph?: number;
    nitrogen_kg_ha?: number;
    phosphorus_kg_ha?: number;
    potassium_kg_ha?: number;
  }): Promise<RecommendationResponse> => {
    return apiClient.post<RecommendationResponse>('/recommendations/', payload);
  },

  getRecommendationHistory: async (farmId?: string): Promise<RecommendationResponse[]> => {
    const query = farmId ? `?farm_id=${farmId}` : '';
    return apiClient.get<RecommendationResponse[]>(`/recommendations/history${query}`);
  }
};
