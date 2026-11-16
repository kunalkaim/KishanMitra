import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import {
  Compass,
  Sprout,
  Droplets,
  Calendar,
  AlertTriangle,
  Layers,
  CheckCircle2,
  ChevronRight,
  ShieldAlert,
  Sparkles,
  Info
} from 'lucide-react';

export const SmartAdvisorPage: React.FC = () => {
  const { activeFarm } = useApp();
  const [activeSection, setActiveSection] = useState<'soil' | 'irrigation' | 'fertilizer' | 'pest' | 'calendar'>('soil');
  const [calendarView, setCalendarView] = useState<'monthly' | 'weekly'>('monthly');

  return (
    <div className="space-y-6 pb-16 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-charcoal-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-xs font-bold text-forest-800 mb-1.5">
            <Compass className="w-3.5 h-3.5 text-saffron-500" />
            <span>Agronomic Advisory Center</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
            Smart Farming Advisor
          </h1>
          <p className="text-xs text-charcoal-400 mt-1">
            Science-backed agronomic guidance for soil health, precision irrigation, bio-fertilizers, and seasonal calendars
          </p>
        </div>

        {/* Section Navigation Tabs */}
        <div className="flex flex-wrap items-center p-1 bg-charcoal-100 rounded-2xl text-xs font-bold gap-1">
          <button
            onClick={() => setActiveSection('soil')}
            className={`px-3 py-1.5 rounded-xl transition-all ${
              activeSection === 'soil' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            Soil Health
          </button>
          <button
            onClick={() => setActiveSection('irrigation')}
            className={`px-3 py-1.5 rounded-xl transition-all ${
              activeSection === 'irrigation' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            Irrigation
          </button>
          <button
            onClick={() => setActiveSection('fertilizer')}
            className={`px-3 py-1.5 rounded-xl transition-all ${
              activeSection === 'fertilizer' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            Fertilizer Planning
          </button>
          <button
            onClick={() => setActiveSection('pest')}
            className={`px-3 py-1.5 rounded-xl transition-all ${
              activeSection === 'pest' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            Pest Risk
          </button>
          <button
            onClick={() => setActiveSection('calendar')}
            className={`px-3 py-1.5 rounded-xl transition-all ${
              activeSection === 'calendar' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            Crop Calendar
          </button>
        </div>
      </div>

      {/* ================= 1. SOIL HEALTH ADVISOR ================= */}
      {activeSection === 'soil' && (
        <div className="space-y-6 animate-fade-in">
          <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-7 shadow-soft space-y-6">
            <div className="flex items-start justify-between pb-4 border-b border-charcoal-100">
              <div>
                <h3 className="text-base font-extrabold text-forest-900">
                  Soil Nutrient Status & Diagnostic Assessment
                </h3>
                <p className="text-xs text-charcoal-400">
                  Evaluation for {activeFarm.name} ({activeFarm.soilType} soil)
                </p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                Overall Grade: A- (Healthy)
              </span>
            </div>

            {/* Nutrients Gauge Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-center text-xs">
              <div className="p-4 rounded-2xl bg-forest-50/70 border border-forest-100">
                <p className="text-charcoal-400 font-bold uppercase text-[10px]">Soil Reaction (pH)</p>
                <p className="text-2xl font-black text-forest-900 mt-1">{activeFarm.soilPh}</p>
                <p className="text-emerald-700 font-bold mt-0.5">Neutral • Ideal</p>
                <p className="text-[11px] text-charcoal-500 mt-2">
                  Nutrients readily soluble and available to plant roots without aluminium toxicity.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-saffron-50/70 border border-saffron-100">
                <p className="text-charcoal-400 font-bold uppercase text-[10px]">Nitrogen (N)</p>
                <p className="text-2xl font-black text-charcoal-900 mt-1">{activeFarm.nitrogen} kg/ha</p>
                <p className="text-saffron-800 font-bold mt-0.5">Medium Level</p>
                <p className="text-[11px] text-charcoal-500 mt-2">
                  Supplemental top-dressing or green manuring with Dhaincha recommended.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-forest-50/70 border border-forest-100">
                <p className="text-charcoal-400 font-bold uppercase text-[10px]">Phosphorus (P)</p>
                <p className="text-2xl font-black text-forest-900 mt-1">{activeFarm.phosphorus} kg/ha</p>
                <p className="text-emerald-700 font-bold mt-0.5">High • Abundant</p>
                <p className="text-[11px] text-charcoal-500 mt-2">
                  Strong root proliferation and cold resistance in Himalayan winter.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-forest-50/70 border border-forest-100">
                <p className="text-charcoal-400 font-bold uppercase text-[10px]">Organic Carbon (OC)</p>
                <p className="text-2xl font-black text-forest-900 mt-1">{activeFarm.organicCarbon}%</p>
                <p className="text-forest-800 font-bold mt-0.5">Good Humus</p>
                <p className="text-[11px] text-charcoal-500 mt-2">
                  Fosters microbial biomass and moisture retention across terraced slopes.
                </p>
              </div>
            </div>

            {/* Soil Improvement Suggestions */}
            <div className="p-5 rounded-2xl bg-forest-950 text-white space-y-3">
              <h4 className="text-sm font-bold text-saffron-400 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" />
                <span>Actionable Soil Enrichment Protocol</span>
              </h4>
              <ul className="space-y-2 text-xs text-forest-200">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Vermicompost Integration:</strong> Apply 2 tonnes/acre prior to Rabi tillage to stabilize soil aggregates against slope erosion.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Bio-inoculant:</strong> Treat seeds with <i>PSB (Phosphate Solubilizing Bacteria)</i> to unlock soil-bound phosphorus for seedling vigor.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Mulching:</strong> Spread dry pine needles or paddy straw across vegetable ridges to prevent topsoil drying from valley winds.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* ================= 2. IRRIGATION ADVISOR ================= */}
      {activeSection === 'irrigation' && (
        <div className="space-y-6 animate-fade-in">
          <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-7 shadow-soft space-y-5 text-xs">
            <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
              <div>
                <h3 className="text-base font-extrabold text-forest-900">
                  Precision Water Management & Irrigation Schedule
                </h3>
                <p className="text-charcoal-400">Current Setup: Drip System with Stream / Canal Supply</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-sky-50 text-sky-800 border border-sky-200 flex items-center gap-1">
                <Droplets className="w-3.5 h-3.5 text-sky-600" />
                40% Water Savings
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-2xl bg-charcoal-50 border border-charcoal-100 space-y-1">
                <p className="text-[10px] uppercase font-bold text-charcoal-400">Daily Crop Evapotranspiration (ETc)</p>
                <p className="text-xl font-black text-forest-900">3.8 mm / day</p>
                <p className="text-charcoal-500 text-[11px]">Normal for early winter clear sunshine</p>
              </div>

              <div className="p-4 rounded-2xl bg-charcoal-50 border border-charcoal-100 space-y-1">
                <p className="text-[10px] uppercase font-bold text-charcoal-400">Soil Moisture Depletion</p>
                <p className="text-xl font-black text-forest-900">32% of Field Capacity</p>
                <p className="text-emerald-700 text-[11px] font-bold">Within safe root-zone threshold</p>
              </div>

              <div className="p-4 rounded-2xl bg-charcoal-50 border border-charcoal-100 space-y-1">
                <p className="text-[10px] uppercase font-bold text-charcoal-400">Next Scheduled Watering</p>
                <p className="text-xl font-black text-forest-900">Tomorrow, 06:00 AM</p>
                <p className="text-charcoal-500 text-[11px]">45-minute cycle per terrace sub-plot</p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-forest-50/70 border border-forest-100 space-y-2">
              <h4 className="font-bold text-forest-900">Hill Agriculture Water Efficiency Tips:</h4>
              <p className="text-charcoal-600">
                1. Avoid flood irrigation on slope gradients above 5% to prevent nutrient wash-out into lower terrace walls.<br />
                2. Install check basins on terrace outlets to trap sediment-rich runoff for natural compost formation.<br />
                3. Switch off irrigation 48 hours prior to the forecasted weekend shower (Nov 15) to conserve power and stream flow.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ================= 3. FERTILIZER ADVISOR ================= */}
      {activeSection === 'fertilizer' && (
        <div className="space-y-6 animate-fade-in">
          <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-7 shadow-soft space-y-5 text-xs">
            <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
              <div>
                <h3 className="text-base font-extrabold text-forest-900">
                  Stage-Specific Balanced Fertilizer Plan
                </h3>
                <p className="text-charcoal-400">Designed for Basmati Paddy & Rabi Wheat Rotation</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-forest-50 text-forest-900 border border-forest-200">
                Integrated Nutrition (INM)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-2xl bg-forest-50/60 border border-forest-100 space-y-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-forest-900 text-white">Stage 1: Basal Application</span>
                <p className="font-bold text-forest-900 text-sm">At Final Land Preparation</p>
                <p className="text-charcoal-600 leading-relaxed">
                  - Well-rotted FYM / Compost: 4 tonnes/acre<br />
                  - Single Super Phosphate (SSP): 50 kg/acre<br />
                  - Muriate of Potash (MOP): 20 kg/acre<br />
                  - Neem-coated Urea: 25% of total nitrogen split
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-forest-50/60 border border-forest-100 space-y-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-forest-700 text-white">Stage 2: Tillering / Vegetative</span>
                <p className="font-bold text-forest-900 text-sm">20–25 Days After Sowing</p>
                <p className="text-charcoal-600 leading-relaxed">
                  - Neem-coated Urea: 50% split (top dressing after light hoeing)<br />
                  - Zinc Sulphate: 5 kg/acre (prevents Khaira disease in paddy)<br />
                  - Liquid biofertilizer spray in morning
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-forest-50/60 border border-forest-100 space-y-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-forest-800 text-white">Stage 3: Panicle Initiation</span>
                <p className="font-bold text-forest-900 text-sm">45–50 Days After Sowing</p>
                <p className="text-charcoal-600 leading-relaxed">
                  - Remaining 25% Nitrogen top-dressing<br />
                  - Potassium foliar spray (00:00:50 @ 1.5%) during heading to enhance grain weight and luster
                </p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 text-[11px] leading-relaxed flex items-center gap-2">
              <Info className="w-4 h-4 text-amber-700 shrink-0" />
              <span>
                <strong>Official Protocol:</strong> Dosages should strictly align with your local Krishi Vigyan Kendra (KVK) guidelines. Avoid excessive basal nitrogen to prevent plant softening and lodging under hill gusts.
              </span>
            </div>
          </div>
        </div>
      )}

      {/* ================= 4. PEST RISK ADVISOR ================= */}
      {activeSection === 'pest' && (
        <div className="space-y-6 animate-fade-in">
          <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-7 shadow-soft space-y-5 text-xs">
            <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
              <div>
                <h3 className="text-base font-extrabold text-forest-900">
                  Weather-Triggered Pest & Disease Risk Matrix
                </h3>
                <p className="text-charcoal-400">Pre-symptomatic surveillance based on ambient humidity & temperature</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-800 border border-amber-200">
                2 Moderate Alerts Active
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200 space-y-2">
                <div className="flex items-center justify-between">
                  <p className="font-bold text-amber-950 text-sm">Early Blight Risk (Solanaceous Crops)</p>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-200 text-amber-900">Moderate Risk</span>
                </div>
                <p className="text-charcoal-600">
                  Triggered by daytime temperature of 24°C and dew formation. Watch tomato and potato lower leaves for concentric circular spots.
                </p>
                <p className="font-bold text-amber-900 pt-1">
                  Cultural Control: Prune lower yellowing foliage and mulch soil with dry straw.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-forest-50/70 border border-forest-200 space-y-2">
                <div className="flex items-center justify-between">
                  <p className="font-bold text-forest-950 text-sm">Yellow Stripe Rust (Wheat / Barley)</p>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">Low Risk Currently</span>
                </div>
                <p className="text-charcoal-600">
                  Favored by sub-15°C cold fog. Maintain weekly scouting along northern field borders facing Himalayan winds.
                </p>
                <p className="font-bold text-forest-900 pt-1">
                  Preventive: Grow certified resistant cultivars (HD 3086 / DBW 187).
                </p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 text-[11px] leading-relaxed flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0" />
              <span>
                <strong>Important Advisory Notice:</strong> KisanMitra prioritizes biological bio-agents (*Trichoderma*, *Pseudomonas*) and cultural IPM practices. We do not provide unverified chemical pesticide doses without KVK verification.
              </span>
            </div>
          </div>
        </div>
      )}

      {/* ================= 5. CROP CALENDAR ================= */}
      {activeSection === 'calendar' && (
        <div className="space-y-6 animate-fade-in">
          <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-7 shadow-soft space-y-5 text-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-charcoal-100">
              <div>
                <h3 className="text-base font-extrabold text-forest-900">
                  Visual Agricultural Milestones Calendar
                </h3>
                <p className="text-charcoal-400">Uttarakhand Hill & Valley Seasonal Workflow (Kharif • Rabi • Zaid)</p>
              </div>

              <div className="flex items-center p-1 bg-charcoal-100 rounded-xl text-xs font-bold">
                <button
                  onClick={() => setCalendarView('monthly')}
                  className={`px-3 py-1 rounded-lg ${calendarView === 'monthly' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600'}`}
                >
                  Monthly View
                </button>
                <button
                  onClick={() => setCalendarView('weekly')}
                  className={`px-3 py-1 rounded-lg ${calendarView === 'weekly' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600'}`}
                >
                  Weekly View
                </button>
              </div>
            </div>

            {/* Calendar Milestones Timeline */}
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-forest-50/60 border border-forest-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="w-10 h-10 rounded-xl bg-forest-900 text-saffron-400 font-bold flex items-center justify-center shrink-0">
                    NOV
                  </span>
                  <div>
                    <h4 className="font-extrabold text-forest-900 text-sm">Winter Wheat & Mustard Sowing Window</h4>
                    <p className="text-charcoal-500 text-[11px]">Primary Rabi seed drilling, basal fertilizer application, and bed leveling</p>
                  </div>
                </div>
                <span className="px-3 py-1 rounded-full font-bold text-xs bg-emerald-100 text-emerald-800 shrink-0">
                  Active Now (Optimal)
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-charcoal-50 border border-charcoal-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="w-10 h-10 rounded-xl bg-forest-700 text-white font-bold flex items-center justify-center shrink-0">
                    DEC
                  </span>
                  <div>
                    <h4 className="font-extrabold text-forest-900 text-sm">Crown Root Initiation (CRI) Irrigation</h4>
                    <p className="text-charcoal-500 text-[11px]">First critical irrigation for wheat 21 days after germination</p>
                  </div>
                </div>
                <span className="px-3 py-1 rounded-full font-bold text-xs bg-charcoal-200 text-charcoal-700 shrink-0">
                  Upcoming
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-charcoal-50 border border-charcoal-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="w-10 h-10 rounded-xl bg-forest-700 text-white font-bold flex items-center justify-center shrink-0">
                    JAN
                  </span>
                  <div>
                    <h4 className="font-extrabold text-forest-900 text-sm">Tillering & Frost Protection</h4>
                    <p className="text-charcoal-500 text-[11px]">Light evening sprinkler cycles to buffer young crops against sub-zero Himalayan frost</p>
                  </div>
                </div>
                <span className="px-3 py-1 rounded-full font-bold text-xs bg-charcoal-200 text-charcoal-700 shrink-0">
                  Upcoming
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-charcoal-50 border border-charcoal-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="w-10 h-10 rounded-xl bg-saffron-500 text-charcoal-900 font-bold flex items-center justify-center shrink-0">
                    APR
                  </span>
                  <div>
                    <h4 className="font-extrabold text-forest-900 text-sm">Golden Harvest & Mandi Baisakhi Sales</h4>
                    <p className="text-charcoal-500 text-[11px]">Threshing, moisture testing (below 12%), and mandi transit</p>
                  </div>
                </div>
                <span className="px-3 py-1 rounded-full font-bold text-xs bg-saffron-100 text-saffron-900 shrink-0">
                  Season Close
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
