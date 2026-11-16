import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import { StatCard } from '../../components/common/StatCard';
import { ChartCard } from '../../components/common/ChartCard';
import {
  Sprout,
  Sparkles,
  CloudSun,
  AlertTriangle,
  TrendingUp,
  MapPin,
  Calendar,
  Droplets,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Bug,
  Thermometer,
  Wind,
  Layers,
  ChevronRight,
  ExternalLink,
  Plus
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid
} from 'recharts';

export const DashboardPage: React.FC = () => {
  const {
    profile,
    farms,
    activeFarm,
    weather,
    mandiPrices,
    currentRecommendation,
    notifications,
    diagnosesHistory,
    t
  } = useApp();

  const navigate = useNavigate();

  const totalArea = farms.reduce((acc, f) => acc + f.size, 0);
  const topCrop = currentRecommendation.recommendedCrops[0];

  // 7-day temperature & humidity preview for mini-chart
  const weatherMiniChart = weather.forecast7Day.map(f => ({
    day: f.day,
    temp: f.tempMax,
    rainProb: f.rainfallProb,
  }));

  // Mandi price preview
  const nearbyMandis = mandiPrices.slice(0, 3);

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* ================= 1. GREETING HEADER ================= */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 sm:p-7 rounded-3xl bg-gradient-to-r from-forest-950 via-forest-900 to-forest-800 text-white shadow-soft-lg border border-forest-700/40 relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 opacity-10 pointer-events-none flex items-center pr-8">
          <Sprout className="w-64 h-64 text-white" />
        </div>

        <div className="relative z-10 space-y-1.5">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-800/80 border border-forest-600/50 text-[11px] font-semibold text-saffron-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Farm Location: {activeFarm.village}, {activeFarm.district} ({activeFarm.elevation}m ASL)</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Namaste, {profile.name}! Welcome to KisanMitra.
          </h1>

          <p className="text-xs sm:text-sm text-forest-200/90 max-w-2xl font-normal">
            Your land intelligence is fully synchronized. Optimal weather conditions for Kharif-Rabi transition.
          </p>
        </div>

        <div className="relative z-10 flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => navigate('/crop-recommendation')}
            className="px-4 py-2.5 rounded-xl font-bold text-xs bg-saffron-500 hover:bg-saffron-400 text-charcoal-900 shadow-md transition-all active:scale-95 flex items-center gap-1.5"
          >
            <Sparkles className="w-4 h-4" />
            <span>New Crop Plan</span>
          </button>

          <button
            onClick={() => navigate('/advisory')}
            className="px-4 py-2.5 rounded-xl font-bold text-xs bg-forest-800 hover:bg-forest-700 text-white border border-forest-600 transition-all flex items-center gap-1.5"
          >
            <Bug className="w-4 h-4 text-emerald-300" />
            <span>Pest & Disease Advisory</span>
          </button>
        </div>
      </div>

      {/* ================= 2. OVERVIEW STATISTICS ================= */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          title="Total Farms"
          value={farms.length}
          subtitle="Registered Field Plots"
          icon={Sprout}
          variant="forest"
          onClick={() => navigate('/farms')}
        />

        <StatCard
          title="Cultivated Area"
          value={`${totalArea.toFixed(1)} Ac`}
          subtitle="Terraces & Orchards"
          icon={Layers}
          variant="forest"
          onClick={() => navigate('/farms')}
        />

        <StatCard
          title="Active Crop Plan"
          value={topCrop ? topCrop.name.split(' ')[0] : 'Basmati'}
          subtitle={`${topCrop ? topCrop.suitabilityScore : 96}% Ensemble Fit`}
          icon={Sparkles}
          variant="saffron"
          badge="Hybrid AI"
          onClick={() => navigate('/crop-recommendation')}
        />

        <StatCard
          title="Current Weather"
          value={`${weather.temperature}°C`}
          subtitle={weather.condition}
          icon={CloudSun}
          variant="neutral"
          trend={{ value: 'Clear', isPositive: true, label: 'Optimal for field work' }}
          onClick={() => navigate('/weather')}
        />

        <StatCard
          title="Pending Alerts"
          value={notifications.filter(n => !n.read).length}
          subtitle="Weather & Mandi"
          icon={AlertTriangle}
          variant="emerald"
          badge="Active"
          onClick={() => navigate('/weather')}
        />
      </div>

      {/* ================= 3. WEATHER & HYBRID AI HERO CARDS ================= */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: AI Recommendation Summary (7 Cols) */}
        <div className="lg:col-span-7 rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
              <div className="flex items-center gap-2">
                <span className="p-2 rounded-xl bg-forest-50 text-forest-700">
                  <Sparkles className="w-5 h-5" />
                </span>
                <div>
                  <h3 className="text-base font-extrabold text-forest-900">
                    AI Crop Recommendation Summary
                  </h3>
                  <p className="text-xs text-charcoal-400">
                    Calculated for {activeFarm.name} ({activeFarm.soilType} soil)
                  </p>
                </div>
              </div>

              <span className="px-3 py-1 rounded-full text-xs font-black bg-emerald-50 text-emerald-800 border border-emerald-200">
                {currentRecommendation.ensembleConfidence}% Confidence
              </span>
            </div>

            {/* Recommended Crop Showcase Banner */}
            <div className="mt-5 p-4 rounded-2xl bg-forest-50/60 border border-forest-100 flex flex-col sm:flex-row items-center gap-4">
              <img
                src={topCrop.image}
                alt={topCrop.name}
                className="w-full sm:w-28 h-28 rounded-xl object-cover shadow-sm shrink-0"
              />

              <div className="flex-1 space-y-1 text-center sm:text-left">
                <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
                  <h4 className="text-base font-extrabold text-forest-900 leading-tight">
                    {topCrop.name}
                  </h4>
                  <span className="text-xs font-semibold text-forest-700 bg-white px-2 py-0.5 rounded-md border border-forest-200">
                    {topCrop.hindiName}
                  </span>
                </div>

                <p className="text-xs text-charcoal-600 leading-snug">
                  {topCrop.shortExplanation}
                </p>

                <div className="pt-2 flex flex-wrap items-center justify-center sm:justify-start gap-3 text-xs text-charcoal-600 font-semibold">
                  <span className="flex items-center gap-1 text-forest-800">
                    <Droplets className="w-3.5 h-3.5 text-forest-600" />
                    Water: {topCrop.waterRequirement}
                  </span>
                  <span>•</span>
                  <span>Duration: {topCrop.growingDurationDays} Days</span>
                  <span>•</span>
                  <span className="text-emerald-700 font-bold">
                    Est. Profit: ₹{topCrop.estimatedNetProfitPerAcre.toLocaleString()}/ac
                  </span>
                  {topCrop.modalPricePerQuintal && (
                    <>
                      <span>•</span>
                      <span className="text-amber-800 font-bold">
                        Mandi: ₹{topCrop.modalPricePerQuintal.toLocaleString()}/q
                      </span>
                    </>
                  )}
                  {topCrop.ragCitations && topCrop.ragCitations.length > 0 && (
                    <>
                      <span>•</span>
                      <span className="text-forest-800 font-bold bg-forest-50 px-2 py-0.5 rounded border border-forest-200">
                        POP: {topCrop.ragCitations[0].publisher.includes('VPKAS') ? 'ICAR-VPKAS Almora' : 'GBPUAT Pantnagar'}
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Alternative Crops Chips */}
            <div className="mt-4 pt-3 border-t border-charcoal-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <span className="font-bold text-charcoal-500">Top Alternative Crops:</span>
              <div className="flex flex-wrap gap-2">
                {currentRecommendation.recommendedCrops.slice(1).map((alt, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg bg-charcoal-50 border border-charcoal-200 font-semibold text-charcoal-800 flex items-center gap-1.5"
                  >
                    <span>{alt.name.split('(')[0]}</span>
                    <span className="text-[10px] font-bold text-forest-700 bg-white px-1 rounded">
                      {alt.suitabilityScore}%
                    </span>
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-charcoal-100 flex items-center justify-between">
            <span className="text-xs text-charcoal-400">
              Validated across 3 models (Fuzzy, Bayesian & Decision Tree)
            </span>
            <button
              onClick={() => navigate('/crop-recommendation')}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-forest-800 hover:text-forest-900 group"
            >
              <span>View Detailed Recommendation</span>
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </button>
          </div>
        </div>

        {/* Right: Weather Overview (5 Cols) */}
        <div className="lg:col-span-5 rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
              <div className="flex items-center gap-2">
                <span className="p-2 rounded-xl bg-saffron-50 text-saffron-700">
                  <CloudSun className="w-5 h-5" />
                </span>
                <div>
                  <h3 className="text-base font-extrabold text-forest-900">
                    Weather Overview
                  </h3>
                  <p className="text-xs text-charcoal-400">{weather.location}</p>
                </div>
              </div>

              <NavLink
                to="/weather"
                className="text-xs font-bold text-forest-700 hover:underline flex items-center gap-1"
              >
                7-Day Forecast <ChevronRight className="w-3.5 h-3.5" />
              </NavLink>
            </div>

            {/* Current Metrics Grid */}
            <div className="mt-5 grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-2xl bg-forest-50/50 border border-forest-100">
                <div className="flex items-center gap-1.5 text-charcoal-500 font-medium">
                  <Thermometer className="w-3.5 h-3.5 text-rose-500" />
                  <span>Temperature</span>
                </div>
                <p className="text-xl font-black text-forest-900 mt-1">
                  {weather.temperature}°C
                </p>
                <p className="text-[10px] text-charcoal-400">Min 14° • Max 27°</p>
              </div>

              <div className="p-3 rounded-2xl bg-forest-50/50 border border-forest-100">
                <div className="flex items-center gap-1.5 text-charcoal-500 font-medium">
                  <Droplets className="w-3.5 h-3.5 text-sky-500" />
                  <span>Relative Humidity</span>
                </div>
                <p className="text-xl font-black text-forest-900 mt-1">
                  {weather.humidity}%
                </p>
                <p className="text-[10px] text-charcoal-400">Optimal vegetative range</p>
              </div>

              <div className="p-3 rounded-2xl bg-forest-50/50 border border-forest-100">
                <div className="flex items-center gap-1.5 text-charcoal-500 font-medium">
                  <CloudSun className="w-3.5 h-3.5 text-forest-600" />
                  <span>Rain Probability</span>
                </div>
                <p className="text-xl font-black text-forest-900 mt-1">
                  {weather.rainfallProbability}%
                </p>
                <p className="text-[10px] text-charcoal-400">Expected 0.0 mm today</p>
              </div>

              <div className="p-3 rounded-2xl bg-forest-50/50 border border-forest-100">
                <div className="flex items-center gap-1.5 text-charcoal-500 font-medium">
                  <Wind className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Wind Speed</span>
                </div>
                <p className="text-xl font-black text-forest-900 mt-1">
                  {weather.windSpeed} km/h
                </p>
                <p className="text-[10px] text-charcoal-400">Direction {weather.windDirection}</p>
              </div>
            </div>

            {/* Mini Trend Line Chart */}
            <div className="mt-4 pt-3 border-t border-charcoal-100">
              <p className="text-[11px] font-bold text-charcoal-400 uppercase tracking-wider mb-2">
                7-Day Max Temperature Trend (°C)
              </p>
              <div className="h-20 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={weatherMiniChart}>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#174B35',
                        color: '#fff',
                        borderRadius: '8px',
                        fontSize: '11px',
                        border: 'none',
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="temp"
                      stroke="#E8AD45"
                      strokeWidth={2.5}
                      dot={{ r: 3, fill: '#E8AD45' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="mt-4 p-3 rounded-xl bg-saffron-50/80 border border-saffron-200/80 text-[11px] text-saffron-900 font-medium">
            🌾 <strong>Agri-Advisory:</strong> {weather.advisory}
          </div>
        </div>
      </div>

      {/* ================= 4. MARKET INTELLIGENCE & FARM HEALTH ================= */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Market Intelligence (6 Cols) */}
        <div className="lg:col-span-6 rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft">
          <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
            <div className="flex items-center gap-2">
              <span className="p-2 rounded-xl bg-forest-50 text-forest-700">
                <TrendingUp className="w-5 h-5" />
              </span>
              <div>
                <h3 className="text-base font-extrabold text-forest-900">
                  Nearby Mandi Price Intelligence
                </h3>
                <p className="text-xs text-charcoal-400">Live wholesale rates across Uttarakhand</p>
              </div>
            </div>

            <NavLink
              to="/market-intelligence"
              className="text-xs font-bold text-forest-700 hover:underline flex items-center gap-1"
            >
              Full Explorer <ChevronRight className="w-3.5 h-3.5" />
            </NavLink>
          </div>

          <div className="mt-4 divide-y divide-charcoal-100">
            {nearbyMandis.map((m) => (
              <div key={m.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-xs font-bold text-forest-900">{m.commodity}</p>
                    <span className="text-[10px] text-charcoal-400 font-medium">
                      ({m.variety})
                    </span>
                  </div>
                  <p className="text-[11px] text-charcoal-500 mt-0.5">
                    {m.mandiName} • {m.district}
                  </p>
                </div>

                <div className="text-right">
                  <p className="text-sm font-black text-charcoal-900">
                    ₹{m.modalPrice.toLocaleString()} / q
                  </p>
                  <span
                    className={`inline-block px-1.5 py-0.2 text-[10px] font-bold rounded ${
                      m.dailyChangePercentage >= 0
                        ? 'text-emerald-700 bg-emerald-50'
                        : 'text-rose-700 bg-rose-50'
                    }`}
                  >
                    {m.dailyChangePercentage >= 0 ? '+' : ''}
                    {m.dailyChangePercentage}%
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 p-3 rounded-2xl bg-charcoal-50 border border-charcoal-100 flex items-center justify-between text-xs">
            <div>
              <span className="text-charcoal-400">Highest Local Rate:</span>{' '}
              <strong className="text-forest-900">Harsil Rajma (₹12,800/q)</strong>
            </div>
            <div>
              <span className="text-charcoal-400">Arrivals:</span>{' '}
              <strong className="text-charcoal-800">Steady (+4.5%)</strong>
            </div>
          </div>
        </div>

        {/* Right: Farm Health & Soil Indicators (6 Cols) */}
        <div className="lg:col-span-6 rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft">
          <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
            <div className="flex items-center gap-2">
              <span className="p-2 rounded-xl bg-forest-50 text-forest-700">
                <Sprout className="w-5 h-5" />
              </span>
              <div>
                <h3 className="text-base font-extrabold text-forest-900">
                  Farm & Soil Health Status
                </h3>
                <p className="text-xs text-charcoal-400">
                  {activeFarm.name} • Soil Health Card: Valid
                </p>
              </div>
            </div>

            <NavLink
              to="/smart-advisor"
              className="text-xs font-bold text-forest-700 hover:underline flex items-center gap-1"
            >
              Advisor Details <ChevronRight className="w-3.5 h-3.5" />
            </NavLink>
          </div>

          {/* Soil Metrics Progress Cards */}
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            <div className="p-3 rounded-xl bg-forest-50/60 border border-forest-100 text-center">
              <p className="text-[10px] uppercase font-bold text-charcoal-400">Soil pH</p>
              <p className="text-lg font-black text-forest-900 mt-1">{activeFarm.soilPh}</p>
              <span className="text-[10px] font-bold text-emerald-700">Optimal (Neutral)</span>
            </div>

            <div className="p-3 rounded-xl bg-forest-50/60 border border-forest-100 text-center">
              <p className="text-[10px] uppercase font-bold text-charcoal-400">Nitrogen (N)</p>
              <p className="text-lg font-black text-forest-900 mt-1">{activeFarm.nitrogen}</p>
              <span className="text-[10px] font-bold text-saffron-700">Medium (kg/ha)</span>
            </div>

            <div className="p-3 rounded-xl bg-forest-50/60 border border-forest-100 text-center">
              <p className="text-[10px] uppercase font-bold text-charcoal-400">Phosphorus (P)</p>
              <p className="text-lg font-black text-forest-900 mt-1">{activeFarm.phosphorus}</p>
              <span className="text-[10px] font-bold text-emerald-700">High (kg/ha)</span>
            </div>

            <div className="p-3 rounded-xl bg-forest-50/60 border border-forest-100 text-center">
              <p className="text-[10px] uppercase font-bold text-charcoal-400">Potassium (K)</p>
              <p className="text-lg font-black text-forest-900 mt-1">{activeFarm.potassium}</p>
              <span className="text-[10px] font-bold text-emerald-700">Adequate</span>
            </div>
          </div>

          {/* Irrigation & Soil Carbon Indicator */}
          <div className="mt-4 p-4 rounded-2xl bg-charcoal-50 border border-charcoal-100 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-charcoal-700">Organic Carbon (OC):</span>
              <span className="font-bold text-forest-900">{activeFarm.organicCarbon}% (Good mountain profile)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-semibold text-charcoal-700">Irrigation Setup:</span>
              <span className="font-bold text-forest-900 uppercase">{activeFarm.irrigationType} System ({activeFarm.waterAvailability} water)</span>
            </div>
            <div className="flex items-center justify-between pt-1 border-t border-charcoal-200/60">
              <span className="font-semibold text-charcoal-700">Next Scheduled Watering:</span>
              <span className="font-bold text-emerald-700">Tomorrow, 06:00 AM (Drip Cycle)</span>
            </div>
          </div>
        </div>
      </div>

      {/* ================= 5. RECENT ACTIVITIES & WEATHER WARNINGS ================= */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Recent Activity Feed (7 Cols) */}
        <div className="lg:col-span-7 rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft">
          <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
            <h3 className="text-base font-extrabold text-forest-900">
              Recent Field & Advisory Activities
            </h3>
            <span className="text-xs text-charcoal-400">Updated in real time</span>
          </div>

          <div className="mt-4 space-y-3">
            <div className="p-3 rounded-2xl bg-charcoal-50 border border-charcoal-100 flex items-start gap-3">
              <div className="p-2 rounded-xl bg-forest-100 text-forest-800 shrink-0">
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-bold text-forest-900">AI Crop Plan Generated</p>
                  <span className="text-[10px] text-charcoal-400">Today, 09:45 AM</span>
                </div>
                <p className="text-[11px] text-charcoal-600 mt-0.5">
                  Top recommendation: Aromatic Basmati Paddy (96% fit) for Shivalik Plot A.
                </p>
              </div>
            </div>

            <div className="p-3 rounded-2xl bg-charcoal-50 border border-charcoal-100 flex items-start gap-3">
              <div className="p-2 rounded-xl bg-emerald-100 text-emerald-800 shrink-0">
                <Bug className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-bold text-forest-900">Pest & Disease Advisory</p>
                  <span className="text-[10px] text-charcoal-400">Today, 11:20 AM</span>
                </div>
                <p className="text-[11px] text-charcoal-600 mt-0.5">
                  Analyzed foliar blast symptoms in Finger Millet. Prescribed Trichoderma viride and organic aeration.
                </p>
              </div>
            </div>

            <div className="p-3 rounded-2xl bg-charcoal-50 border border-charcoal-100 flex items-start gap-3">
              <div className="p-2 rounded-xl bg-saffron-100 text-saffron-900 shrink-0">
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-bold text-forest-900">Harvest Outcome Validated</p>
                  <span className="text-[10px] text-charcoal-400">28 Oct 2026</span>
                </div>
                <p className="text-[11px] text-charcoal-600 mt-0.5">
                  Basmati yield of 23.2 q/acre recorded against AI predicted 22.5 q/acre (+3.1% variance).
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Priority Alerts & Notifications (5 Cols) */}
        <div className="lg:col-span-5 rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft">
          <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
            <h3 className="text-base font-extrabold text-forest-900">
              Active Alerts & Weather Warnings
            </h3>
            <span className="w-2.5 h-2.5 rounded-full bg-saffron-500 animate-ping" />
          </div>

          <div className="mt-4 space-y-3">
            {weather.alerts.map((alert, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-2xl bg-amber-50/70 border border-amber-200 text-xs text-amber-950 font-medium space-y-1"
              >
                <div className="flex items-center gap-1.5 font-bold text-amber-900">
                  <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                  <span>Weather Advisory Alert #{idx + 1}</span>
                </div>
                <p className="text-[11px] leading-relaxed text-amber-900/90">{alert}</p>
              </div>
            ))}

            <div className="p-3.5 rounded-2xl bg-emerald-50/70 border border-emerald-200 text-xs text-emerald-950 font-medium space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-emerald-900">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>e-NAM Mandi Price Spike</span>
              </div>
              <p className="text-[11px] leading-relaxed text-emerald-900/90">
                Basmati Paddy prices in Dehradun APMC moved up +3.8% today (₹3,850/q). Good selling opportunity.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
