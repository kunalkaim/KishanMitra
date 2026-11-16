import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { uttarakhandDistricts } from '../../data/demoData';
import {
  MapPin,
  Mountain,
  CloudRain,
  Layers,
  Sprout,
  Compass,
  ArrowRight,
  ChevronRight,
  Filter,
  CheckCircle2,
  Scale
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';

export const RegionIntelligencePage: React.FC = () => {
  const { setWeatherDistrict, showToast } = useApp();

  const [selectedState, setSelectedState] = useState('Uttarakhand');
  const [selectedDistrictId, setSelectedDistrictId] = useState('dehradun');
  const [compareDistrictId, setCompareDistrictId] = useState('chamoli');
  const [showComparison, setShowComparison] = useState(false);

  const activeDistrict = uttarakhandDistricts.find(d => d.id === selectedDistrictId) || uttarakhandDistricts[0];
  const compareDistrict = uttarakhandDistricts.find(d => d.id === compareDistrictId) || uttarakhandDistricts[6];

  // Elevation and rainfall chart data
  const chartData = uttarakhandDistricts.map(d => ({
    name: d.name,
    rainfall: d.avgRainfallMm,
  }));

  const handleSelectDistrict = (distId: string) => {
    setSelectedDistrictId(distId);
    const d = uttarakhandDistricts.find(item => item.id === distId);
    if (d) {
      setWeatherDistrict(d.name);
      showToast(`Selected ${d.name} District. Agro-climatic context updated.`, 'info');
    }
  };

  return (
    <div className="space-y-6 pb-16 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-charcoal-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-xs font-bold text-forest-800 mb-1.5">
            <Compass className="w-3.5 h-3.5 text-saffron-500" />
            <span>Agro-Climatic Regional Knowledge Base</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
            Region & District Intelligence
          </h1>
          <p className="text-xs text-charcoal-400 mt-1">
            Explore agro-climatic zones, elevation gradients (200m–4,500m), soil profiles, and crop suitability across Uttarakhand
          </p>
        </div>

        {/* State Selector (Scalable for All India) */}
        <div className="flex items-center gap-2">
          <label className="text-xs font-bold text-charcoal-500">State Focus:</label>
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="px-3.5 py-2 rounded-xl border border-charcoal-200 bg-white text-xs font-bold text-forest-900 shadow-sm focus:ring-2 focus:ring-forest-600 focus:outline-none"
          >
            <option value="Uttarakhand">Uttarakhand (Active Focus)</option>
            <option value="Himachal Pradesh">Himachal Pradesh (Expansion Ready)</option>
            <option value="Punjab">Punjab (Terai / Plains Expansion)</option>
            <option value="Uttar Pradesh">Uttar Pradesh (Gangetic Basin)</option>
            <option value="Rajasthan">Rajasthan (Arid Agriculture)</option>
          </select>
        </div>
      </div>

      {/* Main Grid: Interactive Map Explorer & District Detail Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: District Cards Grid / Interactive Selector (7 Cols) */}
        <div className="lg:col-span-7 rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-charcoal-100">
            <div>
              <h3 className="text-base font-extrabold text-forest-900">
                13 Districts of Uttarakhand
              </h3>
              <p className="text-xs text-charcoal-400">Click a district to view detailed micro-climate and crop suitability</p>
            </div>
            <span className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-forest-50 text-forest-800">
              Selectable
            </span>
          </div>

          {/* Interactive District Chips Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {uttarakhandDistricts.map((d) => {
              const isSelected = d.id === selectedDistrictId;
              return (
                <button
                  key={d.id}
                  onClick={() => handleSelectDistrict(d.id)}
                  className={`p-3 rounded-2xl text-left border transition-all ${
                    isSelected
                      ? 'bg-forest-900 text-white border-forest-900 shadow-md ring-2 ring-saffron-400/40'
                      : 'bg-kisan-bg hover:bg-forest-50 border-charcoal-100 text-charcoal-800'
                  }`}
                >
                  <p className="font-extrabold text-xs flex items-center justify-between">
                    <span>{d.name}</span>
                    {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-saffron-400 shrink-0" />}
                  </p>
                  <p className={`text-[10px] mt-1 truncate ${isSelected ? 'text-forest-200' : 'text-charcoal-400'}`}>
                    {d.elevationRange}
                  </p>
                </button>
              );
            })}
          </div>

          {/* District Rainfall Comparison Chart */}
          <div className="pt-4 border-t border-charcoal-100">
            <h4 className="text-xs font-bold text-forest-900 uppercase tracking-wider mb-3">
              Average Annual Rainfall Comparison (mm/year)
            </h4>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" tick={{ fontSize: 9 }} interval={0} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#174B35',
                      color: '#fff',
                      borderRadius: '8px',
                      fontSize: '11px',
                    }}
                  />
                  <Bar dataKey="rainfall" fill="#3D8054" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Right: Selected District Intelligence Card (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft space-y-5">
            <div className="flex items-start justify-between pb-3 border-b border-charcoal-100">
              <div>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-forest-100 text-forest-900">
                  Agro-Climatic Zone
                </span>
                <h3 className="text-xl font-black text-forest-900 mt-1">
                  {activeDistrict.name} District
                </h3>
                <p className="text-xs text-charcoal-500 font-medium">{activeDistrict.agroZone}</p>
              </div>

              <div className="w-10 h-10 rounded-2xl bg-forest-50 text-forest-700 flex items-center justify-center shrink-0">
                <MapPin className="w-5 h-5" />
              </div>
            </div>

            <p className="text-xs text-charcoal-600 leading-relaxed">
              {activeDistrict.description}
            </p>

            {/* Microclimate Matrix */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-2xl bg-forest-50/60 border border-forest-100">
                <div className="flex items-center gap-1.5 text-charcoal-500 font-medium">
                  <Mountain className="w-3.5 h-3.5 text-forest-700" />
                  <span>Altitude Range</span>
                </div>
                <p className="font-black text-forest-900 text-sm mt-1">{activeDistrict.elevationRange}</p>
              </div>

              <div className="p-3 rounded-2xl bg-forest-50/60 border border-forest-100">
                <div className="flex items-center gap-1.5 text-charcoal-500 font-medium">
                  <CloudRain className="w-3.5 h-3.5 text-sky-600" />
                  <span>Annual Rainfall</span>
                </div>
                <p className="font-black text-forest-900 text-sm mt-1">{activeDistrict.avgRainfallMm} mm</p>
              </div>
            </div>

            {/* Soil Type */}
            <div className="p-3 rounded-2xl bg-charcoal-50 border border-charcoal-100 text-xs">
              <span className="text-charcoal-400 font-medium">Dominant Soil Profile:</span>
              <p className="font-bold text-forest-900 text-sm mt-0.5">{activeDistrict.soilType}</p>
            </div>

            {/* Major Cash & Food Crops */}
            <div>
              <p className="text-[11px] font-bold text-charcoal-400 uppercase tracking-wider mb-2">
                Predominant Cash & Traditional Crops
              </p>
              <div className="flex flex-wrap gap-1.5">
                {activeDistrict.majorCrops.map((c, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-forest-50 border border-forest-200 text-forest-900"
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-2 border-t border-charcoal-100">
              <button
                onClick={() => setShowComparison(!showComparison)}
                className="w-full py-2.5 rounded-xl text-xs font-bold bg-forest-900 hover:bg-forest-800 text-white transition-all flex items-center justify-center gap-2 shadow-sm"
              >
                <Scale className="w-3.5 h-3.5 text-saffron-400" />
                <span>{showComparison ? 'Hide Region Comparison' : 'Compare with Another District'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Region Comparison Modal / Drawer */}
      {showComparison && (
        <div className="rounded-3xl bg-white border border-charcoal-200 p-6 shadow-soft animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-charcoal-100 gap-3">
            <div>
              <h3 className="text-base font-extrabold text-forest-900">
                Inter-District Comparative Agricultural Intelligence
              </h3>
              <p className="text-xs text-charcoal-400">Side-by-side agro-climatic assessment</p>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-charcoal-600">Compare With:</span>
              <select
                value={compareDistrictId}
                onChange={(e) => setCompareDistrictId(e.target.value)}
                className="px-3 py-1.5 rounded-xl border border-charcoal-200 text-xs font-bold text-forest-900 focus:outline-none"
              >
                {uttarakhandDistricts.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
            <div className="p-4 rounded-2xl bg-forest-50/70 border border-forest-100 space-y-2">
              <h4 className="font-extrabold text-forest-900 text-sm">{activeDistrict.name} District</h4>
              <p className="text-charcoal-600">Zone: <strong>{activeDistrict.agroZone}</strong></p>
              <p className="text-charcoal-600">Elevation: <strong>{activeDistrict.elevationRange}</strong></p>
              <p className="text-charcoal-600">Rainfall: <strong>{activeDistrict.avgRainfallMm} mm/year</strong></p>
              <p className="text-charcoal-600">Soil: <strong>{activeDistrict.soilType}</strong></p>
              <p className="text-charcoal-600">Major Crops: {activeDistrict.majorCrops.join(', ')}</p>
            </div>

            <div className="p-4 rounded-2xl bg-saffron-50/70 border border-saffron-100 space-y-2">
              <h4 className="font-extrabold text-charcoal-900 text-sm">{compareDistrict.name} District</h4>
              <p className="text-charcoal-600">Zone: <strong>{compareDistrict.agroZone}</strong></p>
              <p className="text-charcoal-600">Elevation: <strong>{compareDistrict.elevationRange}</strong></p>
              <p className="text-charcoal-600">Rainfall: <strong>{compareDistrict.avgRainfallMm} mm/year</strong></p>
              <p className="text-charcoal-600">Soil: <strong>{compareDistrict.soilType}</strong></p>
              <p className="text-charcoal-600">Major Crops: {compareDistrict.majorCrops.join(', ')}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
