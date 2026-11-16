import { apiClient } from './apiClient';

export interface AdvisoryIntervention {
  type: string;
  remedy_name: string;
  dosage_per_liter: string;
  application_method: string;
  precaution: string;
}

export interface AdvisoryResponse {
  id: string;
  crop_name: string;
  crop_growth_stage: string;
  suspected_pest_or_pathogen: string;
  diagnostic_category: string;
  confidence_level: string;
  advisory_response: string;
  recommended_interventions: AdvisoryIntervention[];
  preventive_measures: string[];
  disclaimer: string;
  is_demo: boolean;
  created_at: string;
}

export interface AdvisoryInput {
  farm_id?: string;
  crop_name: string;
  crop_growth_stage: string;
  observed_symptoms: string;
  farming_conditions: string;
  affected_area_percentage: number;
}

export const advisoryService = {
  submitCase: async (payload: AdvisoryInput): Promise<AdvisoryResponse> => {
    return apiClient.post<AdvisoryResponse>('/advisory/cases', payload);
  },

  getHistory: async (farmId?: string): Promise<AdvisoryResponse[]> => {
    const query = farmId ? `?farm_id=${farmId}` : '';
    return apiClient.get<AdvisoryResponse[]>(`/advisory/cases${query}`);
  },

  getCaseById: async (caseId: string): Promise<AdvisoryResponse> => {
    return apiClient.get<AdvisoryResponse>(`/advisory/cases/${caseId}`);
  }
};
