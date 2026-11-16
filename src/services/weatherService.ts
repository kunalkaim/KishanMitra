import { apiClient } from './apiClient';

export interface WeatherForecastDay {
  date: string;
  day: string;
  temp_max: number;
  temp_min: number;
  humidity: number;
  rainfall_prob: number;
  condition: string;
  icon: string;
  advisory: string;
}

export interface WeatherData {
  district_name: string;
  temperature_min_c: number;
  temperature_max_c: number;
  humidity_percent: number;
  rainfall_mm: number;
  wind_speed_kmh: number;
  condition_text: string;
  forecast: WeatherForecastDay[];
  agricultural_alert?: string;
}

export const weatherService = {
  getWeather: async (district: string = 'Almora'): Promise<WeatherData> => {
    return apiClient.get<WeatherData>(`/weather/?district=${encodeURIComponent(district)}`);
  }
};
