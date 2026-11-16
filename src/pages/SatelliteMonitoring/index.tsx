import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import {
  Satellite,
  Layers,
  MapPin,
  Calendar,
  AlertTriangle,
  Info,
  Droplets,
  Activity,
  CheckCircle2,
  Maximize2
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';

export const SatelliteMonitoringPage: React.FC = () => {
  const { activeFarm } = useApp();

  const [activeLayer, setActiveLayer] = useState<'rgb' | 'ndvi' | 'ndwi'>('ndvi');
  const [selectedPassDate, setSelectedPassDate] = useState('02 Nov 2026');

  // Historical NDVI index curve (past 6 months)
  const ndviTrend = [
    { month: 'Jun', currentNdvi: 0.35, baseline: 0.38 },
    { month: 'Jul', currentNdvi: 0.58, baseline: 0.55 },
    { month: 'Aug', currentNdvi: 0.78, baseline: 0.72 },
    { month: 'Sep', currentNdvi: 0.84, baseline: 0.80 },
    { month: 'Oct', currentNdvi: 0.82, baseline: 0.79 },
    { month: 'Nov', currentNdvi: 0.76, baseline: 0.74 },
  ];

  return (
    <div className="space-y-6 pb-16 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-charcoal-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-xs font-bold text-forest-800 mb-1.5">
            <Satellite className="w-3.5 h-3.5 text-sky-500" />
            <span>Sentinel-2 Multispectral Earth Observation</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
            Satellite & Field Remote Sensing
          </h1>
          <p className="text-xs text-charcoal-400 mt-1">
            Multispectral NDVI vegetation vigor index, moisture stress heatmaps, and field canopy monitoring
          </p>
        </div>

        {/* Integration Status Badge */}
        <span className="px-3.5 py-1.5 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300 flex items-center gap-1.5">
          <Info className="w-4 h-4 text-amber-700" />
          <span>Satellite Integration Preview</span>
        </span>
      </div>

      {/* Prominent Disclaimer Notice */}
      <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 flex items-start gap-3 text-xs text-amber-950">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <p className="font-bold">Satellite Data Notice & Backend Readiness:</p>
          <p className="text-charcoal-600 text-[11px] leading-relaxed">
            Live Sentinel-2 / Landsat-8 API endpoints are scheduled for deployment. The polygon boundary viewer and NDVI time-series curves below demonstrate how 10-meter spatial resolution spectral indices will be visualized for your registered parcel: <strong>{activeFarm.name}</strong>.
          </p>
        </div>
      </div>

      {/* Main Satellite Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Interactive Satellite Viewer (7 Cols) */}
        <div className="lg:col-span-7 rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-charcoal-100 gap-3">
            <div>
              <h3 className="text-base font-extrabold text-forest-900">
                Field Parcel Spectral Viewer
              </h3>
              <p className="text-xs text-charcoal-400">
                {activeFarm.name} • GPS ({activeFarm.latitude || '30.3421'}°N, {activeFarm.longitude || '78.1189'}°E)
              </p>
            </div>

            {/* Layer Toggles */}
            <div className="flex items-center p-1 bg-charcoal-100 rounded-xl text-xs font-bold">
              <button
                onClick={() => setActiveLayer('rgb')}
                className={`px-3 py-1 rounded-lg ${activeLayer === 'rgb' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600'}`}
              >
                True Color (RGB)
              </button>
              <button
                onClick={() => setActiveLayer('ndvi')}
                className={`px-3 py-1 rounded-lg ${activeLayer === 'ndvi' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600'}`}
              >
                NDVI Vigor
              </button>
              <button
                onClick={() => setActiveLayer('ndwi')}
                className={`px-3 py-1 rounded-lg ${activeLayer === 'ndwi' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600'}`}
              >
                Moisture (NDWI)
              </button>
            </div>
          </div>

          {/* Satellite Viewer Container */}
          <div className="relative rounded-2xl overflow-hidden h-80 sm:h-96 border border-charcoal-200 bg-charcoal-900 group">
            {/* Base Image */}
            <img
              src="/hero-bg.jpg"
              alt="Satellite Terraced Plot Observation"
              className={`w-full h-full object-cover transition-all duration-500 ${
                activeLayer === 'ndvi' ? 'contrast-125 saturate-200 hue-rotate-15' : ''
              }`}
            />

            {/* Polygon Boundary Overlay */}
            <div className="absolute inset-0 pointer-events-none flex items-center justify-center p-8">
              <div className="w-3/4 h-3/4 border-2 border-dashed border-saffron-400 rounded-2xl bg-saffron-400/10 flex flex-col justify-between p-3">
                <span className="self-start px-2 py-0.5 rounded text-[10px] font-bold bg-forest-950/90 text-white backdrop-blur-md">
                  Field Boundary: {activeFarm.size} Acres
                </span>
                <span className="self-end px-2 py-0.5 rounded text-[10px] font-mono text-saffron-300 bg-forest-950/90">
                  Avg NDVI: 0.76 (Vigorous)
                </span>
              </div>
            </div>

            {/* Bottom Floating Legend */}
            <div className="absolute bottom-3 left-3 right-3 p-2.5 rounded-xl bg-forest-950/85 backdrop-blur-md border border-forest-800 text-white flex items-center justify-between text-[11px]">
              <span className="font-bold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                Pass: {selectedPassDate} (Cloud cover 2.1%)
              </span>

              <div className="flex items-center gap-2">
                <span className="text-[10px] text-forest-300">Stress</span>
                <div className="w-24 h-2 rounded-full bg-gradient-to-r from-rose-500 via-amber-400 to-emerald-500" />
                <span className="text-[10px] text-forest-300">Vigorous</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Spectral Telemetry & Historical Curve (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Telemetry Metrics */}
          <div className="rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft space-y-4">
            <h4 className="text-base font-extrabold text-forest-900">
              Remote Sensing Field Telemetry
            </h4>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-2xl bg-forest-50/70 border border-forest-100">
                <span className="text-charcoal-400 uppercase text-[10px] font-bold">Mean NDVI</span>
                <p className="text-2xl font-black text-forest-900 mt-1">0.76</p>
                <span className="text-emerald-700 font-bold text-[10px]">High Biomass Density</span>
              </div>

              <div className="p-3 rounded-2xl bg-sky-50/70 border border-sky-100">
                <span className="text-charcoal-400 uppercase text-[10px] font-bold">Canopy NDWI</span>
                <p className="text-2xl font-black text-sky-950 mt-1">+0.32</p>
                <span className="text-sky-700 font-bold text-[10px]">Adequate Cell Turgor</span>
              </div>
            </div>

            <div className="space-y-2 pt-2 border-t border-charcoal-100 text-xs">
              <div className="flex justify-between">
                <span className="text-charcoal-500">Sensor Platform:</span>
                <strong className="text-forest-900">ESA Sentinel-2A Multispectral</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-charcoal-500">Spatial Resolution:</span>
                <strong className="text-forest-900">10 Meters / Pixel</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-charcoal-500">Revisit Frequency:</span>
                <strong className="text-forest-900">Every 5 Days</strong>
              </div>
            </div>
          </div>

          {/* Historical NDVI Curve */}
          <div className="rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft">
            <h4 className="text-xs font-bold text-forest-900 uppercase tracking-wider mb-2">
              6-Month NDVI Historical Trajectory
            </h4>
            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={ndviTrend}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                  <YAxis domain={[0.2, 1.0]} tick={{ fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#174B35',
                      color: '#fff',
                      borderRadius: '8px',
                      fontSize: '11px',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="currentNdvi"
                    name="Observed NDVI"
                    stroke="#174B35"
                    strokeWidth={2.5}
                    dot={{ r: 3 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="baseline"
                    name="5-Yr Average"
                    stroke="#E8AD45"
                    strokeWidth={2}
                    strokeDasharray="3 3"
                    dot={{ r: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
