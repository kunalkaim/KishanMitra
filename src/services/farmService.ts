import { apiClient } from './apiClient';

export interface Farm {
  id: string;
  farmer_id: string;
  farm_name: string;
  state: string;
  district: string;
  block?: string;
  village?: string;
  pincode?: string;
  total_area_acres: number;
  cultivated_area_acres: number;
  irrigation_type: string;
  soil_type: string;
  ownership_type: string;
  latitude?: number;
  longitude?: number;
  elevation_meters?: number;
  is_active: boolean;
  created_at: string;
}

export interface SoilTest {
  id: string;
  farm_id: string;
  test_date: string;
  soil_ph: number;
  organic_carbon_percent: number;
  nitrogen_kg_ha: number;
  phosphorus_kg_ha: number;
  potassium_kg_ha: number;
  sulphur_ppm?: number;
  zinc_ppm?: number;
  iron_ppm?: number;
  electrical_conductivity?: number;
  testing_lab_name?: string;
}

export const farmService = {
  listFarms: async (): Promise<Farm[]> => {
    return apiClient.get<Farm[]>('/farms/');
  },

  getFarmById: async (id: string): Promise<Farm> => {
    return apiClient.get<Farm>(`/farms/${id}`);
  },

  createFarm: async (farm: Omit<Farm, 'id' | 'farmer_id' | 'is_active' | 'created_at'>): Promise<Farm> => {
    return apiClient.post<Farm>('/farms/', farm);
  },

  updateFarm: async (id: string, farm: Partial<Farm>): Promise<Farm> => {
    return apiClient.put<Farm>(`/farms/${id}`, farm);
  },

  deleteFarm: async (id: string): Promise<void> => {
    return apiClient.delete<void>(`/farms/${id}`);
  },

  listSoilTests: async (farmId?: string): Promise<SoilTest[]> => {
    const query = farmId ? `?farm_id=${farmId}` : '';
    return apiClient.get<SoilTest[]>(`/soil/${query}`);
  },

  recordSoilTest: async (soilData: Omit<SoilTest, 'id'>): Promise<SoilTest> => {
    return apiClient.post<SoilTest>('/soil/', soilData);
  }
};
