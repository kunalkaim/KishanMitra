import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { FarmerFeedback } from '../../types';
import {
  MessageSquareHeart,
  Star,
  CheckCircle2,
  AlertTriangle,
  Upload,
  Calendar,
  Layers,
  Sparkles,
  BarChart3,
  TrendingUp,
  Info
} from 'lucide-react';

export const FeedbackPage: React.FC = () => {
  const { activeFarm, feedbacks, addFeedback, showToast } = useApp();

  const [activeTab, setActiveTab] = useState<'report' | 'history' | 'analytics'>('report');

  // Form State
  const [cropCultivated, setCropCultivated] = useState('Basmati Rice (Pusa 1509)');
  const [followedRecommendation, setFollowedRecommendation] = useState<'Yes' | 'Partially' | 'No'>('Yes');
  const [sowingDate, setSowingDate] = useState('2026-06-15');
  const [harvestDate, setHarvestDate] = useState('2026-10-25');
  const [actualYield, setActualYield] = useState(23.5);
  const [predictedYield, setPredictedYield] = useState(22.5);
  const [actualCost, setActualCost] = useState(23800);
  const [estimatedCost, setEstimatedCost] = useState(24500);
  const [actualPrice, setActualPrice] = useState(3920);
  const [estimatedPrice, setEstimatedPrice] = useState(3850);
  const [problems, setProblems] = useState<string[]>(['Minor stem borer']);
  const [rating, setRating] = useState(5);
  const [notes, setNotes] = useState('Excellent result with early drip irrigation scheduling and recommended Pusa 1509 cultivar.');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    addFeedback({
      farmId: activeFarm.id,
      farmName: activeFarm.name,
      cropCultivated,
      followedRecommendation,
      sowingDate,
      harvestDate,
      actualYield,
      predictedYield,
      actualCost,
      estimatedCost,
      actualSellingPrice: actualPrice,
      estimatedSellingPrice: estimatedPrice,
      problemsEncountered: problems,
      rating,
      notes,
    });

    setActiveTab('history');
  };

  const yieldVariance = Math.round(((actualYield - predictedYield) / predictedYield) * 100);

  return (
    <div className="space-y-6 pb-16 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-charcoal-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-xs font-bold text-forest-800 mb-1.5">
            <MessageSquareHeart className="w-3.5 h-3.5 text-rose-500" />
            <span>Closed-Loop Outcome Reporting</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
            Farmer Harvest Feedback & Outcomes
          </h1>
          <p className="text-xs text-charcoal-400 mt-1">
            Report your real harvest yields and financial outcomes to validate and strengthen regional AI model accuracy
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center p-1 bg-charcoal-100 rounded-2xl text-xs font-bold">
          <button
            onClick={() => setActiveTab('report')}
            className={`px-4 py-2 rounded-xl transition-all ${
              activeTab === 'report' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            Report Harvest
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 rounded-xl transition-all ${
              activeTab === 'history' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            Outcome History ({feedbacks.length})
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-2 rounded-xl transition-all ${
              activeTab === 'analytics' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            Validation Pipeline
          </button>
        </div>
      </div>

      {/* ================= TAB 1: REPORT HARVEST FORM ================= */}
      {activeTab === 'report' && (
        <form onSubmit={handleSubmit} className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-8 shadow-soft space-y-6 text-xs animate-fade-in">
          <div>
            <h3 className="text-base font-extrabold text-forest-900">
              Harvest Outcome & Performance Reporting
            </h3>
            <p className="text-charcoal-400">Field: {activeFarm.name} ({activeFarm.size} Acres, {activeFarm.district})</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">Crop Cultivated</label>
              <input
                type="text"
                required
                value={cropCultivated}
                onChange={(e) => setCropCultivated(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 font-semibold focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Did you follow KisanMitra's AI Recommendation?
              </label>
              <select
                value={followedRecommendation}
                onChange={(e) => setFollowedRecommendation(e.target.value as any)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 font-semibold focus:outline-none focus:ring-2 focus:ring-forest-600"
              >
                <option value="Yes">Yes, fully followed cultivar & irrigation advice</option>
                <option value="Partially">Partially followed (adjusted fertilizer or dates)</option>
                <option value="No">No, planted alternate choice</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">Actual Sowing Date</label>
              <input
                type="date"
                value={sowingDate}
                onChange={(e) => setSowingDate(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 font-semibold focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">Actual Harvest Date</label>
              <input
                type="date"
                value={harvestDate}
                onChange={(e) => setHarvestDate(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 font-semibold focus:outline-none"
              />
            </div>
          </div>

          {/* Actual vs Predicted Yield & Financials */}
          <div className="p-4 rounded-2xl bg-forest-50/60 border border-forest-100 space-y-4">
            <h4 className="font-extrabold text-forest-900 text-xs uppercase tracking-wider">
              Comparison: Actual vs AI Predicted Yield & Financials
            </h4>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-charcoal-600 font-bold mb-1">Actual Yield (q/ac)</label>
                <input
                  type="number"
                  step="0.1"
                  value={actualYield}
                  onChange={(e) => setActualYield(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-1.5 rounded-lg border border-charcoal-200 font-bold"
                />
              </div>

              <div>
                <label className="block text-charcoal-600 font-bold mb-1">Predicted Yield (q/ac)</label>
                <input
                  type="number"
                  step="0.1"
                  value={predictedYield}
                  onChange={(e) => setPredictedYield(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-1.5 rounded-lg border border-charcoal-200 font-bold bg-white"
                />
              </div>

              <div>
                <label className="block text-charcoal-600 font-bold mb-1">Selling Rate (₹/q)</label>
                <input
                  type="number"
                  value={actualPrice}
                  onChange={(e) => setActualPrice(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-1.5 rounded-lg border border-charcoal-200 font-bold"
                />
              </div>
            </div>
          </div>

          {/* Star Rating */}
          <div>
            <label className="block font-bold text-charcoal-700 mb-1.5">
              Overall Recommendation Utility Rating
            </label>
            <div className="flex items-center gap-1.5">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  className="p-1 hover:scale-110 transition-transform"
                >
                  <Star
                    className={`w-6 h-6 ${
                      rating >= star ? 'text-saffron-500 fill-saffron-500' : 'text-charcoal-200'
                    }`}
                  />
                </button>
              ))}
              <span className="ml-2 font-bold text-forest-900">{rating} out of 5 Stars</span>
            </div>
          </div>

          {/* Written Feedback */}
          <div>
            <label className="block font-bold text-charcoal-700 mb-1">
              Field Observations & Problems Encountered
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Describe pest incidents, moisture issues, or mandi price negotiation outcomes..."
              className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 font-semibold focus:outline-none focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              className="px-6 py-3 rounded-2xl font-bold text-xs bg-forest-900 hover:bg-forest-800 text-white shadow-md active:scale-95 flex items-center gap-2"
            >
              <CheckCircle2 className="w-4 h-4 text-saffron-400" />
              <span>Submit Verified Outcome for Validation</span>
            </button>
          </div>
        </form>
      )}

      {/* ================= TAB 2: OUTCOME HISTORY ================= */}
      {activeTab === 'history' && (
        <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-8 shadow-soft space-y-4 animate-fade-in text-xs">
          <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
            <div>
              <h3 className="text-base font-extrabold text-forest-900">
                Historical Harvest Outcomes
              </h3>
              <p className="text-charcoal-400">Audited farmer performance records</p>
            </div>
            <span className="font-bold text-forest-800 bg-forest-50 px-3 py-1 rounded-full">
              {feedbacks.length} Submissions
            </span>
          </div>

          <div className="space-y-4">
            {feedbacks.map((fb) => (
              <div
                key={fb.id}
                className="p-5 rounded-2xl bg-charcoal-50/70 border border-charcoal-100 space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <h4 className="font-extrabold text-forest-900 text-sm">{fb.cropCultivated}</h4>
                    <p className="text-charcoal-400 text-[11px]">{fb.farmName} • Submitted on {fb.createdAt}</p>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-forest-100 text-forest-900">
                      Followed: {fb.followedRecommendation}
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                      {fb.status}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                  <div className="p-2.5 rounded-xl bg-white border border-charcoal-100">
                    <span className="text-[10px] text-charcoal-400 block font-bold">Actual Yield</span>
                    <strong className="text-forest-900">{fb.actualYield} q/ac</strong>
                  </div>
                  <div className="p-2.5 rounded-xl bg-white border border-charcoal-100">
                    <span className="text-[10px] text-charcoal-400 block font-bold">Predicted Yield</span>
                    <strong className="text-charcoal-700">{fb.predictedYield} q/ac</strong>
                  </div>
                  <div className="p-2.5 rounded-xl bg-white border border-charcoal-100">
                    <span className="text-[10px] text-charcoal-400 block font-bold">Actual Rate</span>
                    <strong className="text-forest-900">₹{fb.actualSellingPrice}/q</strong>
                  </div>
                  <div className="p-2.5 rounded-xl bg-white border border-charcoal-100">
                    <span className="text-[10px] text-charcoal-400 block font-bold">Rating</span>
                    <strong className="text-saffron-600">{fb.rating} ★</strong>
                  </div>
                </div>

                <p className="text-charcoal-600 italic text-[11px]">"{fb.notes}"</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ================= TAB 3: VALIDATION PIPELINE ================= */}
      {activeTab === 'analytics' && (
        <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-8 shadow-soft space-y-5 animate-fade-in text-xs">
          <div className="flex items-center justify-between pb-4 border-b border-charcoal-100">
            <div>
              <h3 className="text-base font-extrabold text-forest-900">
                AI Continuous Learning & Model Validation Pipeline
              </h3>
              <p className="text-charcoal-400">How feedback data is curated before periodic model updates</p>
            </div>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-900 border border-amber-200">
              Curated Pipeline
            </span>
          </div>

          <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200 flex items-start gap-3 text-amber-950">
            <Info className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <p className="font-bold">Continuous Learning Architecture Notice:</p>
              <p className="text-charcoal-600 text-[11px] leading-relaxed">
                KisanMitra does not blindly retrain models in production upon every individual feedback submission to prevent adversarial drift or statistical contamination. Submissions are pooled into regional validation cohorts, cross-checked against satellite NDVI data, and vetted by agronomic researchers prior to scheduled semi-annual weight retraining.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-forest-50/60 border border-forest-100 space-y-1">
              <span className="text-[10px] uppercase font-bold text-charcoal-400">Total Harvest Reports</span>
              <p className="text-2xl font-black text-forest-900">{feedbacks.length + 184}</p>
              <span className="text-emerald-700 font-semibold text-[11px]">Across 13 districts</span>
            </div>

            <div className="p-4 rounded-2xl bg-forest-50/60 border border-forest-100 space-y-1">
              <span className="text-[10px] uppercase font-bold text-charcoal-400">Mean Yield Accuracy</span>
              <p className="text-2xl font-black text-forest-900">93.8%</p>
              <span className="text-emerald-700 font-semibold text-[11px]">±6.2% mean absolute error</span>
            </div>

            <div className="p-4 rounded-2xl bg-forest-50/60 border border-forest-100 space-y-1">
              <span className="text-[10px] uppercase font-bold text-charcoal-400">Farmer Satisfaction</span>
              <p className="text-2xl font-black text-saffron-600">4.8 / 5.0</p>
              <span className="text-charcoal-500 font-semibold text-[11px]">89% adoption rate</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
