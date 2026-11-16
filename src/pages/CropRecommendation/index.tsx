import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { CropRecommendationInput, RecommendedCrop } from '../../types';
import { CropCard } from '../../components/common/CropCard';
import { AIModelComparison } from '../../components/common/AIModelComparison';
import {
  Sparkles,
  MapPin,
  Layers,
  CloudSun,
  DollarSign,
  Cpu,
  Sliders,
  Download,
  Share2,
  CheckCircle2,
  ArrowRight,
  RefreshCw,
  Droplets,
  Scale,
  Calendar,
  Info
} from 'lucide-react';
import { uttarakhandDistricts } from '../../data/demoData';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis
} from 'recharts';

export const CropRecommendationPage: React.FC = () => {
  const { activeFarm, currentRecommendation, isCalculatingRecommendation, generateRecommendation, showToast, language, t } = useApp();
  const isHindi = language === 'hi';

  const [step, setStep] = useState(5); // Start at 5 (results view) for instant rich feedback or let user re-run wizard!
  const [selectedCropIndex, setSelectedCropIndex] = useState(0);

  // Wizard input state prefilled from activeFarm
  const [formData, setFormData] = useState<CropRecommendationInput>({
    farmId: activeFarm.id,
    state: activeFarm.state,
    district: activeFarm.district,
    block: activeFarm.block,
    village: activeFarm.village,
    elevation: activeFarm.elevation || 640,
    soilType: activeFarm.soilType,
    nitrogen: activeFarm.nitrogen,
    phosphorus: activeFarm.phosphorus,
    potassium: activeFarm.potassium,
    soilPh: activeFarm.soilPh,
    organicCarbon: activeFarm.organicCarbon,
    electricalConductivity: activeFarm.electricalConductivity,
    temperature: 24.5,
    humidity: 58,
    rainfall: 120,
    season: activeFarm.currentSeason,
    farmSize: activeFarm.size,
    irrigationAvailability: activeFarm.waterAvailability,
    availableBudget: activeFarm.availableBudget,
    previousCrop: activeFarm.previousCrops[0] || 'Wheat',
    farmingMethod: 'integrated',
  });

  // What-If Simulator state
  const [simRainfall, setSimRainfall] = useState(120);
  const [simTemp, setSimTemp] = useState(formData.temperature);
  const [simIrrigation, setSimIrrigation] = useState(formData.irrigationAvailability);
  const [simBudget, setSimBudget] = useState(formData.availableBudget);

  const [isComparing, setIsComparing] = useState(false);

  // Sync form inputs and trigger unified AI recommendation on activeFarm change or initial mount
  useEffect(() => {
    const updated: CropRecommendationInput = {
      farmId: activeFarm.id,
      state: activeFarm.state,
      district: activeFarm.district,
      block: activeFarm.block,
      village: activeFarm.village,
      elevation: activeFarm.elevation || 640,
      soilType: activeFarm.soilType,
      nitrogen: activeFarm.nitrogen,
      phosphorus: activeFarm.phosphorus,
      potassium: activeFarm.potassium,
      soilPh: activeFarm.soilPh,
      organicCarbon: activeFarm.organicCarbon,
      electricalConductivity: activeFarm.electricalConductivity,
      temperature: 24.5,
      humidity: 58,
      rainfall: 120,
      season: activeFarm.currentSeason,
      farmSize: activeFarm.size,
      irrigationAvailability: activeFarm.waterAvailability,
      availableBudget: activeFarm.availableBudget,
      previousCrop: activeFarm.previousCrops[0] || 'Wheat',
      farmingMethod: 'integrated',
    };
    setFormData(updated);
    setSimRainfall(120);
    setSimTemp(24.5);
    setSimIrrigation(activeFarm.waterAvailability);
    setSimBudget(activeFarm.availableBudget);
    generateRecommendation(updated);
  }, [activeFarm.id]);

  const handleGenerate = () => {
    generateRecommendation(formData);
    setStep(5);
  };

  const handleApplyWhatIf = () => {
    generateRecommendation({
      ...formData,
      rainfall: simRainfall,
      temperature: simTemp,
      irrigationAvailability: simIrrigation,
      availableBudget: simBudget,
    });
    showToast('What-If simulation recalculated scores dynamically!', 'info');
  };

  const selectedCrop = currentRecommendation.recommendedCrops[selectedCropIndex] || currentRecommendation.recommendedCrops[0];

  // Feature influence data for bar chart
  const xaiFeatureChart = selectedCrop.xaiInfluences.map(item => ({
    name: item.factor.split('(')[0].trim(),
    weight: item.impact,
  }));

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-8 pb-16 animate-fade-in">
      {/* Page Title & Context Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-charcoal-100">
        <div>
          <div className="flex items-center gap-2 flex-wrap mb-1.5">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-xs font-bold text-forest-800">
              <Sparkles className="w-3.5 h-3.5 text-saffron-500" />
              <span>{isHindi ? 'हाइब्रिड ट्राई-मॉडल एआई निर्णय इंजन' : 'Hybrid Tri-Model AI Decision Engine'}</span>
            </div>
            {isCalculatingRecommendation && (
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 border border-amber-300 text-xs font-bold text-amber-800 animate-pulse">
                <RefreshCw className="w-3 h-3 animate-spin text-amber-600" />
                <span>{isHindi ? 'एआई पाइपलाइन गणना कर रही है...' : 'Computing AI Pipeline...'}</span>
              </div>
            )}
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
            {isHindi ? 'स्मार्ट फसल उपयुक्तता एवं अनुकूलन' : 'Intelligent Crop Suitability & Optimization'}
          </h1>
          <p className="text-xs text-charcoal-400 mt-1">
            {isHindi ? 'फजी लॉजिक, बायेसियन संभावना एवं डिसीजन ट्री द्वारा संचालित' : 'Synthesized using Fuzzy Logic, Bayesian Probabilistic Likelihood & Decision Trees'}
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setStep(step === 5 ? 1 : 5)}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-white hover:bg-forest-50 text-forest-900 border border-charcoal-200 shadow-sm transition-all flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5 text-forest-700" />
            <span>{step === 5 ? (isHindi ? 'विजार्ड पुनः चलाएं' : 'Re-run Wizard') : (isHindi ? 'परिणाम देखें' : 'View Results')}</span>
          </button>

          <button
            onClick={handlePrint}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-forest-900 hover:bg-forest-800 text-white shadow-sm transition-all flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5 text-saffron-400" />
            <span>{isHindi ? 'रिपोर्ट डाउनलोड करें' : 'Download Report'}</span>
          </button>
        </div>
      </div>

      {/* ================= STEP WIZARD ================= */}
      {step < 5 ? (
        <div className="max-w-3xl mx-auto rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-8 shadow-soft space-y-6">
          {/* Step Indicators */}
          <div className="flex items-center justify-between pb-6 border-b border-charcoal-100">
            {[1, 2, 3, 4].map((s) => (
              <div key={s} className="flex items-center gap-2">
                <div
                  className={`w-8 h-8 rounded-full font-bold text-xs flex items-center justify-center ${
                    step === s
                      ? 'bg-forest-900 text-saffron-400 ring-4 ring-forest-100'
                      : step > s
                      ? 'bg-emerald-600 text-white'
                      : 'bg-charcoal-100 text-charcoal-500'
                  }`}
                >
                  {step > s ? <CheckCircle2 className="w-4 h-4" /> : s}
                </div>
                <span className="text-xs font-bold text-charcoal-700 hidden sm:inline">
                  {s === 1 ? 'Location' : s === 2 ? 'Soil NPK' : s === 3 ? 'Climate' : 'Farm Economics'}
                </span>
              </div>
            ))}
          </div>

          {/* STEP 1: LOCATION */}
          {step === 1 && (
            <div className="space-y-4 text-xs animate-fade-in">
              <h3 className="text-base font-bold text-forest-900">Step 1: Geographic Location & Elevation</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">State</label>
                  <input
                    type="text"
                    value={formData.state}
                    readOnly
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 bg-charcoal-50 text-xs font-semibold text-charcoal-500"
                  />
                </div>
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">District (Uttarakhand)</label>
                  <select
                    value={formData.district}
                    onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  >
                    {uttarakhandDistricts.map(d => (
                      <option key={d.id} value={d.name}>{d.name} ({d.agroZone})</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Elevation (Meters above sea level)</label>
                  <input
                    type="number"
                    value={formData.elevation}
                    onChange={(e) => setFormData({ ...formData, elevation: parseInt(e.target.value) || 500 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                  <span className="text-[10px] text-charcoal-400">Critical for sub-tropical vs alpine crop suitability</span>
                </div>
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Block / Village</label>
                  <input
                    type="text"
                    value={formData.block || ''}
                    onChange={(e) => setFormData({ ...formData, block: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                    placeholder="e.g. Raipur / Maldevta"
                  />
                </div>
              </div>
            </div>
          )}

          {/* STEP 2: SOIL CONDITIONS */}
          {step === 2 && (
            <div className="space-y-4 text-xs animate-fade-in">
              <h3 className="text-base font-bold text-forest-900">Step 2: Soil Nutrients & Chemical Metrics</h3>
              <div>
                <label className="block font-bold text-charcoal-700 mb-1">Soil Texture / Type</label>
                <select
                  value={formData.soilType}
                  onChange={(e) => setFormData({ ...formData, soilType: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                >
                  <option value="Loamy Alluvium">Loamy Alluvial Soil</option>
                  <option value="Mountain Forest Loam">Mountain Forest Brown Loam</option>
                  <option value="Gravelly Silt">Gravelly Terrace Silt</option>
                  <option value="Clayey Loam">Clayey Loam (Heavy water holding)</option>
                  <option value="Sandy Loam">Sandy Loam</option>
                </select>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Nitrogen (N) kg/ha</label>
                  <input
                    type="number"
                    value={formData.nitrogen}
                    onChange={(e) => setFormData({ ...formData, nitrogen: parseInt(e.target.value) || 100 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Phosphorus (P) kg/ha</label>
                  <input
                    type="number"
                    value={formData.phosphorus}
                    onChange={(e) => setFormData({ ...formData, phosphorus: parseInt(e.target.value) || 30 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Potassium (K) kg/ha</label>
                  <input
                    type="number"
                    value={formData.potassium}
                    onChange={(e) => setFormData({ ...formData, potassium: parseInt(e.target.value) || 150 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Soil pH (4.0 - 9.0)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.soilPh}
                    onChange={(e) => setFormData({ ...formData, soilPh: parseFloat(e.target.value) || 6.8 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Organic Carbon (%)</label>
                  <input
                    type="number"
                    step="0.05"
                    value={formData.organicCarbon}
                    onChange={(e) => setFormData({ ...formData, organicCarbon: parseFloat(e.target.value) || 0.8 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: CLIMATE */}
          {step === 3 && (
            <div className="space-y-4 text-xs animate-fade-in">
              <h3 className="text-base font-bold text-forest-900">Step 3: Climatic & Seasonal Conditions</h3>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Average Temp (°C)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={formData.temperature}
                    onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) || 24 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Avg Humidity (%)</label>
                  <input
                    type="number"
                    value={formData.humidity}
                    onChange={(e) => setFormData({ ...formData, humidity: parseInt(e.target.value) || 60 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Seasonal Rainfall (mm)</label>
                  <input
                    type="number"
                    value={formData.rainfall}
                    onChange={(e) => setFormData({ ...formData, rainfall: parseInt(e.target.value) || 120 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                  <span className="text-[10px] text-charcoal-400">Cropping season (20 - 300 mm)</span>
                </div>
              </div>

              <div>
                <label className="block font-bold text-charcoal-700 mb-1">Target Farming Season</label>
                <select
                  value={formData.season}
                  onChange={(e) => setFormData({ ...formData, season: e.target.value as any })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                >
                  <option value="Kharif">Kharif (Monsoon / Paddy, Millets, Soybean)</option>
                  <option value="Rabi">Rabi (Winter / Wheat, Mustard, Barley, Peas)</option>
                  <option value="Zaid">Zaid (Summer / Vegetables, Moong, Fodder)</option>
                </select>
              </div>
            </div>
          )}

          {/* STEP 4: FARM ECONOMICS */}
          {step === 4 && (
            <div className="space-y-4 text-xs animate-fade-in">
              <h3 className="text-base font-bold text-forest-900">Step 4: Farm Infrastructure & Economics</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Farm Size (Acres)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={formData.farmSize}
                    onChange={(e) => setFormData({ ...formData, farmSize: parseFloat(e.target.value) || 2 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Water Availability</label>
                  <select
                    value={formData.irrigationAvailability}
                    onChange={(e) => setFormData({ ...formData, irrigationAvailability: e.target.value as any })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  >
                    <option value="abundant">Abundant (Canal or Deep Borewell)</option>
                    <option value="moderate">Moderate (Seasonal Water / Pond)</option>
                    <option value="scarce">Scarce (Rainfed / Hill Gul)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Available Input Budget (₹)</label>
                  <input
                    type="number"
                    step="5000"
                    value={formData.availableBudget}
                    onChange={(e) => setFormData({ ...formData, availableBudget: parseInt(e.target.value) || 50000 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Previous Crop Cultivated</label>
                  <input
                    type="text"
                    value={formData.previousCrop}
                    onChange={(e) => setFormData({ ...formData, previousCrop: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Wizard Navigation Controls */}
          <div className="pt-6 border-t border-charcoal-100 flex items-center justify-between">
            {step > 1 ? (
              <button
                type="button"
                onClick={() => setStep(step - 1)}
                className="px-5 py-2.5 rounded-xl text-xs font-bold text-charcoal-600 hover:bg-charcoal-100 transition-colors"
              >
                Back
              </button>
            ) : <div />}

            {step < 4 ? (
              <button
                type="button"
                onClick={() => setStep(step + 1)}
                className="px-6 py-2.5 rounded-xl text-xs font-bold bg-forest-900 text-white hover:bg-forest-800 transition-all flex items-center gap-1.5"
              >
                <span>Continue</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="button"
                disabled={isCalculatingRecommendation}
                onClick={handleGenerate}
                className="px-7 py-3 rounded-xl text-xs font-black bg-saffron-500 hover:bg-saffron-400 disabled:opacity-60 text-charcoal-900 shadow-lg shadow-saffron-500/20 transition-all flex items-center gap-2"
              >
                {isCalculatingRecommendation ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-charcoal-900" />
                    <span>Processing Hybrid Models...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Generate Hybrid Ensemble Recommendation</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      ) : (
        /* ================= STEP 5: RESULTS & EXPLAINABLE AI VIEW ================= */
        <div className="space-y-8 animate-fade-in">
          {/* Top 3 Recommended Crops */}
          <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
              <div>
                <h2 className="text-xl font-black text-forest-900 tracking-tight">
                  {isHindi ? 'शीर्ष 3 एआई अनुशंसित फसलें' : 'Top 3 AI Recommended Crops'}
                </h2>
                <p className="text-xs text-charcoal-400">
                  {isHindi 
                    ? `${formData.district} जिले (${formData.elevation}मी) के लिए ट्राई-मॉडल एन्सेम्बल उपयुक्तता स्कोर के आधार पर`
                    : `Ranked by tri-model ensemble compatibility score with ${formData.district} district (${formData.elevation}m ASL)`}
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsComparing(!isComparing)}
                  className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-white border border-charcoal-200 hover:border-forest-300 text-forest-900 transition-all flex items-center gap-1.5"
                >
                  <Scale className="w-3.5 h-3.5 text-forest-700" />
                  <span>
                    {isComparing 
                      ? (isHindi ? 'तुलना बंद करें' : 'Close Comparison') 
                      : (isHindi ? 'शीर्ष 3 फसलों की तुलना करें' : 'Compare Top 3 Crops')}
                  </span>
                </button>
              </div>
            </div>

            {/* Crop Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {currentRecommendation.recommendedCrops.map((crop, idx) => (
                <CropCard
                  key={crop.id}
                  crop={crop}
                  rank={idx + 1}
                  isSelected={selectedCropIndex === idx}
                  onSelect={() => setSelectedCropIndex(idx)}
                  onAddToPlan={() => showToast(`Added ${crop.name} to farm crop rotation calendar!`, 'success')}
                />
              ))}
            </div>
          </div>

          {/* Side-by-side Crop Comparison Matrix Drawer */}
          {isComparing && (
            <div className="rounded-3xl bg-white border border-charcoal-200 p-6 shadow-soft animate-fade-in overflow-x-auto">
              <h3 className="text-base font-extrabold text-forest-900 mb-4">
                Top 3 Crops Direct Comparison Matrix
              </h3>
              <table className="w-full text-xs text-left border-collapse min-w-[500px]">
                <thead>
                  <tr className="border-b border-charcoal-200 text-charcoal-500 font-bold uppercase text-[10px]">
                    <th className="py-2.5 px-3">Metric</th>
                    {currentRecommendation.recommendedCrops.map((c, i) => (
                      <th key={i} className="py-2.5 px-3 text-forest-900 font-bold">
                        #{i + 1} {c.name.split('(')[0]}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-charcoal-100">
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-charcoal-600">Suitability Score</td>
                    {currentRecommendation.recommendedCrops.map((c, i) => (
                      <td key={i} className="py-2.5 px-3 font-bold text-forest-800">{c.suitabilityScore}%</td>
                    ))}
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-charcoal-600">Water Requirement</td>
                    {currentRecommendation.recommendedCrops.map((c, i) => (
                      <td key={i} className="py-2.5 px-3">{c.waterRequirement}</td>
                    ))}
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-charcoal-600">Growing Duration</td>
                    {currentRecommendation.recommendedCrops.map((c, i) => (
                      <td key={i} className="py-2.5 px-3">{c.growingDurationDays} Days</td>
                    ))}
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-charcoal-600">Expected Yield</td>
                    {currentRecommendation.recommendedCrops.map((c, i) => (
                      <td key={i} className="py-2.5 px-3 font-semibold">{c.expectedYieldQuintalsPerAcre} q/acre</td>
                    ))}
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-charcoal-600">Estimated Net Profit</td>
                    {currentRecommendation.recommendedCrops.map((c, i) => (
                      <td key={i} className="py-2.5 px-3 font-bold text-emerald-700">₹{c.estimatedNetProfitPerAcre.toLocaleString()}/acre</td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {/* ================= HYBRID AI ENSEMBLE BREAKDOWN ================= */}
          <AIModelComparison
            models={currentRecommendation.ensembleBreakdown}
            ensembleConfidence={currentRecommendation.ensembleConfidence}
            modelAgreement={currentRecommendation.modelAgreement}
          />

          {/* ================= EXPLAINABLE AI (XAI) PANEL ================= */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Feature Contribution Radar / Bar (7 Cols) */}
            <div className="lg:col-span-7 rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft">
              <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
                <div>
                  <h3 className="text-base font-extrabold text-forest-900">
                    Why is {selectedCrop.name.split('(')[0]} Recommended?
                  </h3>
                  <p className="text-xs text-charcoal-400">
                    Agronomic compatibility and feature suitability for Rank #{selectedCropIndex + 1}
                  </p>
                </div>
                <span className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-forest-50 text-forest-800">
                  Agronomic Compatibility
                </span>
              </div>

              <div className="mt-5 h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={xaiFeatureChart} layout="vertical" margin={{ left: 10, right: 20 }}>
                    <XAxis type="number" unit="%" domain={[0, 40]} />
                    <YAxis dataKey="name" type="category" width={110} tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#174B35',
                        color: '#fff',
                        borderRadius: '8px',
                        fontSize: '11px',
                      }}
                    />
                    <Bar dataKey="weight" fill="#174B35" radius={[0, 8, 8, 0]}>
                      {xaiFeatureChart.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={index === 0 ? '#E8AD45' : '#174B35'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="mt-4 pt-3 border-t border-charcoal-100 space-y-2 text-xs">
                {selectedCrop.xaiInfluences.map((inf, i) => (
                  <div key={i} className="flex items-start gap-2 text-charcoal-600">
                    <span className="w-1.5 h-1.5 rounded-full bg-forest-700 mt-1.5 shrink-0" />
                    <p>
                      <strong className="text-forest-900">{inf.factor}:</strong> {inf.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* ================= WHAT-IF SIMULATOR (5 Cols) ================= */}
            <div className="lg:col-span-5 rounded-3xl bg-forest-50/70 border border-forest-200/80 p-6 shadow-soft flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 pb-3 border-b border-forest-200">
                  <span className="p-2 rounded-xl bg-forest-900 text-saffron-400">
                    <Sliders className="w-4 h-4" />
                  </span>
                  <div>
                    <h3 className="text-base font-extrabold text-forest-900">
                      {isHindi ? 'इंटरैक्टिव यदि-तो परिदृश्य सिम्युलेटर' : 'Interactive What-If Simulator'}
                    </h3>
                    <p className="text-[11px] text-charcoal-500">
                      {isHindi ? 'मौसम व बजट में बदलाव का प्रभाव तुरंत देखें' : 'Simulate climate shifts & see dynamic recalculation'}
                    </p>
                  </div>
                </div>

                <div className="mt-5 space-y-4 text-xs">
                  {/* Rainfall Slider */}
                  <div>
                    <div className="flex justify-between font-bold text-charcoal-700 mb-1">
                      <span>{isHindi ? 'मौसमी वर्षा:' : 'Seasonal Rainfall:'}</span>
                      <span className="text-forest-900 font-black">{simRainfall} mm</span>
                    </div>
                    <input
                      type="range"
                      min="30"
                      max="300"
                      step="10"
                      value={simRainfall}
                      onChange={(e) => setSimRainfall(parseInt(e.target.value))}
                      className="w-full accent-forest-700 cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] text-charcoal-400">
                      <span>{isHindi ? 'शुष्क मौसम (30mm)' : 'Dry Season (30mm)'}</span>
                      <span>{isHindi ? 'भारी मानसून (300mm)' : 'Heavy Monsoon (300mm)'}</span>
                    </div>
                  </div>

                  {/* Temperature Slider */}
                  <div>
                    <div className="flex justify-between font-bold text-charcoal-700 mb-1">
                      <span>{isHindi ? 'घाटी का तापमान:' : 'Valley Temperature:'}</span>
                      <span className="text-forest-900 font-black">{simTemp}°C</span>
                    </div>
                    <input
                      type="range"
                      min="12"
                      max="38"
                      step="0.5"
                      value={simTemp}
                      onChange={(e) => setSimTemp(parseFloat(e.target.value))}
                      className="w-full accent-forest-700 cursor-pointer"
                    />
                  </div>

                  {/* Water Availability Toggle */}
                  <div>
                    <label className="block font-bold text-charcoal-700 mb-1">
                      {isHindi ? 'सिंचाई जल की उपलब्धता' : 'Simulated Water Availability'}
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {(['abundant', 'moderate', 'scarce'] as const).map((w) => (
                        <button
                          key={w}
                          type="button"
                          onClick={() => setSimIrrigation(w)}
                          className={`py-1.5 px-2 rounded-xl font-bold capitalize text-xs transition-all ${
                            simIrrigation === w
                              ? 'bg-forest-900 text-white'
                              : 'bg-white border border-charcoal-200 text-charcoal-700'
                          }`}
                        >
                          {isHindi ? (w === 'abundant' ? 'प्रचुर' : w === 'moderate' ? 'मध्यम' : 'सीमित') : w}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Budget Slider */}
                  <div>
                    <div className="flex justify-between font-bold text-charcoal-700 mb-1">
                      <span>{isHindi ? 'अनुमानित बजट:' : 'Simulated Budget:'}</span>
                      <span className="text-forest-900 font-black">₹{simBudget.toLocaleString()}</span>
                    </div>
                    <input
                      type="range"
                      min="15000"
                      max="150000"
                      step="5000"
                      value={simBudget}
                      onChange={(e) => setSimBudget(parseInt(e.target.value))}
                      className="w-full accent-forest-700 cursor-pointer"
                    />
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-forest-200">
                <button
                  type="button"
                  disabled={isCalculatingRecommendation}
                  onClick={handleApplyWhatIf}
                  className="w-full py-2.5 rounded-xl text-xs font-black bg-saffron-500 hover:bg-saffron-400 disabled:opacity-60 text-charcoal-900 shadow-md transition-all flex items-center justify-center gap-1.5"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isCalculatingRecommendation ? 'animate-spin' : ''}`} />
                  <span>
                    {isCalculatingRecommendation 
                      ? (isHindi ? 'एआई पाइपलाइन गणना कर रही है...' : 'Recalculating Pipeline...') 
                      : (isHindi ? 'गतिशील उपयुक्तता की पुनः गणना करें' : 'Recalculate Dynamic Suitability')}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
