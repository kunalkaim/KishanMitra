import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { uttarakhandDistricts } from '../../data/demoData';
import {
  CloudSun,
  Sun,
  CloudRain,
  Wind,
  Droplets,
  AlertTriangle,
  Calendar,
  CheckCircle2,
  TrendingDown,
  Info,
  Compass,
  Thermometer,
  ShieldAlert
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend
} from 'recharts';

export const WeatherPage: React.FC = () => {
  const { weather, setWeatherDistrict, showToast } = useApp();
  const [selectedDistrict, setSelectedDistrict] = useState('Dehradun');

  const handleDistrictChange = (dist: string) => {
    setSelectedDistrict(dist);
    setWeatherDistrict(dist);
    showToast(`Weather telemetry switched to ${dist} station.`, 'info');
  };

  const forecastData = weather.forecast7Day.map(f => ({
    day: f.day,
    date: f.date,
    tempMax: f.tempMax,
    tempMin: f.tempMin,
    rainfallMm: f.rainfallMm,
    humidity: f.humidity,
    rainfallProb: f.rainfallProb,
  }));

  return (
    <div className="space-y-6 pb-16 animate-fade-in">
      {/* Header with District Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-charcoal-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-xs font-bold text-forest-800 mb-1.5">
            <CloudSun className="w-3.5 h-3.5 text-saffron-500" />
            <span>Agro-Meteorological Telemetry</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
            Agricultural Weather Intelligence
          </h1>
          <p className="text-xs text-charcoal-400 mt-1">
            7-day agricultural forecasts, sowing window advisories, rain probability thresholds, and spray guidelines
          </p>
        </div>

        {/* District Weather Switcher */}
        <div className="flex items-center gap-2">
          <label className="text-xs font-bold text-charcoal-500">Weather Station:</label>
          <select
            value={selectedDistrict}
            onChange={(e) => handleDistrictChange(e.target.value)}
            className="px-3.5 py-2 rounded-xl border border-charcoal-200 bg-white text-xs font-bold text-forest-900 shadow-sm focus:ring-2 focus:ring-forest-600 focus:outline-none"
          >
            {uttarakhandDistricts.map(d => (
              <option key={d.id} value={d.name}>{d.name} ({d.elevationRange})</option>
            ))}
          </select>
        </div>
      </div>

      {/* Demo Notice Banner */}
      <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-between text-xs text-amber-900">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-amber-600 shrink-0" />
          <span>
            <strong>Demonstration Weather Data:</strong> Prepared for IMD (India Meteorological Dept) & OpenWeatherMap API connection.
          </span>
        </div>
        <span className="hidden sm:inline-block font-mono text-[10px] text-amber-700 uppercase font-bold">
          API Adapter Ready
        </span>
      </div>

      {/* Current Weather Hero Banner */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-forest-950 via-forest-900 to-forest-800 text-white shadow-soft-lg border border-forest-700/50 relative overflow-hidden">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
          <div className="md:col-span-7 space-y-3">
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-forest-800/80 text-saffron-300 border border-forest-700">
              Station: {weather.location}
            </span>
            <div className="flex items-baseline gap-4">
              <span className="text-5xl sm:text-6xl font-black tracking-tight">
                {weather.temperature}°C
              </span>
              <span className="text-lg font-bold text-forest-200">
                {weather.condition}
              </span>
            </div>

            <p className="text-xs sm:text-sm text-forest-100/90 leading-relaxed max-w-xl">
              🌾 <strong>Field Advisory:</strong> {weather.advisory}
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-4 text-xs text-forest-200">
              <span className="flex items-center gap-1.5">
                <Thermometer className="w-4 h-4 text-saffron-400" />
                Min: {weather.tempMin}°C • Max: {weather.tempMax}°C
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5">
                <Droplets className="w-4 h-4 text-sky-400" />
                Humidity: {weather.humidity}%
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5">
                <Wind className="w-4 h-4 text-emerald-400" />
                Wind: {weather.windSpeed} km/h ({weather.windDirection})
              </span>
            </div>
          </div>

          <div className="md:col-span-5 flex flex-col gap-3">
            <div className="p-4 rounded-2xl bg-forest-900/80 border border-forest-700/80 space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-forest-300">Sowing Window:</span>
                <span className="px-2 py-0.5 rounded-full font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  {weather.sowingWindowStatus}
                </span>
              </div>
              <p className="text-[11px] text-forest-200 leading-snug">
                Ideal soil temperature for Rabi nursery bed seeding and winter mustard sowing.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-forest-900/80 border border-forest-700/80 space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-forest-300">Irrigation Timing:</span>
                <span className="px-2 py-0.5 rounded-full font-bold bg-saffron-500/20 text-saffron-300 border border-saffron-500/30">
                  Favorable Now
                </span>
              </div>
              <p className="text-[11px] text-forest-200 leading-snug">
                Zero rainfall today; water drip lines early morning (06:00-09:00 AM) to minimize evapotranspiration loss.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 7-Day Forecast Cards Carousel/Grid */}
      <div>
        <h3 className="text-base font-extrabold text-forest-900 mb-3">
          7-Day Weather & Agricultural Forecast
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          {weather.forecast7Day.map((f, idx) => (
            <div
              key={idx}
              className={`p-3.5 rounded-2xl text-center border transition-all ${
                idx === 0
                  ? 'bg-forest-900 text-white border-forest-800 shadow-md ring-2 ring-saffron-400/30'
                  : 'bg-white border-charcoal-100 hover:border-forest-200 text-charcoal-800'
              }`}
            >
              <p className="text-xs font-black uppercase tracking-wider">{f.day}</p>
              <p className={`text-[10px] ${idx === 0 ? 'text-forest-200' : 'text-charcoal-400'}`}>
                {f.date}
              </p>

              <div className="my-2 flex justify-center">
                {f.rainfallProb > 40 ? (
                  <CloudRain className={`w-6 h-6 ${idx === 0 ? 'text-sky-300' : 'text-sky-500'}`} />
                ) : (
                  <Sun className={`w-6 h-6 ${idx === 0 ? 'text-saffron-400' : 'text-saffron-500'}`} />
                )}
              </div>

              <p className="text-xs font-bold truncate">{f.condition}</p>

              <div className="mt-2 text-xs font-bold flex items-center justify-center gap-1">
                <span className={idx === 0 ? 'text-white' : 'text-forest-900'}>{f.tempMax}°</span>
                <span className={`text-[10px] ${idx === 0 ? 'text-forest-300' : 'text-charcoal-400'}`}>
                  / {f.tempMin}°
                </span>
              </div>

              <div className="mt-2 pt-2 border-t border-charcoal-100/30 text-[10px] font-semibold flex items-center justify-center gap-1 text-sky-500">
                <Droplets className="w-3 h-3" />
                <span>{f.rainfallProb}% Rain</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Weather Visualizations (Recharts) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Temperature Trend */}
        <div className="p-6 rounded-3xl bg-white border border-charcoal-100 shadow-soft">
          <div className="flex items-center justify-between pb-3 border-b border-charcoal-100 mb-4">
            <h4 className="text-sm font-bold text-forest-900">
              7-Day Temperature Range Curve (°C)
            </h4>
            <span className="text-[11px] text-charcoal-400 font-semibold">Max vs Min</span>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={forecastData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                <YAxis unit="°C" domain={[8, 32]} tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#174B35',
                    color: '#fff',
                    borderRadius: '8px',
                    fontSize: '11px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line
                  type="monotone"
                  dataKey="tempMax"
                  name="Max Temp (°C)"
                  stroke="#E8AD45"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="tempMin"
                  name="Min Temp (°C)"
                  stroke="#3D8054"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Rainfall Probability & Volume */}
        <div className="p-6 rounded-3xl bg-white border border-charcoal-100 shadow-soft">
          <div className="flex items-center justify-between pb-3 border-b border-charcoal-100 mb-4">
            <h4 className="text-sm font-bold text-forest-900">
              Precipitation Probability (%) & Expected Volume (mm)
            </h4>
            <span className="text-[11px] text-sky-600 font-bold">Rain Forecast</span>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={forecastData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                <YAxis yAxisId="left" unit="%" domain={[0, 100]} tick={{ fontSize: 11 }} />
                <YAxis yAxisId="right" orientation="right" unit="mm" domain={[0, 20]} tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#174B35',
                    color: '#fff',
                    borderRadius: '8px',
                    fontSize: '11px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Bar yAxisId="left" dataKey="rainfallProb" name="Rainfall Prob (%)" fill="#94BEA3" radius={[4, 4, 0, 0]} />
                <Bar yAxisId="right" dataKey="rainfallMm" name="Volume (mm)" fill="#3D8054" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Critical Weather Alerts & Guidance */}
      <div className="rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft space-y-4">
        <h4 className="text-base font-extrabold text-forest-900 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-saffron-600" />
          <span>Agricultural Weather Risk Guidance</span>
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200 space-y-1.5">
            <p className="font-extrabold text-amber-900">Incoming Convective Rainfall (Nov 15)</p>
            <p className="text-charcoal-600 leading-relaxed">
              70% probability of 14mm shower. Avoid broadcasting granular nitrogen 48 hours prior to prevent surface runoff into valley nullahs.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-forest-50/70 border border-forest-200 space-y-1.5">
            <p className="font-extrabold text-forest-900">Spraying Suitability</p>
            <p className="text-charcoal-600 leading-relaxed">
              Wind speed is moderate (8 km/h). Tomorrow morning (07:00–10:00 AM) is optimal for applying organic bio-fungicides or micronutrient foliar spray.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-sky-50/70 border border-sky-200 space-y-1.5">
            <p className="font-extrabold text-sky-900">Winter Frost Alert</p>
            <p className="text-charcoal-600 leading-relaxed">
              Night temperature predicted to touch 11°C. High altitude orchards in Chamoli & Uttarkashi should monitor young saplings.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
