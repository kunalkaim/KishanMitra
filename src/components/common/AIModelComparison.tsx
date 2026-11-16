import React from 'react';
import { AIModelPrediction } from '../../types';
import { Cpu, GitFork, BarChart3, ShieldCheck, Check } from 'lucide-react';

interface AIModelComparisonProps {
  models: AIModelPrediction[];
  ensembleConfidence: number;
  modelAgreement: 'Very High' | 'High' | 'Moderate';
}

export const AIModelComparison: React.FC<AIModelComparisonProps> = ({
  models,
  ensembleConfidence,
  modelAgreement,
}) => {
  const getModelIcon = (name: string) => {
    if (name.toLowerCase().includes('fuzzy')) return Cpu;
    if (name.toLowerCase().includes('decision')) return GitFork;
    return BarChart3;
  };

  return (
    <div className="p-6 rounded-2xl bg-white border border-forest-100 shadow-soft">
      {/* Header with Ensemble Agreement Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b border-charcoal-100 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-forest-50 text-forest-700">
              <Cpu className="w-4 h-4" />
            </span>
            <h3 className="text-base font-extrabold text-forest-900 tracking-tight">
              Hybrid Multi-Model Ensemble Architecture
            </h3>
          </div>
          <p className="text-xs text-charcoal-400 mt-1">
            Tri-expert validation: Fuzzy Logic, Bayesian Likelihood & Empirical Decision Trees
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-xl bg-forest-50 border border-forest-200 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-forest-700" />
            <div>
              <p className="text-[10px] uppercase font-bold text-charcoal-400">Consensus</p>
              <p className="text-xs font-extrabold text-forest-900">{modelAgreement} Agreement</p>
            </div>
          </div>

          <div className="px-3.5 py-1.5 rounded-xl bg-saffron-50 border border-saffron-200">
            <p className="text-[10px] uppercase font-bold text-saffron-800">Ensemble Confidence</p>
            <p className="text-sm font-black text-saffron-900">{ensembleConfidence}%</p>
          </div>
        </div>
      </div>

      {/* 3 Expert Model Cards Grid */}
      <div className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-4">
        {models.map((model, idx) => {
          const Icon = getModelIcon(model.modelName);
          return (
            <div
              key={idx}
              className="p-4 rounded-xl bg-charcoal-50/70 border border-charcoal-100 hover:border-forest-200 transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-lg bg-forest-100 text-forest-800 flex items-center justify-center">
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <h5 className="text-xs font-bold text-forest-900 leading-tight">
                      {model.modelName.split(' ')[0]} Expert
                    </h5>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <p className="text-[10px] text-charcoal-400">
                        Weight: <span className="font-bold text-charcoal-700">{Math.round(model.weight * 100)}%</span>
                      </p>
                      {model.weight === 0 && (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                          Domain Validator
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <span className="px-2 py-0.5 rounded-md text-xs font-extrabold bg-white text-forest-900 border border-charcoal-200 shadow-sm">
                  {model.confidence}%
                </span>
              </div>

              <div className="mt-3 p-2 rounded-lg bg-white border border-charcoal-100">
                <p className="text-[10px] uppercase font-bold text-charcoal-400">Top Predicted Crop</p>
                <p className="text-xs font-bold text-forest-800 mt-0.5 truncate">
                  {model.topCrop}
                </p>
              </div>

              <p className="mt-2.5 text-[11px] text-charcoal-600 leading-relaxed font-normal">
                {model.logicSummary}
              </p>

              <div className="mt-3 pt-2.5 border-t border-charcoal-100/80 space-y-1">
                <p className="text-[10px] uppercase font-semibold text-charcoal-400 tracking-wider">
                  Evaluated Criteria
                </p>
                {model.keyFactors.map((factor, fIdx) => (
                  <div key={fIdx} className="flex items-center gap-1.5 text-[11px] text-charcoal-700">
                    <Check className="w-3 h-3 text-forest-600 shrink-0" />
                    <span className="truncate">{factor}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
