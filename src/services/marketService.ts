import { apiClient } from './apiClient';

export interface MarketPrice {
  id: string;
  mandi_id: string;
  mandi_name: string;
  district_name: string;
  crop_id: string;
  crop_name: string;
  arrival_date: string;
  min_price_per_quintal: number;
  max_price_per_quintal: number;
  modal_price_per_quintal: number;
  arrivals_in_tonnes: number;
  trend: string;
}

export interface MandiComparison {
  crop_name: string;
  prices: MarketPrice[];
  highest_mandi: string;
  highest_price: number;
  lowest_mandi: string;
  lowest_price: number;
  recommendation: string;
}

export const marketService = {
  getPrices: async (district?: string, cropName?: string): Promise<MarketPrice[]> => {
    const params = new URLSearchParams();
    if (district) params.append('district', district);
    if (cropName) params.append('crop_name', cropName);
    const query = params.toString() ? `?${params.toString()}` : '';
    return apiClient.get<MarketPrice[]>(`/market/prices${query}`);
  },

  getComparison: async (cropName: string): Promise<MandiComparison> => {
    return apiClient.get<MandiComparison>(`/market/comparison?crop_name=${encodeURIComponent(cropName)}`);
  }
};
