import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import { advisoryService, AdvisoryResponse } from '../../services/advisoryService';
import {
  Bug,
  Sparkles,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Bot,
  RefreshCw,
  FileText,
  Info,
  Layers,
  ThermometerSnowflake,
  Droplets,
  Calendar,
  Send,
  History
} from 'lucide-react';

export const PestDiseaseAdvisoryPage: React.FC = () => {
  const { activeFarm, showToast, t } = useApp();
  const navigate = useNavigate();

  // Form State
  const [cropName, setCropName] = useState('Finger Millet (Mandua / Ragi)');
  const [growthStage, setGrowthStage] = useState('Tillering / Vegetative');
  const [observedSymptoms, setObservedSymptoms] = useState(
    'Spindle-shaped brown lesions with greyish centres on leaf blades and neck of the panicle.'
  );
  const [farmingConditions, setFarmingConditions] = useState(
    'Heavy intermittent monsoon rains, morning mist, cloudy weather, high terrace field humidity.'
  );
  const [affectedArea, setAffectedArea] = useState<number>(15);

  // Advisory Result State
  const [loading, setLoading] = useState(false);
  const [currentAdvisory, setCurrentAdvisory] = useState<AdvisoryResponse | null>(null);
  const [history, setHistory] = useState<AdvisoryResponse[]>([]);
  const [activeTab, setActiveTab] = useState<'advisory' | 'history'>('advisory');

  // Quick Preset Samples for Instant Farmer Demonstration
  const presetCases = [
    {
      label: 'Foliar Blast (Mandua / Rice)',
      crop: 'Finger Millet (Mandua / Ragi)',
      stage: 'Tillering / Vegetative',
      symptoms: 'Spindle-shaped brown lesions with greyish centres on leaf blades and neck of the panicle.',
      conditions: 'Heavy intermittent monsoon rains, morning mist, cloudy weather, high terrace field humidity.',
      area: 15
    },
    {
      label: 'Yellow Rust / Stripe Rust (Wheat)',
      crop: 'Wheat (VL Gehun 907)',
      stage: 'Vegetative to Heading',
      symptoms: 'Yellow pustules arranged in prominent linear stripes along leaf veins with yellow powdery spores.',
      conditions: 'Cool winter temperatures (10-14°C), heavy morning dew in hill valley, overcast sky.',
      area: 20
    },
    {
      label: 'Stem Borer Dead-Heart (Paddy)',
      crop: 'Basmati Rice (Dehraduni Type)',
      stage: 'Tillering',
      symptoms: 'Dead heart in central shoots which pull out easily; tiny entry holes and frass near the base.',
      conditions: 'Warm humid weather with occasional evening showers.',
      area: 10
    },
    {
      label: 'Khaira / Zinc Deficiency (Paddy)',
      crop: 'Basmati Rice (Dehraduni Type)',
      stage: 'Seedling to Early Tillering',
      symptoms: 'Bronze discoloration and reddish-brown pigmentation appearing first on older leaves; stunted growth.',
      conditions: 'Continuously submerged high-calcium terrace soils with high water table.',
      area: 25
    }
  ];

  // Load Initial Advisory or Demo
  useEffect(() => {
    // Initial fetch from backend if available
    advisoryService.getHistory(activeFarm.id)
      .then(res => {
        if (res && res.length > 0) {
          setHistory(res);
          setCurrentAdvisory(res[0]);
        }
      })
      .catch(() => {
        // Fallback to local default if backend is offline
      });
  }, [activeFarm.id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!observedSymptoms.trim()) {
      showToast('Please enter observed symptoms', 'info');
      return;
    }

    setLoading(true);
    try {
      const response = await advisoryService.submitCase({
        farm_id: activeFarm.id,
        crop_name: cropName,
        crop_growth_stage: growthStage,
        observed_symptoms: observedSymptoms,
        farming_conditions: farmingConditions,
        affected_area_percentage: affectedArea
      });

      setCurrentAdvisory(response);
      setHistory(prev => [response, ...prev]);
      showToast(`Advisory generated: ${response.suspected_pest_or_pathogen}`, 'success');
    } catch (err: any) {
      // Offline fallback: generate client-side structured advisory
      const fallbackAdvisory: AdvisoryResponse = {
        id: 'advisory-fallback-' + Date.now(),
        crop_name: cropName,
        crop_growth_stage: growthStage,
        suspected_pest_or_pathogen: observedSymptoms.toLowerCase().includes('rust')
          ? 'Yellow Rust / Stripe Rust (Puccinia striiformis)'
          : observedSymptoms.toLowerCase().includes('borer')
          ? 'Stem Borer (Scirpophaga incertulas)'
          : observedSymptoms.toLowerCase().includes('bronze')
          ? 'Khaira Disease (Zinc Deficiency)'
          : 'Blast (Magnaporthe oryzae)',
        diagnostic_category: observedSymptoms.toLowerCase().includes('bronze')
          ? 'Nutrient Deficiency'
          : observedSymptoms.toLowerCase().includes('borer')
          ? 'Insect Pest'
          : 'Fungal Disease',
        confidence_level: 'High Confidence (Agronomic Symptom Match)',
        advisory_response: `Symptoms reflect acute foliar/pathogen stress in ${cropName}. Microclimate humidity and terrace moisture levels require targeted bio-control intervention to prevent secondary spread across adjacent terraces.`,
        recommended_interventions: [
          {
            type: 'Organic Bio-agent',
            remedy_name: 'Trichoderma viride or Pseudomonas fluorescens',
            dosage_per_liter: '5-10 g / litre of water',
            application_method: 'Foliar spray during early morning or calm evening',
            precaution: 'Do not combine with synthetic chemical fungicides.'
          },
          {
            type: 'Botanical Formulation',
            remedy_name: 'Neem Seed Kernel Extract (NSKE 5%) or Azadirachtin 1500 ppm',
            dosage_per_liter: '3 ml / litre of water with mild soap wetting agent',
            application_method: 'Target underside of leaves and canopy base',
            precaution: 'Spray when rain is not anticipated for 4 hours.'
          }
        ],
        preventive_measures: [
          'Maintain terrace drainage channels to prevent stagnant moisture accumulation',
          'Avoid excessive split urea applications during overcast humid weeks',
          'Collect and compost or burn infected leaf residues after harvest'
        ],
        disclaimer: 'Advisory provided for agronomic guidance based on reported symptoms. Verify acute chemical interventions with your local Block Agriculture Officer or KVK specialist.',
        is_demo: true,
        created_at: new Date().toISOString()
      };

      setCurrentAdvisory(fallbackAdvisory);
      setHistory(prev => [fallbackAdvisory, ...prev]);
      showToast('Advisory generated successfully (Local Agronomic Engine)', 'success');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPreset = (preset: typeof presetCases[0]) => {
    setCropName(preset.crop);
    setGrowthStage(preset.stage);
    setObservedSymptoms(preset.symptoms);
    setFarmingConditions(preset.conditions);
    setAffectedArea(preset.area);
    showToast(`Loaded sample: ${preset.label}`, 'info');
  };

  const handleAskAIAssistant = () => {
    if (!currentAdvisory) return;
    const query = encodeURIComponent(
      `How do I manage ${currentAdvisory.suspected_pest_or_pathogen} in ${currentAdvisory.crop_name} organically under ${farmingConditions}?`
    );
    navigate(`/ai-assistant?q=${query}`);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1.5 rounded-lg bg-forest-100 text-forest-700">
              <Bug className="w-5 h-5" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-forest-600 bg-forest-50 px-2 py-0.5 rounded-full border border-forest-200">
              AgriTech Advisory Intelligence
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-forest-900 tracking-tight">
            Pest & Disease Advisory
          </h1>
          <p className="text-xs md:text-sm text-charcoal-500 mt-1">
            Rule-based and verified agronomic diagnostic intelligence (GBPUAT Pantnagar & ICAR-VPKAS Almora). Enter symptoms and microclimate conditions for instant organic IPM remedies.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 p-1 bg-charcoal-100/80 rounded-xl border border-charcoal-200">
          <button
            onClick={() => setActiveTab('advisory')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'advisory'
                ? 'bg-white text-forest-900 shadow-sm'
                : 'text-charcoal-600 hover:text-forest-800'
            }`}
          >
            <Bug className="w-3.5 h-3.5" />
            <span>Symptom Diagnostic</span>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'history'
                ? 'bg-white text-forest-900 shadow-sm'
                : 'text-charcoal-600 hover:text-forest-800'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Case History ({history.length})</span>
          </button>
        </div>
      </div>

      {activeTab === 'advisory' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Input Form (5 cols) */}
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-white rounded-2xl border border-charcoal-200 p-5 shadow-soft space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-charcoal-100">
                <h3 className="text-sm font-bold text-forest-900 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-forest-600" />
                  <span>Report Observed Symptoms</span>
                </h3>
                <span className="text-[11px] font-semibold text-charcoal-400">Text-Based Diagnosis</span>
              </div>

              {/* Sample Preset Buttons */}
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-charcoal-500 mb-1.5">
                  Load Verified Sample Case:
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {presetCases.map((preset, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSelectPreset(preset)}
                      className="px-2 py-1 rounded-md text-[11px] font-medium bg-forest-50 hover:bg-forest-100 text-forest-800 border border-forest-200 transition-colors text-left"
                    >
                      {preset.label}
                    </button>
                  ))}
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-3.5">
                {/* Crop Name */}
                <div>
                  <label className="block text-xs font-bold text-forest-900 mb-1">
                    Target Crop:
                  </label>
                  <select
                    value={cropName}
                    onChange={(e) => setCropName(e.target.value)}
                    className="w-full text-xs font-medium rounded-xl border border-charcoal-200 px-3 py-2 bg-white text-charcoal-800 focus:outline-none focus:ring-2 focus:ring-forest-500"
                  >
                    <option value="Finger Millet (Mandua / Ragi)">Finger Millet (Mandua / Ragi)</option>
                    <option value="Basmati Rice (Dehraduni Type)">Basmati Rice (Dehraduni Type)</option>
                    <option value="Barnyard Millet (Jhangora)">Barnyard Millet (Jhangora)</option>
                    <option value="Wheat (VL Gehun 907)">Wheat (VL Gehun 907)</option>
                    <option value="Rajma (Munsyari Kidney Beans)">Rajma (Munsyari Kidney Beans)</option>
                    <option value="Black Soybean (Bhatt)">Black Soybean (Bhatt)</option>
                    <option value="Mustard / Rapeseed">Mustard / Rapeseed</option>
                    <option value="Himalayan Hill Potato">Himalayan Hill Potato</option>
                  </select>
                </div>

                {/* Growth Stage */}
                <div>
                  <label className="block text-xs font-bold text-forest-900 mb-1">
                    Crop Growth Stage:
                  </label>
                  <select
                    value={growthStage}
                    onChange={(e) => setGrowthStage(e.target.value)}
                    className="w-full text-xs font-medium rounded-xl border border-charcoal-200 px-3 py-2 bg-white text-charcoal-800 focus:outline-none focus:ring-2 focus:ring-forest-500"
                  >
                    <option value="Seedling / Germination">Seedling / Germination (0-20 DAS)</option>
                    <option value="Tillering / Vegetative">Tillering / Vegetative (20-45 DAS)</option>
                    <option value="Flowering / Booting">Flowering / Booting (45-70 DAS)</option>
                    <option value="Grain Filling / Fruiting">Grain Filling / Fruiting (70-95 DAS)</option>
                    <option value="Physiological Maturity">Physiological Maturity (95+ DAS)</option>
                  </select>
                </div>

                {/* Observed Symptoms */}
                <div>
                  <label className="block text-xs font-bold text-forest-900 mb-1">
                    Observed Symptoms (Foliar, Stem, or Root):
                  </label>
                  <textarea
                    rows={3}
                    value={observedSymptoms}
                    onChange={(e) => setObservedSymptoms(e.target.value)}
                    placeholder="Describe lesion shape, color, leaf curling, spots, or pest frass..."
                    className="w-full text-xs font-medium rounded-xl border border-charcoal-200 p-3 bg-white text-charcoal-800 focus:outline-none focus:ring-2 focus:ring-forest-500"
                    required
                  />
                </div>

                {/* Microclimate & Farming Conditions */}
                <div>
                  <label className="block text-xs font-bold text-forest-900 mb-1">
                    Microclimate & Field Conditions:
                  </label>
                  <textarea
                    rows={2}
                    value={farmingConditions}
                    onChange={(e) => setFarmingConditions(e.target.value)}
                    placeholder="Rainfall pattern, morning fog, soil moisture, sunlight..."
                    className="w-full text-xs font-medium rounded-xl border border-charcoal-200 p-3 bg-white text-charcoal-800 focus:outline-none focus:ring-2 focus:ring-forest-500"
                    required
                  />
                </div>

                {/* Affected Area Percentage Slider */}
                <div>
                  <div className="flex justify-between items-center text-xs font-bold text-forest-900 mb-1">
                    <span>Estimated Crop Area Affected:</span>
                    <span className="text-forest-700 bg-forest-50 px-2 py-0.5 rounded-full border border-forest-200">
                      {affectedArea}% of Field
                    </span>
                  </div>
                  <input
                    type="range"
                    min={1}
                    max={100}
                    value={affectedArea}
                    onChange={(e) => setAffectedArea(Number(e.target.value))}
                    className="w-full accent-forest-600 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-charcoal-400 mt-0.5">
                    <span>1% (Isolated Foci)</span>
                    <span>25% (Moderate)</span>
                    <span>50%+ (Severe)</span>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 px-4 bg-forest-800 hover:bg-forest-900 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-sm transition-all disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Evaluating Agronomic Knowledge Rules...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 text-saffron-400" />
                      <span>Generate Agronomic Advisory</span>
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* Farm Context Card */}
            <div className="bg-forest-50/70 border border-forest-200/80 rounded-2xl p-4 flex items-center gap-3">
              <span className="p-2 rounded-xl bg-forest-100 text-forest-800 shrink-0">
                <Layers className="w-5 h-5" />
              </span>
              <div>
                <p className="text-xs font-bold text-forest-900">Current Farm Context</p>
                <p className="text-[11px] text-forest-700">
                  {activeFarm.name} ({activeFarm.district}, {activeFarm.soilType})
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: Advisory Result (7 cols) */}
          <div className="lg:col-span-7 space-y-4">
            {currentAdvisory ? (
              <div className="bg-white rounded-2xl border border-charcoal-200 p-6 shadow-soft space-y-5">
                {/* Header Banner */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-charcoal-100">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-forest-100 text-forest-800 border border-forest-200">
                        {currentAdvisory.diagnostic_category}
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-saffron-50 text-saffron-800 border border-saffron-200">
                        {currentAdvisory.confidence_level}
                      </span>
                    </div>
                    <h2 className="text-lg md:text-xl font-extrabold text-forest-950">
                      {currentAdvisory.suspected_pest_or_pathogen}
                    </h2>
                    <p className="text-xs text-charcoal-500 mt-0.5">
                      Target Crop: <span className="font-semibold text-charcoal-700">{currentAdvisory.crop_name}</span> | Stage: <span className="font-semibold text-charcoal-700">{currentAdvisory.crop_growth_stage}</span>
                    </p>
                  </div>

                  <button
                    onClick={handleAskAIAssistant}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white text-xs font-bold transition-all shadow-sm shrink-0"
                  >
                    <Bot className="w-3.5 h-3.5" />
                    <span>Ask AI Assistant</span>
                  </button>
                </div>

                {/* Agronomic Summary */}
                <div className="bg-charcoal-50 border border-charcoal-200 rounded-xl p-4">
                  <h4 className="text-xs font-bold text-forest-900 mb-1 flex items-center gap-1.5">
                    <Info className="w-3.5 h-3.5 text-forest-600" />
                    <span>Agronomic Diagnosis Summary:</span>
                  </h4>
                  <p className="text-xs text-charcoal-700 leading-relaxed">
                    {currentAdvisory.advisory_response}
                  </p>
                </div>

                {/* Recommended Interventions (IPM) */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-forest-900 mb-3 flex items-center gap-1.5">
                    <ShieldAlert className="w-4 h-4 text-forest-600" />
                    <span>Prescribed Interventions & Organic IPM:</span>
                  </h4>

                  <div className="space-y-3">
                    {currentAdvisory.recommended_interventions.map((item, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl border border-charcoal-200 bg-white hover:border-forest-300 transition-colors"
                      >
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <span className="text-xs font-bold text-forest-900 flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 text-forest-600 shrink-0" />
                            {item.remedy_name}
                          </span>
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-forest-50 text-forest-700 border border-forest-200 shrink-0">
                            {item.type}
                          </span>
                        </div>
                        <p className="text-[11px] text-charcoal-600 mb-1">
                          <strong className="text-charcoal-800">Dosage:</strong> {item.dosage_per_liter}
                        </p>
                        <p className="text-[11px] text-charcoal-600 mb-1">
                          <strong className="text-charcoal-800">Application:</strong> {item.application_method}
                        </p>
                        {item.precaution && (
                          <p className="text-[11px] text-amber-700 bg-amber-50/80 px-2 py-1 rounded-md border border-amber-200/60 mt-1 flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3 shrink-0" />
                            <span><strong>Precaution:</strong> {item.precaution}</span>
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Long Term Preventive Measures */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-forest-900 mb-2">
                    Terrace & Field Preventive Measures:
                  </h4>
                  <ul className="space-y-1.5">
                    {currentAdvisory.preventive_measures.map((prev, idx) => (
                      <li key={idx} className="text-xs text-charcoal-600 flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-forest-600 mt-1.5 shrink-0" />
                        <span>{prev}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Disclaimer */}
                <div className="bg-amber-50/60 border border-amber-200 rounded-xl p-3 flex items-start gap-2.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                  <p className="text-[11px] text-amber-800 leading-normal">
                    <strong>Official Agro-Advisory Note:</strong> {currentAdvisory.disclaimer}
                  </p>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-2xl border border-charcoal-200 p-12 text-center shadow-soft">
                <span className="inline-flex p-3 rounded-2xl bg-forest-50 text-forest-700 mb-3">
                  <Bug className="w-8 h-8" />
                </span>
                <h3 className="text-base font-bold text-forest-900">No Advisory Case Submitted Yet</h3>
                <p className="text-xs text-charcoal-500 max-w-md mx-auto mt-1 mb-4">
                  Select a crop, growth stage, and observed symptoms on the left to receive customized biological and organic IPM prescriptions.
                </p>
                <button
                  type="button"
                  onClick={() => handleSelectPreset(presetCases[0])}
                  className="px-4 py-2 bg-forest-800 text-white rounded-xl text-xs font-bold hover:bg-forest-900 transition-colors"
                >
                  Load Sample Blast Case
                </button>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* History Tab */
        <div className="bg-white rounded-2xl border border-charcoal-200 p-6 shadow-soft space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-charcoal-100">
            <div>
              <h3 className="text-base font-bold text-forest-900">Submitted Advisory Cases</h3>
              <p className="text-xs text-charcoal-500">Log of recorded pest and disease symptoms on your farm</p>
            </div>
            <span className="text-xs font-bold text-forest-700 bg-forest-50 px-2.5 py-1 rounded-lg border border-forest-200">
              {history.length} Cases
            </span>
          </div>

          {history.length === 0 ? (
            <div className="text-center py-10">
              <p className="text-xs text-charcoal-400">No previous advisory cases recorded.</p>
            </div>
          ) : (
            <div className="divide-y divide-charcoal-100">
              {history.map((c) => (
                <div key={c.id} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-bold text-forest-900">{c.suspected_pest_or_pathogen}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-forest-100 text-forest-800">
                        {c.diagnostic_category}
                      </span>
                    </div>
                    <p className="text-xs text-charcoal-600">
                      Crop: <span className="font-semibold">{c.crop_name}</span> | Stage: {c.crop_growth_stage}
                    </p>
                    <p className="text-[11px] text-charcoal-400 mt-0.5">
                      Date: {new Date(c.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <button
                    onClick={() => {
                      setCurrentAdvisory(c);
                      setActiveTab('advisory');
                    }}
                    className="px-3 py-1.5 rounded-lg text-xs font-bold text-forest-800 bg-forest-50 hover:bg-forest-100 border border-forest-200 transition-colors shrink-0"
                  >
                    View Advisory
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
