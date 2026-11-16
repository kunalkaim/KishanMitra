import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { AppShell } from './components/layout/AppShell';

// Public Pages
import { HomePage } from './pages/Home';

// Authenticated Application Modules
import { DashboardPage } from './pages/Dashboard';
import { FarmsPage } from './pages/Farms';
import { FarmerProfilePage } from './pages/Farms/FarmerProfilePage';
import { RegionIntelligencePage } from './pages/RegionIntelligence';
import { CropRecommendationPage } from './pages/CropRecommendation';
import { WeatherPage } from './pages/Weather';
import { MarketIntelligencePage } from './pages/MarketIntelligence';
import { SmartAdvisorPage } from './pages/SmartAdvisor';
import { PestDiseaseAdvisoryPage } from './pages/PestDiseaseAdvisory';
import { AIAssistantPage } from './pages/AIAssistant';
import { CropRotationPage } from './pages/CropRotation';
import { SatelliteMonitoringPage } from './pages/SatelliteMonitoring';
import { FeedbackPage } from './pages/Feedback';
import { AnalyticsPage } from './pages/Analytics';
import { SettingsPage } from './pages/Settings';
import { HelpPage } from './pages/Help';

export const App: React.FC = () => {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Website */}
          <Route path="/" element={<HomePage />} />

          {/* Authenticated Farmer Portal Shell */}
          <Route element={<AppShell />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/farms" element={<FarmsPage />} />
            <Route path="/farmer-profile" element={<FarmerProfilePage />} />
            <Route path="/region-intelligence" element={<RegionIntelligencePage />} />
            <Route path="/crop-recommendation" element={<CropRecommendationPage />} />
            <Route path="/weather" element={<WeatherPage />} />
            <Route path="/market-intelligence" element={<MarketIntelligencePage />} />
            <Route path="/smart-advisor" element={<SmartAdvisorPage />} />
            <Route path="/advisory" element={<PestDiseaseAdvisoryPage />} />
            <Route path="/disease-detection" element={<Navigate to="/advisory" replace />} />
            <Route path="/ai-assistant" element={<AIAssistantPage />} />
            <Route path="/crop-rotation" element={<CropRotationPage />} />
            <Route path="/satellite-monitoring" element={<SatelliteMonitoringPage />} />
            <Route path="/feedback" element={<FeedbackPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/help" element={<HelpPage />} />
          </Route>

          {/* Fallback Redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
};

export default App;
