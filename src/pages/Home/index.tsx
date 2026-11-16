import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { PublicNavbar } from './PublicNavbar';
import { PublicFooter } from './PublicFooter';
import {
  Sprout,
  Sparkles,
  Bug,
  TrendingUp,
  CloudSun,
  MapPin,
  Bot,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Cpu,
  BarChart3,
  Calendar,
  Satellite,
  Search,
  ExternalLink,
  ChevronRight,
  PhoneCall,
  Award
} from 'lucide-react';
import { uttarakhandDistricts, demoMandiPrices } from '../../data/demoData';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [quickDistrict, setQuickDistrict] = useState('Dehradun');
  const [quickCrop, setQuickCrop] = useState('Basmati Rice');

  return (
    <div className="min-h-screen bg-kisan-bg text-charcoal-900 flex flex-col selection:bg-forest-100 selection:text-forest-900">
      <PublicNavbar onOpenAuth={() => navigate('/dashboard')} />

      {/* ===================== HERO SECTION ===================== */}
      <section className="relative min-h-[92vh] flex items-center pt-24 pb-16 overflow-hidden">
        {/* Background Image with Rich Forest Gradient Overlay */}
        <div className="absolute inset-0 z-0">
          <img
            src="/hero-bg.jpg"
            alt="Uttarakhand Himalayan Terrace Agricultural Fields"
            className="w-full h-full object-cover object-center scale-105 animate-soft-pulse duration-[20000ms]"
          />
          {/* Deep Forest Gradient Overlays for Supreme Contrast & Readability */}
          <div className="absolute inset-0 bg-gradient-to-r from-forest-950/95 via-forest-950/80 to-forest-900/60" />
          <div className="absolute inset-0 bg-gradient-to-t from-forest-950 via-transparent to-forest-950/50" />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full py-12">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left Column: Vision & CTAs */}
            <div className="lg:col-span-7 text-white space-y-6">
              {/* Regional Focus Pill */}
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-forest-800/80 border border-forest-600/50 text-forest-100 text-xs font-semibold backdrop-blur-md shadow-lg">
                <span className="w-2 h-2 rounded-full bg-saffron-400 animate-ping" />
                <span className="text-saffron-300 font-bold">Uttarakhand Pioneer Focus</span>
                <span className="text-forest-300">•</span>
                <span>All-India Scalable Architecture</span>
              </div>

              {/* Main Headline */}
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black tracking-tight leading-[1.12]">
                Know Your Land.{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-saffron-300 via-saffron-400 to-amber-200">
                  Grow Smarter.
                </span>{' '}
                Earn Better.
              </h1>

              {/* Sub-headline */}
              <p className="text-base sm:text-lg text-forest-100/90 font-normal leading-relaxed max-w-2xl">
                KisanMitra empowers Indian farmers with <span className="text-saffron-300 font-semibold">Explainable AI</span> crop recommendations, tri-model ensemble intelligence (Fuzzy Logic + Bayesian + Decision Trees), expert pest & disease advisory, and live mandi analytics.
              </p>

              {/* Trust Badges */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 text-xs text-forest-200">
                <div className="flex items-center gap-2 p-2.5 rounded-xl bg-forest-900/60 border border-forest-800/80 backdrop-blur-md">
                  <Cpu className="w-4 h-4 text-saffron-400 shrink-0" />
                  <span>3-Expert Ensemble</span>
                </div>
                <div className="flex items-center gap-2 p-2.5 rounded-xl bg-forest-900/60 border border-forest-800/80 backdrop-blur-md">
                  <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Explainable AI (XAI)</span>
                </div>
                <div className="flex items-center gap-2 p-2.5 rounded-xl bg-forest-900/60 border border-forest-800/80 backdrop-blur-md">
                  <Satellite className="w-4 h-4 text-sky-400 shrink-0" />
                  <span>Remote Sensing Ready</span>
                </div>
              </div>

              {/* CTA Action Buttons */}
              <div className="pt-4 flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
                <NavLink
                  to="/dashboard"
                  className="inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-2xl font-black text-sm bg-saffron-500 hover:bg-saffron-400 text-charcoal-900 shadow-xl shadow-saffron-500/30 transition-all hover:scale-[1.02] active:scale-95"
                >
                  <Sprout className="w-4 h-4" />
                  <span>Launch Farmer Portal</span>
                  <ArrowRight className="w-4 h-4" />
                </NavLink>

                <NavLink
                  to="/crop-recommendation"
                  className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl font-bold text-sm bg-forest-900/80 hover:bg-forest-800 text-white border border-forest-700/60 transition-all backdrop-blur-md"
                >
                  <Sparkles className="w-4 h-4 text-saffron-400" />
                  <span>Test AI Recommendation</span>
                </NavLink>
              </div>
            </div>

            {/* Right Column: Interactive Quick Decision Preview Card */}
            <div className="lg:col-span-5">
              <div className="rounded-3xl bg-white/95 backdrop-blur-xl border border-white/40 shadow-2xl p-6 sm:p-7 text-charcoal-900 space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-charcoal-100">
                  <div className="flex items-center gap-2">
                    <span className="p-2 rounded-xl bg-forest-50 text-forest-700">
                      <Sparkles className="w-5 h-5" />
                    </span>
                    <div>
                      <h3 className="text-sm font-extrabold text-forest-900">
                        Quick Farm Intelligence
                      </h3>
                      <p className="text-[11px] text-charcoal-400">
                        Instant regional suitability & mandi check
                      </p>
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-forest-100 text-forest-900">
                    Live Demo
                  </span>
                </div>

                {/* District Selector */}
                <div>
                  <label className="block text-xs font-bold text-charcoal-700 mb-1.5">
                    Select Farm District (Uttarakhand)
                  </label>
                  <select
                    value={quickDistrict}
                    onChange={(e) => setQuickDistrict(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 bg-charcoal-50 text-xs font-semibold text-charcoal-800 focus:outline-none focus:ring-2 focus:ring-forest-600 focus:bg-white"
                  >
                    {uttarakhandDistricts.map((d) => (
                      <option key={d.id} value={d.name}>
                        {d.name} ({d.agroZone})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Crop Interest */}
                <div>
                  <label className="block text-xs font-bold text-charcoal-700 mb-1.5">
                    Target Crop of Interest
                  </label>
                  <select
                    value={quickCrop}
                    onChange={(e) => setQuickCrop(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 bg-charcoal-50 text-xs font-semibold text-charcoal-800 focus:outline-none focus:ring-2 focus:ring-forest-600 focus:bg-white"
                  >
                    <option value="Basmati Rice">Basmati Rice (Pusa 1509)</option>
                    <option value="Finger Millet (Mandua)">Finger Millet / Mandua (VL 352)</option>
                    <option value="Kidney Beans (Rajma)">Harsil Rajma (Chitra)</option>
                    <option value="Wheat">Wheat (Sharbati)</option>
                    <option value="Tomato">Off-season Tomato (Himsona)</option>
                    <option value="Apple">Temperate Apple (Royal Delicious)</option>
                  </select>
                </div>

                {/* Instant Assessment Output Box */}
                <div className="p-4 rounded-2xl bg-forest-50/70 border border-forest-100/90 space-y-2.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-forest-900">Regional Suitability Index:</span>
                    <span className="font-black text-forest-700 px-2 py-0.5 rounded-md bg-white border border-forest-200">
                      94% (Very High)
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-forest-900">Avg. Mandi Realization:</span>
                    <span className="font-black text-charcoal-900">₹3,850 / Quintal</span>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-forest-900">Recommended Sowing Window:</span>
                    <span className="font-semibold text-forest-800">15 June - 05 July</span>
                  </div>

                  <p className="text-[11px] text-charcoal-500 leading-snug pt-1 border-t border-forest-200/50">
                    💡 Ideal soil pH (6.5–7.2) and agro-climatic valley temperature profile in {quickDistrict}.
                  </p>
                </div>

                {/* Action button */}
                <button
                  onClick={() => navigate('/crop-recommendation')}
                  className="w-full py-3 rounded-xl font-extrabold text-xs bg-forest-900 hover:bg-forest-800 text-white transition-all shadow-md flex items-center justify-center gap-2"
                >
                  <span>Run Complete Multi-Step AI Analysis</span>
                  <ChevronRight className="w-4 h-4 text-saffron-400" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===================== ABOUT SECTION ===================== */}
      <section id="about" className="py-20 bg-white border-b border-charcoal-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center space-y-4">
            <span className="px-3.5 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-forest-50 text-forest-800 border border-forest-200">
              Why KisanMitra
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-forest-900 tracking-tight">
              Bridging the Agricultural Intelligence Gap with Explainable AI
            </h2>
            <p className="text-sm sm:text-base text-charcoal-500 leading-relaxed">
              Traditional crop choices often rely on hearsay, outdated habits, or single-point predictions that fail to explain why a recommendation was made. KisanMitra combines three distinct AI paradigms into a transparent ensemble that farmers can trust.
            </p>
          </div>

          <div className="mt-14 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-7 rounded-3xl bg-kisan-bg border border-charcoal-100 hover:border-forest-200 transition-all shadow-soft">
              <div className="w-12 h-12 rounded-2xl bg-forest-900 text-saffron-400 flex items-center justify-center mb-5">
                <Cpu className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-forest-900">Hybrid AI Ensemble</h3>
              <p className="mt-2 text-xs text-charcoal-500 leading-relaxed">
                Rather than relying on a single black-box neural net, we synthesize predictions from Fuzzy Logic (agronomic boundaries), Gaussian Naive Bayes (climate likelihoods), and Decision Trees (empirical thresholds).
              </p>
            </div>

            <div className="p-7 rounded-3xl bg-kisan-bg border border-charcoal-100 hover:border-forest-200 transition-all shadow-soft">
              <div className="w-12 h-12 rounded-2xl bg-forest-900 text-saffron-400 flex items-center justify-center mb-5">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-forest-900">Explainable Decisions</h3>
              <p className="mt-2 text-xs text-charcoal-500 leading-relaxed">
                Every suggestion comes with transparent feature contributions. You see exactly how soil nitrogen, elevation, market price, water availability, and rainfall determined the final ranking.
              </p>
            </div>

            <div className="p-7 rounded-3xl bg-kisan-bg border border-charcoal-100 hover:border-forest-200 transition-all shadow-soft">
              <div className="w-12 h-12 rounded-2xl bg-forest-900 text-saffron-400 flex items-center justify-center mb-5">
                <MapPin className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-forest-900">Deep Regional Grounding</h3>
              <p className="mt-2 text-xs text-charcoal-500 leading-relaxed">
                Starting with all 13 diverse hill and valley districts of Uttarakhand, the platform adapts to altitude variations (200m to 3,500m), terrace soil types, and regional cash crops like Mandua and Harsil Rajma.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ===================== CORE FEATURES GRID ===================== */}
      <section id="features" className="py-20 bg-forest-50/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-12">
            <div>
              <span className="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-forest-100 text-forest-900">
                Complete AgriTech Suite
              </span>
              <h2 className="text-3xl font-extrabold text-forest-900 tracking-tight mt-2">
                Every Tool a Modern Indian Farmer Needs
              </h2>
            </div>
            <NavLink
              to="/dashboard"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-forest-800 hover:text-forest-900 group"
            >
              <span>Explore All 14 Dedicated Modules</span>
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </NavLink>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div className="p-6 rounded-2xl bg-white border border-charcoal-100 shadow-soft hover:shadow-soft-lg transition-all group">
              <div className="w-10 h-10 rounded-xl bg-forest-50 text-forest-700 flex items-center justify-center mb-4 group-hover:bg-forest-900 group-hover:text-saffron-400 transition-colors">
                <Sparkles className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-forest-900">
                Hybrid AI Crop Recommendation
              </h3>
              <p className="mt-1.5 text-xs text-charcoal-500 leading-relaxed">
                5-step interactive wizard factoring soil NPK, pH, elevation, water, and budget with What-If scenario simulations.
              </p>
              <NavLink
                to="/crop-recommendation"
                className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-forest-700 hover:underline"
              >
                Open Wizard <ChevronRight className="w-3.5 h-3.5" />
              </NavLink>
            </div>

            {/* Feature 2 */}
            <div className="p-6 rounded-2xl bg-white border border-charcoal-100 shadow-soft hover:shadow-soft-lg transition-all group">
              <div className="w-10 h-10 rounded-xl bg-forest-50 text-forest-700 flex items-center justify-center mb-4 group-hover:bg-forest-900 group-hover:text-saffron-400 transition-colors">
                <Bug className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-forest-900">
                Pest & Disease Advisory
              </h3>
              <p className="mt-1.5 text-xs text-charcoal-500 leading-relaxed">
                Rule-based and agronomic diagnostic intelligence for foliar blast, rust, stem borer, and soil nutrient deficiencies with organic IPM remedies.
              </p>
              <NavLink
                to="/advisory"
                className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-forest-700 hover:underline"
              >
                Get Advisory <ChevronRight className="w-3.5 h-3.5" />
              </NavLink>
            </div>

            {/* Feature 3 */}
            <div className="p-6 rounded-2xl bg-white border border-charcoal-100 shadow-soft hover:shadow-soft-lg transition-all group">
              <div className="w-10 h-10 rounded-xl bg-forest-50 text-forest-700 flex items-center justify-center mb-4 group-hover:bg-forest-900 group-hover:text-saffron-400 transition-colors">
                <TrendingUp className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-forest-900">
                Mandi & Profitability Intelligence
              </h3>
              <p className="mt-1.5 text-xs text-charcoal-500 leading-relaxed">
                Live mandi prices from Uttarakhand APMC yards, historical price charts, and an interactive cultivation cost & profit calculator.
              </p>
              <NavLink
                to="/market-intelligence"
                className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-forest-700 hover:underline"
              >
                Explore Mandis <ChevronRight className="w-3.5 h-3.5" />
              </NavLink>
            </div>

            {/* Feature 4 */}
            <div className="p-6 rounded-2xl bg-white border border-charcoal-100 shadow-soft hover:shadow-soft-lg transition-all group">
              <div className="w-10 h-10 rounded-xl bg-forest-50 text-forest-700 flex items-center justify-center mb-4 group-hover:bg-forest-900 group-hover:text-saffron-400 transition-colors">
                <CloudSun className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-forest-900">
                Agricultural Weather & Sowing Windows
              </h3>
              <p className="mt-1.5 text-xs text-charcoal-500 leading-relaxed">
                7-day localized forecast, rain probability thresholds, frost alerts, and optimal spraying window advisories.
              </p>
              <NavLink
                to="/weather"
                className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-forest-700 hover:underline"
              >
                Check Forecast <ChevronRight className="w-3.5 h-3.5" />
              </NavLink>
            </div>

            {/* Feature 5 */}
            <div className="p-6 rounded-2xl bg-white border border-charcoal-100 shadow-soft hover:shadow-soft-lg transition-all group">
              <div className="w-10 h-10 rounded-xl bg-forest-50 text-forest-700 flex items-center justify-center mb-4 group-hover:bg-forest-900 group-hover:text-saffron-400 transition-colors">
                <Bot className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-forest-900">
                RAG Conversational Assistant
              </h3>
              <p className="mt-1.5 text-xs text-charcoal-500 leading-relaxed">
                Context-aware agricultural knowledge agent citing ICAR, GBPUAT, and state advisory manuals with document repository management.
              </p>
              <NavLink
                to="/ai-assistant"
                className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-forest-700 hover:underline"
              >
                Ask Assistant <ChevronRight className="w-3.5 h-3.5" />
              </NavLink>
            </div>

            {/* Feature 6 */}
            <div className="p-6 rounded-2xl bg-white border border-charcoal-100 shadow-soft hover:shadow-soft-lg transition-all group">
              <div className="w-10 h-10 rounded-xl bg-forest-50 text-forest-700 flex items-center justify-center mb-4 group-hover:bg-forest-900 group-hover:text-saffron-400 transition-colors">
                <MapPin className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-forest-900">
                District Geo-Intelligence & Rotation
              </h3>
              <p className="mt-1.5 text-xs text-charcoal-500 leading-relaxed">
                Comprehensive data across 13 Uttarakhand districts, agro-climatic zones, and multi-season crop rotation cycles.
              </p>
              <NavLink
                to="/region-intelligence"
                className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-forest-700 hover:underline"
              >
                View Map <ChevronRight className="w-3.5 h-3.5" />
              </NavLink>
            </div>
          </div>
        </div>
      </section>

      {/* ===================== HOW IT WORKS SECTION ===================== */}
      <section id="how-it-works" className="py-20 bg-white border-b border-charcoal-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mx-auto text-center space-y-3 mb-16">
            <span className="px-3.5 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-saffron-100 text-saffron-900 border border-saffron-200">
              Simple 4-Step Journey
            </span>
            <h2 className="text-3xl font-extrabold text-forest-900 tracking-tight">
              From Soil Profile to Market Profit
            </h2>
            <p className="text-sm text-charcoal-500">
              How KisanMitra guides you through every milestone of the agricultural season
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
            <div className="p-6 rounded-2xl bg-kisan-bg border border-charcoal-100 relative">
              <div className="w-10 h-10 rounded-xl bg-forest-900 text-white font-black text-sm flex items-center justify-center mb-4">
                01
              </div>
              <h4 className="text-base font-bold text-forest-900">Profile Land & Soil</h4>
              <p className="mt-2 text-xs text-charcoal-500 leading-relaxed">
                Register your field coordinates, soil test card metrics (NPK, pH, Organic Carbon), irrigation type, and budget.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-kisan-bg border border-charcoal-100 relative">
              <div className="w-10 h-10 rounded-xl bg-forest-900 text-saffron-400 font-black text-sm flex items-center justify-center mb-4">
                02
              </div>
              <h4 className="text-base font-bold text-forest-900">Run Hybrid AI Ensemble</h4>
              <p className="mt-2 text-xs text-charcoal-500 leading-relaxed">
                Fuzzy Logic, Bayesian Likelihood, and Decision Trees evaluate climate and market data to rank top compatible crops.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-kisan-bg border border-charcoal-100 relative">
              <div className="w-10 h-10 rounded-xl bg-forest-900 text-white font-black text-sm flex items-center justify-center mb-4">
                03
              </div>
              <h4 className="text-base font-bold text-forest-900">Execute Field Actions</h4>
              <p className="mt-2 text-xs text-charcoal-500 leading-relaxed">
                Follow sowing calendars, monitor weather risks, schedule precision irrigation, and scan leaves for early pest prevention.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-kisan-bg border border-charcoal-100 relative">
              <div className="w-10 h-10 rounded-xl bg-forest-900 text-saffron-400 font-black text-sm flex items-center justify-center mb-4">
                04
              </div>
              <h4 className="text-base font-bold text-forest-900">Harvest & Continuous Learning</h4>
              <p className="mt-2 text-xs text-charcoal-500 leading-relaxed">
                Sell at optimal mandi rates, report actual yields, and contribute to the closed-loop farmer feedback validation pipeline.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ===================== CALL TO ACTION BANNER ===================== */}
      <section className="py-16 bg-gradient-to-br from-forest-950 via-forest-900 to-forest-950 text-white relative overflow-hidden">
        <div className="absolute right-0 bottom-0 opacity-10 pointer-events-none">
          <Sprout className="w-96 h-96 text-white" />
        </div>

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6 relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-forest-800/80 border border-forest-700 text-xs text-saffron-300 font-bold">
            <Award className="w-3.5 h-3.5" />
            National Hackathon Ready • Production Frontend
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight leading-tight">
            Ready to Empower Indian Agriculture with AI?
          </h2>

          <p className="text-sm sm:text-base text-forest-200 max-w-2xl mx-auto leading-relaxed">
            Experience the complete authenticated farmer portal with multi-step wizards, interactive Recharts visualizations, Leaflet geo-intelligence, and computer vision diagnosis.
          </p>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-4">
            <NavLink
              to="/dashboard"
              className="w-full sm:w-auto px-8 py-3.5 rounded-2xl font-black text-sm bg-saffron-500 hover:bg-saffron-400 text-charcoal-900 shadow-xl shadow-saffron-500/20 transition-all hover:scale-105 active:scale-95"
            >
              Enter Dashboard Now
            </NavLink>
            <NavLink
              to="/crop-recommendation"
              className="w-full sm:w-auto px-8 py-3.5 rounded-2xl font-bold text-sm bg-forest-800/80 hover:bg-forest-700 text-white border border-forest-600 transition-all"
            >
              Explore AI Crop Recommender
            </NavLink>
          </div>
        </div>
      </section>

      <PublicFooter />
    </div>
  );
};
