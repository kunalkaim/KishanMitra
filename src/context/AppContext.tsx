import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  FarmerProfile,
  Farm,
  WeatherData,
  MandiPrice,
  EnsembleRecommendationResult,
  PlantDiseaseDiagnosis,
  FarmerFeedback,
  Language,
  CropRecommendationInput
} from '../types';
import {
  initialFarmerProfile,
  initialFarms,
  demoWeatherData,
  demoMandiPrices,
  demoRecommendationResult,
  demoDiseaseDiagnoses,
  demoFeedbacks,
  uttarakhandDistricts
} from '../data/demoData';
import { CropRecommendationService, WeatherService } from '../services/apiAdapters';
import { translations } from '../data/translations';
import { calculateDynamicEnsemble } from '../services/cropRecommendationEngine';

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: 'warning' | 'info' | 'success' | 'alert';
  timestamp: string;
  read: boolean;
  link?: string;
}

interface AppContextType {
  profile: FarmerProfile;
  updateProfile: (updated: Partial<FarmerProfile>) => void;
  farms: Farm[];
  activeFarmId: string;
  setActiveFarmId: (id: string) => void;
  activeFarm: Farm;
  addFarm: (farm: Omit<Farm, 'id'>) => Farm;
  updateFarm: (id: string, updated: Partial<Farm>) => void;
  deleteFarm: (id: string) => void;
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
  weather: WeatherData;
  setWeatherDistrict: (districtName: string) => void;
  mandiPrices: MandiPrice[];
  currentRecommendation: EnsembleRecommendationResult;
  isCalculatingRecommendation: boolean;
  generateRecommendation: (input: CropRecommendationInput) => EnsembleRecommendationResult;
  diagnosesHistory: PlantDiseaseDiagnosis[];
  addDiagnosis: (diag: Omit<PlantDiseaseDiagnosis, 'id' | 'timestamp'>) => PlantDiseaseDiagnosis;
  feedbacks: FarmerFeedback[];
  addFeedback: (fb: Omit<FarmerFeedback, 'id' | 'createdAt' | 'status'>) => void;
  notifications: NotificationItem[];
  markNotificationAsRead: (id: string) => void;
  clearAllNotifications: () => void;
  toast: { message: string; type: 'success' | 'error' | 'info' } | null;
  showToast: (message: string, type?: 'success' | 'error' | 'info') => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);



const initialNotifications: NotificationItem[] = [
  {
    id: 'n-1',
    title: 'Rainfall Alert for Dehradun',
    message: 'Convective rainfall predicted in 4 days. Plan rice harvesting or spray schedule accordingly.',
    type: 'warning',
    timestamp: '2 hours ago',
    read: false,
    link: '/weather'
  },
  {
    id: 'n-2',
    title: 'Basmati Paddy Price Surge',
    message: 'Dehradun APMC mandi reported a +3.8% increase in Basmati modal prices today (₹3,850/q).',
    type: 'success',
    timestamp: '5 hours ago',
    read: false,
    link: '/market-intelligence'
  },
  {
    id: 'n-3',
    title: 'Scheduled Irrigation Due',
    message: 'Shivalik Terraced Field requires scheduled drip irrigation tomorrow morning (6:00 AM).',
    type: 'info',
    timestamp: '1 day ago',
    read: true,
    link: '/smart-advisor'
  }
];

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [profile, setProfile] = useState<FarmerProfile>(() => {
    const saved = localStorage.getItem('kisanmitra_profile');
    return saved ? JSON.parse(saved) : initialFarmerProfile;
  });

  const [farms, setFarms] = useState<Farm[]>(() => {
    const saved = localStorage.getItem('kisanmitra_farms');
    return saved ? JSON.parse(saved) : initialFarms;
  });

  const [activeFarmId, setActiveFarmId] = useState<string>(() => {
    return farms[0]?.id || 'farm-1';
  });

  const [language, setLanguage] = useState<Language>(() => {
    const saved = localStorage.getItem('kisanmitra_lang') as Language;
    return saved || 'en';
  });

  const [weather, setWeather] = useState<WeatherData>(demoWeatherData);
  const [mandiPrices] = useState<MandiPrice[]>(demoMandiPrices);
  const [currentRecommendation, setCurrentRecommendation] = useState<EnsembleRecommendationResult>(demoRecommendationResult);
  const [isCalculatingRecommendation, setIsCalculatingRecommendation] = useState<boolean>(false);
  
  const [diagnosesHistory, setDiagnosesHistory] = useState<PlantDiseaseDiagnosis[]>(() => {
    const saved = localStorage.getItem('kisanmitra_diagnoses');
    return saved ? JSON.parse(saved) : demoDiseaseDiagnoses;
  });

  const [feedbacks, setFeedbacks] = useState<FarmerFeedback[]>(() => {
    const saved = localStorage.getItem('kisanmitra_feedbacks');
    return saved ? JSON.parse(saved) : demoFeedbacks;
  });

  const [notifications, setNotifications] = useState<NotificationItem[]>(initialNotifications);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  useEffect(() => {
    localStorage.setItem('kisanmitra_profile', JSON.stringify(profile));
  }, [profile]);

  useEffect(() => {
    localStorage.setItem('kisanmitra_farms', JSON.stringify(farms));
  }, [farms]);

  useEffect(() => {
    localStorage.setItem('kisanmitra_lang', language);
  }, [language]);

  useEffect(() => {
    localStorage.setItem('kisanmitra_diagnoses', JSON.stringify(diagnosesHistory));
  }, [diagnosesHistory]);

  useEffect(() => {
    localStorage.setItem('kisanmitra_feedbacks', JSON.stringify(feedbacks));
  }, [feedbacks]);

  const activeFarm = farms.find(f => f.id === activeFarmId) || farms[0] || initialFarms[0];

  useEffect(() => {
    if (activeFarm && activeFarm.district) {
      setWeatherDistrict(activeFarm.district);
      WeatherService.getLiveWeather(activeFarm.district).then(liveWeather => {
        if (liveWeather) {
          setWeather(liveWeather);
        }
      }).catch(err => {
        console.warn('Live weather telemetry fetch failed:', err);
      });
    }
  }, [activeFarmId, activeFarm?.district]);

  const updateProfile = (updated: Partial<FarmerProfile>) => {
    setProfile(prev => ({ ...prev, ...updated }));
    showToast('Profile updated successfully!', 'success');
  };

  const addFarm = (newFarmData: Omit<Farm, 'id'>): Farm => {
    const newId = `farm-${Date.now()}`;
    const newFarm: Farm = { ...newFarmData, id: newId };
    setFarms(prev => [...prev, newFarm]);
    setActiveFarmId(newId);
    showToast(`Farm "${newFarm.name}" added successfully!`, 'success');
    return newFarm;
  };

  const updateFarm = (id: string, updated: Partial<Farm>) => {
    setFarms(prev => prev.map(f => f.id === id ? { ...f, ...updated } : f));
    showToast('Farm details updated!', 'success');
  };

  const deleteFarm = (id: string) => {
    if (farms.length <= 1) {
      showToast('You must maintain at least one registered farm.', 'error');
      return;
    }
    setFarms(prev => prev.filter(f => f.id !== id));
    if (activeFarmId === id) {
      const remaining = farms.filter(f => f.id !== id);
      setActiveFarmId(remaining[0].id);
    }
    showToast('Farm removed from registry.', 'info');
  };

  const t = (key: string): string => {
    return translations[language]?.[key] || translations.en[key] || key;
  };

  const setWeatherDistrict = (districtName: string) => {
    const found = uttarakhandDistricts.find(d => d.name.toLowerCase() === districtName.toLowerCase());
    if (found) {
      setWeather(prev => ({
        ...prev,
        location: `${found.name} District`,
        state: 'Uttarakhand',
        temperature: Math.round((26 - (found.lat - 29) * 2.5) * 10) / 10,
        rainfall: found.avgRainfallMm > 1400 ? 2.5 : 0.0,
      }));
    }
  };

  const generateRecommendation = (input: CropRecommendationInput): EnsembleRecommendationResult => {
    // 1. Calculate dynamic hybrid ensemble based on full agronomic parameter scoring
    const result = calculateDynamicEnsemble(input);
    setCurrentRecommendation(result);
    setIsCalculatingRecommendation(true);

    // 2. Query live FastAPI backend (with resilient fallback to dynamic model)
    CropRecommendationService.getUnifiedRecommendation(input, activeFarm.id)
      .then(liveResult => {
        if (liveResult && liveResult.recommendedCrops && liveResult.recommendedCrops.length > 0) {
          setCurrentRecommendation(liveResult);
          showToast(
            language === 'hi'
              ? 'लाइव एआई मॉडल अनुशंसा सफलतापूर्वक प्राप्त हुई!'
              : 'Live Unified AI recommendation generated successfully!',
            'success'
          );
        }
      })
      .catch(err => {
        console.warn('Live backend response fallback to dynamic model:', err);
      })
      .finally(() => {
        setIsCalculatingRecommendation(false);
      });

    return result;
  };

  const addDiagnosis = (diagData: Omit<PlantDiseaseDiagnosis, 'id' | 'timestamp'>): PlantDiseaseDiagnosis => {
    const newDiag: PlantDiseaseDiagnosis = {
      ...diagData,
      id: `diag-${Date.now()}`,
      timestamp: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    };
    setDiagnosesHistory(prev => [newDiag, ...prev]);
    showToast(`Diagnosis generated: ${newDiag.diseaseName} (${newDiag.confidenceScore}% confidence)`, 'success');
    return newDiag;
  };

  const addFeedback = (fbData: Omit<FarmerFeedback, 'id' | 'createdAt' | 'status'>) => {
    const newFb: FarmerFeedback = {
      ...fbData,
      id: `fb-${Date.now()}`,
      createdAt: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
      status: 'Pending Review'
    };
    setFeedbacks(prev => [newFb, ...prev]);
    showToast('Thank you! Your harvest outcome has been recorded for model validation.', 'success');
  };

  const markNotificationAsRead = (id: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const clearAllNotifications = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 4000);
  };

  return (
    <AppContext.Provider
      value={{
        profile,
        updateProfile,
        farms,
        activeFarmId,
        setActiveFarmId,
        activeFarm,
        addFarm,
        updateFarm,
        deleteFarm,
        language,
        setLanguage,
        t,
        weather,
        setWeatherDistrict,
        mandiPrices,
        currentRecommendation,
        isCalculatingRecommendation,
        generateRecommendation,
        diagnosesHistory,
        addDiagnosis,
        feedbacks,
        addFeedback,
        notifications,
        markNotificationAsRead,
        clearAllNotifications,
        toast,
        showToast
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
