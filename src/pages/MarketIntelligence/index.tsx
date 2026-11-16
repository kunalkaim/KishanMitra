import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { demoMandiPrices } from '../../data/demoData';
import {
  TrendingUp,
  DollarSign,
  Calculator,
  Scale,
  Search,
  Filter,
  ArrowUpRight,
  ArrowDownRight,
  AlertCircle,
  CheckCircle2,
  PieChart as PieChartIcon
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  BarChart,
  Bar,
  Legend
} from 'recharts';

export const MarketIntelligencePage: React.FC = () => {
  const { mandiPrices, activeFarm } = useApp();

  // Filters
  const [selectedDistrict, setSelectedDistrict] = useState('All');
  const [searchCommodity, setSearchCommodity] = useState('');
  const [selectedTab, setSelectedTab] = useState<'mandi' | 'calculator' | 'comparison'>('mandi');

  // Profitability Calculator Inputs
  const [calcFarmSize, setCalcFarmSize] = useState(activeFarm.size || 3.5);
  const [calcCrop, setCalcCrop] = useState('Basmati Rice (Pusa 1509)');
  const [calcSeedCost, setCalcSeedCost] = useState(2500);
  const [calcFertilizerCost, setCalcFertilizerCost] = useState(4800);
  const [calcLabourCost, setCalcLabourCost] = useState(6500);
  const [calcIrrigationCost, setCalcIrrigationCost] = useState(2200);
  const [calcMachineryCost, setCalcMachineryCost] = useState(3800);
  const [calcTransportCost, setCalcTransportCost] = useState(1500);
  const [calcExpectedYield, setCalcExpectedYield] = useState(22.5); // quintals per acre
  const [calcSellingPrice, setCalcSellingPrice] = useState(3850); // INR per quintal

  // Dynamic calculations
  const totalCostPerAcre = calcSeedCost + calcFertilizerCost + calcLabourCost + calcIrrigationCost + calcMachineryCost + calcTransportCost;
  const totalCultivationCost = totalCostPerAcre * calcFarmSize;
  const totalProductionQuintals = calcExpectedYield * calcFarmSize;
  const grossRevenue = totalProductionQuintals * calcSellingPrice;
  const netProfit = grossRevenue - totalCultivationCost;
  const profitMarginPercent = grossRevenue > 0 ? Math.round((netProfit / grossRevenue) * 100) : 0;
  const breakEvenPrice = totalProductionQuintals > 0 ? Math.round(totalCultivationCost / totalProductionQuintals) : 0;

  // Filtered mandi prices
  const filteredMandis = mandiPrices.filter((m) => {
    const matchesDist = selectedDistrict === 'All' || m.district.toLowerCase() === selectedDistrict.toLowerCase();
    const matchesCrop = m.commodity.toLowerCase().includes(searchCommodity.toLowerCase()) || m.mandiName.toLowerCase().includes(searchCommodity.toLowerCase());
    return matchesDist && matchesCrop;
  });

  // Mock 30-day historical trend for selected commodity
  const historyTrend = [
    { date: '15 Oct', price: 3620, baseline: 3600 },
    { date: '20 Oct', price: 3680, baseline: 3600 },
    { date: '25 Oct', price: 3710, baseline: 3600 },
    { date: '30 Oct', price: 3740, baseline: 3600 },
    { date: '05 Nov', price: 3790, baseline: 3600 },
    { date: '11 Nov', price: 3850, baseline: 3600 },
  ];

  return (
    <div className="space-y-6 pb-16 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-charcoal-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-xs font-bold text-forest-800 mb-1.5">
            <TrendingUp className="w-3.5 h-3.5 text-saffron-500" />
            <span>e-NAM & APMC Market Analytics</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
            Market & Economic Intelligence
          </h1>
          <p className="text-xs text-charcoal-400 mt-1">
            Real-time APMC wholesale price discovery, multi-crop comparison & dynamic cultivation profitability simulator
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center p-1 bg-charcoal-100 rounded-2xl text-xs font-bold">
          <button
            onClick={() => setSelectedTab('mandi')}
            className={`px-4 py-2 rounded-xl transition-all ${
              selectedTab === 'mandi' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            Mandi Explorer
          </button>
          <button
            onClick={() => setSelectedTab('calculator')}
            className={`px-4 py-2 rounded-xl transition-all ${
              selectedTab === 'calculator' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            Profitability Calculator
          </button>
          <button
            onClick={() => setSelectedTab('comparison')}
            className={`px-4 py-2 rounded-xl transition-all ${
              selectedTab === 'comparison' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            Crop Comparison
          </button>
        </div>
      </div>

      {/* ================= TAB 1: MANDI PRICE EXPLORER ================= */}
      {selectedTab === 'mandi' && (
        <div className="space-y-6 animate-fade-in">
          {/* Search & Filter Bar */}
          <div className="p-4 rounded-2xl bg-white border border-charcoal-100 shadow-soft flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="relative flex-1 w-full">
              <Search className="w-4 h-4 text-charcoal-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search commodity or mandi (e.g. Basmati, Dehradun, Wheat)..."
                value={searchCommodity}
                onChange={(e) => setSearchCommodity(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-xl border border-charcoal-200 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <span className="text-xs font-bold text-charcoal-500 whitespace-nowrap">District:</span>
              <select
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
                className="px-3 py-2 rounded-xl border border-charcoal-200 text-xs font-bold text-charcoal-800 bg-white focus:outline-none"
              >
                <option value="All">All Districts</option>
                <option value="Dehradun">Dehradun</option>
                <option value="Nainital">Nainital</option>
                <option value="Almora">Almora</option>
                <option value="Haridwar">Haridwar</option>
                <option value="Uttarkashi">Uttarkashi</option>
              </select>
            </div>
          </div>

          {/* Mandi Table */}
          <div className="rounded-3xl bg-white border border-charcoal-100 shadow-soft overflow-hidden">
            <div className="p-5 border-b border-charcoal-100 flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-forest-900">
                  Live Mandi Daily Wholesale Quotes
                </h3>
                <p className="text-xs text-charcoal-400">Official APMC prices in ₹ per Quintal (100 kg)</p>
              </div>
              <span className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                Live Agmarknet Sync
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left border-collapse min-w-[700px]">
                <thead>
                  <tr className="border-b border-charcoal-100 bg-charcoal-50/70 text-charcoal-500 font-bold uppercase text-[10px]">
                    <th className="py-3 px-4">Commodity / Variety</th>
                    <th className="py-3 px-4">Mandi & District</th>
                    <th className="py-3 px-4">Modal Price (₹/q)</th>
                    <th className="py-3 px-4">Min - Max Range</th>
                    <th className="py-3 px-4">24h Change</th>
                    <th className="py-3 px-4">Arrival Volume</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-charcoal-100">
                  {filteredMandis.map((m) => (
                    <tr key={m.id} className="hover:bg-forest-50/30 transition-colors">
                      <td className="py-3.5 px-4 font-bold text-forest-900">
                        {m.commodity}
                        <span className="block text-[10px] text-charcoal-400 font-normal">{m.variety}</span>
                      </td>
                      <td className="py-3.5 px-4 font-medium text-charcoal-700">
                        {m.mandiName}
                        <span className="block text-[10px] text-charcoal-400">{m.district}, {m.state}</span>
                      </td>
                      <td className="py-3.5 px-4 font-black text-sm text-forest-900">
                        ₹{m.modalPrice.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 font-medium text-charcoal-600">
                        ₹{m.minPrice.toLocaleString()} - ₹{m.maxPrice.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 font-bold">
                        <span
                          className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded ${
                            m.dailyChangePercentage >= 0
                              ? 'bg-emerald-50 text-emerald-700'
                              : 'bg-rose-50 text-rose-700'
                          }`}
                        >
                          {m.dailyChangePercentage >= 0 ? (
                            <ArrowUpRight className="w-3 h-3" />
                          ) : (
                            <ArrowDownRight className="w-3 h-3" />
                          )}
                          {m.dailyChangePercentage}%
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-charcoal-600 font-medium">
                        {m.arrivalVolumeQuintals.toLocaleString()} q
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Historical Trend Chart */}
          <div className="rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft">
            <div className="flex items-center justify-between pb-4 border-b border-charcoal-100 mb-4">
              <div>
                <h4 className="text-base font-extrabold text-forest-900">
                  30-Day Modal Price Trend: Paddy (Basmati 1509)
                </h4>
                <p className="text-xs text-charcoal-400">Dehradun APMC Mandi price trajectory</p>
              </div>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md">
                +6.3% Over Past 30 Days
              </span>
            </div>

            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historyTrend}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis unit="₹" domain={[3500, 4000]} tick={{ fontSize: 11 }} />
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
                    dataKey="price"
                    name="Modal Price (₹/q)"
                    stroke="#174B35"
                    strokeWidth={3}
                    dot={{ r: 4, fill: '#E8AD45' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* ================= TAB 2: CROP PROFITABILITY CALCULATOR ================= */}
      {selectedTab === 'calculator' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
          {/* Inputs Form (6 Cols) */}
          <div className="lg:col-span-6 rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-7 shadow-soft space-y-4 text-xs">
            <div className="flex items-center gap-2 pb-3 border-b border-charcoal-100">
              <span className="p-2 rounded-xl bg-forest-50 text-forest-700">
                <Calculator className="w-5 h-5" />
              </span>
              <div>
                <h3 className="text-base font-extrabold text-forest-900">
                  Cultivation Cost & Return Inputs
                </h3>
                <p className="text-charcoal-400 text-[11px]">Edit inputs to calculate dynamic net returns</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-bold text-charcoal-700 mb-1">Target Crop</label>
                <select
                  value={calcCrop}
                  onChange={(e) => setCalcCrop(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-charcoal-200 text-xs font-semibold focus:outline-none"
                >
                  <option value="Basmati Rice (Pusa 1509)">Basmati Rice (Pusa 1509)</option>
                  <option value="Finger Millet (Mandua)">Finger Millet / Mandua (VL 352)</option>
                  <option value="Wheat (Sharbati)">Wheat (Sharbati)</option>
                  <option value="Harsil Rajma">Harsil Rajma (Chitra)</option>
                  <option value="Tomato (Himsona)">Off-season Tomato (Himsona)</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-charcoal-700 mb-1">Farm Area (Acres)</label>
                <input
                  type="number"
                  step="0.5"
                  value={calcFarmSize}
                  onChange={(e) => setCalcFarmSize(parseFloat(e.target.value) || 1)}
                  className="w-full px-3 py-2 rounded-xl border border-charcoal-200 text-xs font-semibold focus:outline-none"
                />
              </div>
            </div>

            <p className="font-bold text-forest-900 pt-2 border-t border-charcoal-100">
              Per-Acre Expenditure Breakdown (₹)
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-charcoal-500 text-[11px] mb-1">Seed Cost / ac</label>
                <input
                  type="number"
                  value={calcSeedCost}
                  onChange={(e) => setCalcSeedCost(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-1.5 rounded-lg border border-charcoal-200 font-semibold focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-charcoal-500 text-[11px] mb-1">Fertilizer / ac</label>
                <input
                  type="number"
                  value={calcFertilizerCost}
                  onChange={(e) => setCalcFertilizerCost(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-1.5 rounded-lg border border-charcoal-200 font-semibold focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-charcoal-500 text-[11px] mb-1">Labour Cost / ac</label>
                <input
                  type="number"
                  value={calcLabourCost}
                  onChange={(e) => setCalcLabourCost(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-1.5 rounded-lg border border-charcoal-200 font-semibold focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-charcoal-500 text-[11px] mb-1">Irrigation / ac</label>
                <input
                  type="number"
                  value={calcIrrigationCost}
                  onChange={(e) => setCalcIrrigationCost(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-1.5 rounded-lg border border-charcoal-200 font-semibold focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-charcoal-500 text-[11px] mb-1">Machinery / ac</label>
                <input
                  type="number"
                  value={calcMachineryCost}
                  onChange={(e) => setCalcMachineryCost(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-1.5 rounded-lg border border-charcoal-200 font-semibold focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-charcoal-500 text-[11px] mb-1">Transport / ac</label>
                <input
                  type="number"
                  value={calcTransportCost}
                  onChange={(e) => setCalcTransportCost(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-1.5 rounded-lg border border-charcoal-200 font-semibold focus:outline-none"
                />
              </div>
            </div>

            <p className="font-bold text-forest-900 pt-2 border-t border-charcoal-100">
              Yield & Market Expectations
            </p>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-charcoal-600 mb-1 font-bold">Expected Yield (q/acre)</label>
                <input
                  type="number"
                  step="0.5"
                  value={calcExpectedYield}
                  onChange={(e) => setCalcExpectedYield(parseFloat(e.target.value) || 1)}
                  className="w-full px-3 py-2 rounded-xl border border-charcoal-200 font-bold focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-charcoal-600 mb-1 font-bold">Expected Price (₹/quintal)</label>
                <input
                  type="number"
                  step="50"
                  value={calcSellingPrice}
                  onChange={(e) => setCalcSellingPrice(parseInt(e.target.value) || 1000)}
                  className="w-full px-3 py-2 rounded-xl border border-charcoal-200 font-bold focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Results Analytics Card (6 Cols) */}
          <div className="lg:col-span-6 rounded-3xl bg-forest-950 text-white p-6 sm:p-8 shadow-soft-lg flex flex-col justify-between">
            <div className="space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-forest-800">
                <div>
                  <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-forest-800 text-saffron-300">
                    Financial Summary
                  </span>
                  <h3 className="text-xl font-black text-white mt-1">
                    {calcCrop.split('(')[0]}
                  </h3>
                  <p className="text-xs text-forest-300">{calcFarmSize} Acres Cultivation</p>
                </div>

                <div className="text-right">
                  <span className="text-[10px] uppercase font-bold text-forest-400">Profit Margin</span>
                  <p className="text-2xl font-black text-saffron-400">{profitMarginPercent}%</p>
                </div>
              </div>

              {/* Big KPI Display */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl bg-forest-900/80 border border-forest-800">
                  <p className="text-[11px] font-bold text-forest-300 uppercase">Estimated Net Profit</p>
                  <p className="text-2xl sm:text-3xl font-black text-emerald-400 mt-1">
                    ₹{netProfit.toLocaleString()}
                  </p>
                  <p className="text-[10px] text-forest-400 mt-0.5">
                    ₹{Math.round(netProfit / calcFarmSize).toLocaleString()} / acre
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-forest-900/80 border border-forest-800">
                  <p className="text-[11px] font-bold text-forest-300 uppercase">Gross Revenue</p>
                  <p className="text-2xl sm:text-3xl font-black text-white mt-1">
                    ₹{grossRevenue.toLocaleString()}
                  </p>
                  <p className="text-[10px] text-forest-400 mt-0.5">
                    {totalProductionQuintals.toFixed(1)} Quintals Produced
                  </p>
                </div>
              </div>

              {/* Financial Metrics Row */}
              <div className="grid grid-cols-3 gap-3 text-center text-xs">
                <div className="p-3 rounded-xl bg-forest-900/50 border border-forest-800">
                  <span className="text-forest-400 text-[10px] block">Total Expenditure</span>
                  <strong className="text-white text-sm">₹{totalCultivationCost.toLocaleString()}</strong>
                </div>

                <div className="p-3 rounded-xl bg-forest-900/50 border border-forest-800">
                  <span className="text-forest-400 text-[10px] block">Cost Per Acre</span>
                  <strong className="text-white text-sm">₹{totalCostPerAcre.toLocaleString()}</strong>
                </div>

                <div className="p-3 rounded-xl bg-forest-900/50 border border-forest-800">
                  <span className="text-forest-400 text-[10px] block">Break-even Rate</span>
                  <strong className="text-saffron-300 text-sm">₹{breakEvenPrice}/q</strong>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-forest-800 text-[11px] text-forest-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-saffron-400 shrink-0" />
              <span>
                Calculations are modeled estimates based on standard regional inputs and prevailing APMC rates, not guaranteed financial returns.
              </span>
            </div>
          </div>
        </div>
      )}

      {/* ================= TAB 3: CROP COMPARISON ================= */}
      {selectedTab === 'comparison' && (
        <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-8 shadow-soft animate-fade-in space-y-6">
          <div>
            <h3 className="text-base font-extrabold text-forest-900">
              Top 3 Regional Crops Economics Comparison
            </h3>
            <p className="text-xs text-charcoal-400">
              Comparative analysis of cultivation expenses, water requirements, and net profit per acre
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-5 rounded-2xl bg-forest-50/60 border border-forest-100 space-y-3">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-forest-900 text-white">
                Rank #1
              </span>
              <h4 className="text-base font-bold text-forest-900">Basmati Rice (Pusa 1509)</h4>
              <p className="text-xs text-charcoal-600">High revenue cereal for irrigated valleys.</p>

              <div className="space-y-1.5 text-xs text-charcoal-700 pt-2 border-t border-forest-200">
                <div className="flex justify-between">
                  <span>Input Cost / ac:</span>
                  <strong>₹21,300</strong>
                </div>
                <div className="flex justify-between">
                  <span>Water Requirement:</span>
                  <strong className="text-rose-600">High (1,100mm)</strong>
                </div>
                <div className="flex justify-between">
                  <span>Expected Yield:</span>
                  <strong>22.5 q/ac</strong>
                </div>
                <div className="flex justify-between text-emerald-800 font-bold">
                  <span>Estimated Net Profit:</span>
                  <strong>₹48,600 / ac</strong>
                </div>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-saffron-50/60 border border-saffron-100 space-y-3">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-saffron-500 text-charcoal-900">
                Rank #2
              </span>
              <h4 className="text-base font-bold text-forest-900">Finger Millet / Mandua</h4>
              <p className="text-xs text-charcoal-600">Super resilient hill crop with low input cost.</p>

              <div className="space-y-1.5 text-xs text-charcoal-700 pt-2 border-t border-saffron-200">
                <div className="flex justify-between">
                  <span>Input Cost / ac:</span>
                  <strong>₹8,400</strong>
                </div>
                <div className="flex justify-between">
                  <span>Water Requirement:</span>
                  <strong className="text-emerald-700">Low (350mm)</strong>
                </div>
                <div className="flex justify-between">
                  <span>Expected Yield:</span>
                  <strong>14.0 q/ac</strong>
                </div>
                <div className="flex justify-between text-emerald-800 font-bold">
                  <span>Estimated Net Profit:</span>
                  <strong>₹39,500 / ac</strong>
                </div>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-forest-50/60 border border-forest-100 space-y-3">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-forest-700 text-white">
                Rank #3
              </span>
              <h4 className="text-base font-bold text-forest-900">Black Soybean (Bhatt)</h4>
              <p className="text-xs text-charcoal-600">Soil enriching nitrogen-fixing legume.</p>

              <div className="space-y-1.5 text-xs text-charcoal-700 pt-2 border-t border-forest-200">
                <div className="flex justify-between">
                  <span>Input Cost / ac:</span>
                  <strong>₹10,500</strong>
                </div>
                <div className="flex justify-between">
                  <span>Water Requirement:</span>
                  <strong className="text-forest-700">Medium (500mm)</strong>
                </div>
                <div className="flex justify-between">
                  <span>Expected Yield:</span>
                  <strong>11.2 q/ac</strong>
                </div>
                <div className="flex justify-between text-emerald-800 font-bold">
                  <span>Estimated Net Profit:</span>
                  <strong>₹34,200 / ac</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
