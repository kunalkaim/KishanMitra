import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import {
  Repeat,
  Sprout,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Layers,
  Calendar,
  ShieldCheck,
  Award
} from 'lucide-react';

export const CropRotationPage: React.FC = () => {
  const { activeFarm, showToast } = useApp();

  const [previousCrop, setPreviousCrop] = useState(activeFarm.previousCrops[0] || 'Basmati Rice');
  const [rotationHorizon, setRotationHorizon] = useState<'1year' | '2year' | '3year'>('1year');
  const [selectedGoal, setSelectedGoal] = useState<'soil_health' | 'profit' | 'water_saving'>('soil_health');

  // Pre-configured agronomic rotation plans
  const rotationSequences = [
    {
      season: 'Kharif (Monsoon)',
      crop: 'Basmati Rice (Pusa 1509)',
      family: 'Poaceae (Gramineae)',
      waterReq: 'High',
      nutrientImpact: 'Consumes Nitrogen & Potassium heavily',
      nitrogenBalance: -25,
      weedSuppression: 'High (puddled conditions)',
      status: 'Current Season'
    },
    {
      season: 'Rabi (Winter)',
      crop: 'Yellow Mustard (Sarson)',
      family: 'Brassicaceae (Cruciferae)',
      waterReq: 'Low to Medium',
      nutrientImpact: 'Deep taproot breaks hard pan; bio-fumigates soil against nematodes',
      nitrogenBalance: -10,
      weedSuppression: 'Very High (dense canopy)',
      status: 'Recommended Next'
    },
    {
      season: 'Zaid (Summer)',
      crop: 'Green Gram / Moong (Summer Legume)',
      family: 'Fabaceae (Leguminosae)',
      waterReq: 'Low',
      nutrientImpact: 'Fixes atmospheric nitrogen into root nodules; enriches soil',
      nitrogenBalance: +38,
      weedSuppression: 'Moderate',
      status: 'Soil Replenisher'
    }
  ];

  const handleSavePlan = () => {
    showToast('Multi-season crop rotation plan saved to farm profile!', 'success');
  };

  return (
    <div className="space-y-6 pb-16 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-charcoal-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-xs font-bold text-forest-800 mb-1.5">
            <Repeat className="w-3.5 h-3.5 text-saffron-500" />
            <span>Ecological Agronomy Engine</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
            Intelligent Crop Rotation Planner
          </h1>
          <p className="text-xs text-charcoal-400 mt-1">
            Design multi-season crop sequences that replenish soil nitrogen, disrupt pest cycles, and prevent monoculture soil fatigue
          </p>
        </div>

        <button
          onClick={handleSavePlan}
          className="px-5 py-2.5 rounded-2xl font-bold text-xs bg-forest-900 hover:bg-forest-800 text-white shadow-md transition-all active:scale-95 flex items-center gap-2"
        >
          <Sparkles className="w-3.5 h-3.5 text-saffron-400" />
          <span>Save Rotation Sequence</span>
        </button>
      </div>

      {/* Rotation Parameters Bar */}
      <div className="p-5 rounded-3xl bg-white border border-charcoal-100 shadow-soft grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
        <div>
          <label className="block font-bold text-charcoal-700 mb-1">Active Farm & Field</label>
          <input
            type="text"
            readOnly
            value={`${activeFarm.name} (${activeFarm.size} Acres)`}
            className="w-full px-3 py-2 rounded-xl border border-charcoal-200 bg-charcoal-50 font-semibold text-charcoal-600"
          />
        </div>

        <div>
          <label className="block font-bold text-charcoal-700 mb-1">Previous Crop in Field</label>
          <select
            value={previousCrop}
            onChange={(e) => setPreviousCrop(e.target.value)}
            className="w-full px-3 py-2 rounded-xl border border-charcoal-200 font-semibold text-charcoal-800 focus:outline-none"
          >
            <option value="Basmati Rice">Basmati Rice / Paddy (Poaceae)</option>
            <option value="Wheat">Wheat (Poaceae)</option>
            <option value="Finger Millet">Finger Millet / Mandua (Poaceae)</option>
            <option value="Tomato">Off-season Tomato (Solanaceae)</option>
            <option value="Potato">Potato (Solanaceae)</option>
          </select>
        </div>

        <div>
          <label className="block font-bold text-charcoal-700 mb-1">Primary Agronomic Goal</label>
          <select
            value={selectedGoal}
            onChange={(e) => setSelectedGoal(e.target.value as any)}
            className="w-full px-3 py-2 rounded-xl border border-charcoal-200 font-semibold text-charcoal-800 focus:outline-none"
          >
            <option value="soil_health">Restore Soil Nitrogen & Organic Carbon</option>
            <option value="profit">Maximize Commercial Revenue</option>
            <option value="water_saving">Conserve Water (Drought Resilience)</option>
          </select>
        </div>
      </div>

      {/* Planning Horizon Selector */}
      <div className="flex items-center gap-3">
        <span className="text-xs font-bold text-charcoal-500">Planning Horizon:</span>
        <div className="flex items-center p-1 bg-charcoal-100 rounded-xl text-xs font-bold">
          <button
            onClick={() => setRotationHorizon('1year')}
            className={`px-3 py-1.5 rounded-lg ${rotationHorizon === '1year' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600'}`}
          >
            1-Year (3 Seasons)
          </button>
          <button
            onClick={() => setRotationHorizon('2year')}
            className={`px-3 py-1.5 rounded-lg ${rotationHorizon === '2year' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600'}`}
          >
            2-Year Cycle
          </button>
          <button
            onClick={() => setRotationHorizon('3year')}
            className={`px-3 py-1.5 rounded-lg ${rotationHorizon === '3year' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600'}`}
          >
            3-Year Sustainable Plan
          </button>
        </div>
      </div>

      {/* Visual Crop Sequence Timeline */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {rotationSequences.map((seq, idx) => (
          <div
            key={idx}
            className="rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft space-y-4 text-xs relative overflow-hidden"
          >
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-0.5 rounded-full font-black uppercase text-[10px] bg-forest-100 text-forest-900">
                Phase 0{idx + 1} • {seq.season}
              </span>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                  seq.status === 'Current Season'
                    ? 'bg-forest-900 text-white'
                    : seq.status === 'Recommended Next'
                    ? 'bg-saffron-100 text-saffron-900'
                    : 'bg-emerald-100 text-emerald-800'
                }`}
              >
                {seq.status}
              </span>
            </div>

            <div>
              <h3 className="text-base font-extrabold text-forest-900">{seq.crop}</h3>
              <p className="text-charcoal-400 text-[11px] font-mono mt-0.5">Family: {seq.family}</p>
            </div>

            <p className="text-charcoal-600 leading-relaxed pt-2 border-t border-charcoal-100">
              {seq.nutrientImpact}
            </p>

            <div className="space-y-1.5 pt-2 border-t border-charcoal-100">
              <div className="flex justify-between">
                <span className="text-charcoal-500">Water Consumption:</span>
                <strong className="text-forest-900">{seq.waterReq}</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-charcoal-500">Nitrogen Balance:</span>
                <strong className={seq.nitrogenBalance >= 0 ? 'text-emerald-700 font-bold' : 'text-rose-600 font-bold'}>
                  {seq.nitrogenBalance >= 0 ? '+' : ''}{seq.nitrogenBalance} kg/ha
                </strong>
              </div>
              <div className="flex justify-between">
                <span className="text-charcoal-500">Weed Control:</span>
                <strong className="text-forest-900">{seq.weedSuppression}</strong>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Agronomic Ecological Balance Card */}
      <div className="rounded-3xl bg-forest-950 text-white p-6 sm:p-8 shadow-soft-lg space-y-4">
        <h4 className="text-base font-extrabold text-saffron-400 flex items-center gap-2">
          <Award className="w-5 h-5 text-saffron-400" />
          <span>Annual Rotation Ecological Balance Sheet</span>
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-2xl bg-forest-900/80 border border-forest-800 space-y-1">
            <span className="text-forest-400 uppercase text-[10px] font-bold">Net Nitrogen Recharge</span>
            <p className="text-2xl font-black text-emerald-400">+3 kg / ha Net</p>
            <p className="text-forest-300 text-[11px]">Leguminous Moong crop neutralizes cereal depletion</p>
          </div>

          <div className="p-4 rounded-2xl bg-forest-900/80 border border-forest-800 space-y-1">
            <span className="text-forest-400 uppercase text-[10px] font-bold">Soil Nematode Reduction</span>
            <p className="text-2xl font-black text-white">82% Suppression</p>
            <p className="text-forest-300 text-[11px]">Mustard glucosinolates act as natural bio-fumigant</p>
          </div>

          <div className="p-4 rounded-2xl bg-forest-900/80 border border-forest-800 space-y-1">
            <span className="text-forest-400 uppercase text-[10px] font-bold">Cumulative Net Revenue</span>
            <p className="text-2xl font-black text-saffron-400">₹1,18,500 / acre</p>
            <p className="text-forest-300 text-[11px]">Combined 3-season annualized gross margin</p>
          </div>
        </div>
      </div>
    </div>
  );
};
