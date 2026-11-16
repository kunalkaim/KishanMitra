import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import {
  Settings,
  Globe,
  Bell,
  Key,
  Shield,
  Trash2,
  Save,
  CheckCircle2,
  ExternalLink,
  Smartphone,
  RefreshCw
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { profile, updateProfile, language, setLanguage, showToast } = useApp();

  const [activeTab, setActiveTab] = useState<'general' | 'notifications' | 'api' | 'data'>('general');

  // Notification toggles
  const [notifySms, setNotifySms] = useState(true);
  const [notifyWhatsapp, setNotifyWhatsapp] = useState(true);
  const [notifyWeatherAlerts, setNotifyWeatherAlerts] = useState(true);
  const [notifyMandiSpikes, setNotifyMandiSpikes] = useState(true);

  // API configuration inputs
  const [weatherApiKey, setWeatherApiKey] = useState('demo_imd_openweathermap_key_***');
  const [enamToken, setEnamToken] = useState('demo_enam_apmc_token_***');
  const [cvEndpoint, setCvEndpoint] = useState('https://cv-inference.kisanmitra.gov.in/v1/detect');

  const handleSaveApiSettings = (e: React.FormEvent) => {
    e.preventDefault();
    showToast('API Configuration saved successfully!', 'success');
  };

  const handleResetStorage = () => {
    if (confirm('Are you sure you want to reset demo data back to default initial state?')) {
      localStorage.clear();
      window.location.reload();
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16 animate-fade-in">
      {/* Header */}
      <div className="pb-4 border-b border-charcoal-100">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-xs font-bold text-forest-800 mb-1.5">
          <Settings className="w-3.5 h-3.5 text-forest-700" />
          <span>System & Account Configuration</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
          Settings & Preferences
        </h1>
        <p className="text-xs text-charcoal-400 mt-1">
          Manage bilingual preferences, real-time alert channels, and backend API integration endpoints
        </p>
      </div>

      {/* Tabs */}
      <div className="flex items-center p-1 bg-charcoal-100 rounded-2xl text-xs font-bold">
        <button
          onClick={() => setActiveTab('general')}
          className={`flex-1 py-2 rounded-xl transition-all ${
            activeTab === 'general' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
          }`}
        >
          General & Language
        </button>
        <button
          onClick={() => setActiveTab('notifications')}
          className={`flex-1 py-2 rounded-xl transition-all ${
            activeTab === 'notifications' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
          }`}
        >
          Alert Channels
        </button>
        <button
          onClick={() => setActiveTab('api')}
          className={`flex-1 py-2 rounded-xl transition-all ${
            activeTab === 'api' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
          }`}
        >
          API Integrations
        </button>
        <button
          onClick={() => setActiveTab('data')}
          className={`flex-1 py-2 rounded-xl transition-all ${
            activeTab === 'data' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
          }`}
        >
          Data & Privacy
        </button>
      </div>

      {/* ================= TAB 1: GENERAL & LANGUAGE ================= */}
      {activeTab === 'general' && (
        <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-8 shadow-soft space-y-6 text-xs animate-fade-in">
          <div>
            <h3 className="text-base font-extrabold text-forest-900">Language Preferences</h3>
            <p className="text-charcoal-400">Select preferred display language for all menus and advisory cards</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button
              onClick={() => {
                setLanguage('en');
                showToast('Switched to English interface.', 'info');
              }}
              className={`p-4 rounded-2xl border text-left transition-all ${
                language === 'en'
                  ? 'bg-forest-50 border-forest-600 ring-2 ring-forest-500/20 text-forest-900'
                  : 'bg-white border-charcoal-200 text-charcoal-700 hover:bg-charcoal-50'
              }`}
            >
              <div className="flex items-center justify-between font-extrabold text-sm">
                <span>English</span>
                {language === 'en' && <CheckCircle2 className="w-4 h-4 text-forest-700" />}
              </div>
              <p className="text-xs text-charcoal-500 mt-1">Default international agricultural English</p>
            </button>

            <button
              onClick={() => {
                setLanguage('hi');
                showToast('हिन्दी भाषा सक्रिय की गई।', 'info');
              }}
              className={`p-4 rounded-2xl border text-left transition-all ${
                language === 'hi'
                  ? 'bg-forest-50 border-forest-600 ring-2 ring-forest-500/20 text-forest-900'
                  : 'bg-white border-charcoal-200 text-charcoal-700 hover:bg-charcoal-50'
              }`}
            >
              <div className="flex items-center justify-between font-extrabold text-sm">
                <span>हिन्दी (Hindi)</span>
                {language === 'hi' && <CheckCircle2 className="w-4 h-4 text-forest-700" />}
              </div>
              <p className="text-xs text-charcoal-500 mt-1">भारतीय किसानों के लिए स्थानीय भाषा इंटरफेस</p>
            </button>
          </div>
        </div>
      )}

      {/* ================= TAB 2: ALERT CHANNELS ================= */}
      {activeTab === 'notifications' && (
        <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-8 shadow-soft space-y-6 text-xs animate-fade-in">
          <div>
            <h3 className="text-base font-extrabold text-forest-900">Farmer Notification Channels</h3>
            <p className="text-charcoal-400">Configure how critical weather warnings and mandi spikes reach you</p>
          </div>

          <div className="space-y-4 divide-y divide-charcoal-100">
            <div className="pt-3 flex items-center justify-between">
              <div>
                <p className="font-bold text-forest-900 text-sm">WhatsApp Business Broadcasts</p>
                <p className="text-charcoal-500 text-[11px]">Receive daily morning mandi price bulletins and irrigation reminders on WhatsApp</p>
              </div>
              <input
                type="checkbox"
                checked={notifyWhatsapp}
                onChange={(e) => setNotifyWhatsapp(e.target.checked)}
                className="w-4 h-4 accent-forest-700 rounded cursor-pointer"
              />
            </div>

            <div className="pt-3 flex items-center justify-between">
              <div>
                <p className="font-bold text-forest-900 text-sm">Urgent SMS Alerts (Kisan Portal)</p>
                <p className="text-charcoal-500 text-[11px]">Direct SMS dispatch for hail, sudden cloudburst, or frost warnings</p>
              </div>
              <input
                type="checkbox"
                checked={notifySms}
                onChange={(e) => setNotifySms(e.target.checked)}
                className="w-4 h-4 accent-forest-700 rounded cursor-pointer"
              />
            </div>

            <div className="pt-3 flex items-center justify-between">
              <div>
                <p className="font-bold text-forest-900 text-sm">High Price Spike Mandi Alerts</p>
                <p className="text-charcoal-500 text-[11px]">Trigger notification when modal rates exceed 3-month regional moving average by +5%</p>
              </div>
              <input
                type="checkbox"
                checked={notifyMandiSpikes}
                onChange={(e) => setNotifyMandiSpikes(e.target.checked)}
                className="w-4 h-4 accent-forest-700 rounded cursor-pointer"
              />
            </div>
          </div>
        </div>
      )}

      {/* ================= TAB 3: API INTEGRATIONS ================= */}
      {activeTab === 'api' && (
        <form onSubmit={handleSaveApiSettings} className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-8 shadow-soft space-y-5 text-xs animate-fade-in">
          <div>
            <h3 className="text-base font-extrabold text-forest-900">API Gateway & Inference Endpoints</h3>
            <p className="text-charcoal-400">Configure connection strings for future real-world backend microservices</p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">OpenWeatherMap / IMD Weather API Key</label>
              <input
                type="text"
                value={weatherApiKey}
                onChange={(e) => setWeatherApiKey(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 font-mono text-xs focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-bold text-charcoal-700 mb-1">e-NAM Mandi Agmarknet Service Key</label>
              <input
                type="text"
                value={enamToken}
                onChange={(e) => setEnamToken(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 font-mono text-xs focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-bold text-charcoal-700 mb-1">Deep Learning Computer Vision Endpoint</label>
              <input
                type="text"
                value={cvEndpoint}
                onChange={(e) => setCvEndpoint(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 font-mono text-xs focus:outline-none"
              />
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl font-bold text-xs bg-forest-900 hover:bg-forest-800 text-white shadow-md active:scale-95"
            >
              Save API Endpoints
            </button>
          </div>
        </form>
      )}

      {/* ================= TAB 4: DATA & PRIVACY ================= */}
      {activeTab === 'data' && (
        <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-8 shadow-soft space-y-6 text-xs animate-fade-in">
          <div>
            <h3 className="text-base font-extrabold text-forest-900">Data Management & Privacy</h3>
            <p className="text-charcoal-400">Local browser persistence controls & security protocols</p>
          </div>

          <div className="p-4 rounded-2xl bg-forest-50/70 border border-forest-100 space-y-2">
            <h4 className="font-bold text-forest-900">Client-Side Persistence:</h4>
            <p className="text-charcoal-600 leading-relaxed">
              Your registered farms, soil health metrics, pest & disease advisory cases, and outcome feedback are synchronized with the KisanMitra backend and cached in browser storage.
            </p>
          </div>

          <div className="pt-4 border-t border-charcoal-100 flex items-center justify-between">
            <div>
              <p className="font-bold text-rose-600">Reset Demonstration Storage</p>
              <p className="text-charcoal-400 text-[11px]">Clear all added custom farms and revert to initial seed records</p>
            </div>

            <button
              onClick={handleResetStorage}
              className="px-4 py-2 rounded-xl font-bold text-xs bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 transition-colors flex items-center gap-1.5"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Reset Demo State</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
