import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RecommendedCrop } from '../../types';
import { useApp } from '../../context/AppContext';
import {
  Droplets,
  Calendar,
  Award,
  TrendingUp,
  ChevronDown,
  ChevronUp,
  Sparkles,
  CheckCircle2,
  BookOpen,
  MessageSquare,
  Building2,
  AlertTriangle,
  Info,
  Scale
} from 'lucide-react';

interface CropCardProps {
  crop: RecommendedCrop;
  rank: number;
  isSelected?: boolean;
  onSelect?: () => void;
  onAddToPlan?: () => void;
}

export const CropCard: React.FC<CropCardProps> = ({
  crop,
  rank,
  isSelected,
  onSelect,
  onAddToPlan,
}) => {
  const navigate = useNavigate();
  const { language } = useApp();
  const isHindi = language === 'hi';
  const [showXai, setShowXai] = useState(false);
  const [showRAG, setShowRAG] = useState(false);
  const [showEconomics, setShowEconomics] = useState(false);

  const getRankBadge = () => {
    switch (rank) {
      case 1:
        return 'bg-saffron-500 text-charcoal-900 ring-2 ring-saffron-300';
      case 2:
        return 'bg-forest-700 text-white';
      case 3:
        return 'bg-forest-600 text-white';
      default:
        return 'bg-charcoal-700 text-white';
    }
  };

  const primaryCitation = crop.ragCitations && crop.ragCitations.length > 0 ? crop.ragCitations[0] : null;

  const handleAskAssistant = () => {
    const query = `What is the verified package of practices and cultivation schedule for ${crop.name} in Uttarakhand?`;
    navigate(`/assistant?q=${encodeURIComponent(query)}`);
  };

  return (
    <div
      className={`rounded-2xl bg-white border transition-all duration-200 shadow-soft overflow-hidden flex flex-col justify-between ${
        isSelected
          ? 'border-forest-600 ring-2 ring-forest-500/20'
          : 'border-charcoal-100 hover:border-forest-200'
      }`}
    >
      <div>
        {/* Top Banner with Image */}
        <div className="relative h-48 w-full overflow-hidden bg-charcoal-100">
          <img
            src={crop.image}
            alt={crop.name}
            className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/25 to-transparent" />

          {/* Rank & Score Pill */}
          <div className="absolute top-3 left-3 flex items-center gap-2 flex-wrap">
            <span className={`px-2.5 py-1 rounded-full text-xs font-black shadow-md ${getRankBadge()}`}>
              {isHindi ? `रैंक #${rank}` : `Rank #${rank}`}
            </span>
            <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-white/95 text-forest-900 backdrop-blur-md shadow-md flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-saffron-500" />
              {crop.suitabilityScore}% {isHindi ? 'उपयुक्तता' : 'Suitability'}
            </span>
          </div>

          {/* Citations Pill on Top Right */}
          {primaryCitation && (
            <div className="absolute top-3 right-3">
              <span className="px-2 py-1 rounded-full text-[10px] font-bold bg-forest-900/90 text-white backdrop-blur-md border border-forest-600 shadow-md flex items-center gap-1">
                <BookOpen className="w-2.5 h-2.5 text-saffron-400" />
                <span>{primaryCitation.publisher.includes('VPKAS') ? 'ICAR-VPKAS' : 'GBPUAT 2026'}</span>
              </span>
            </div>
          )}

          {/* Crop Name & Hindi Name */}
          <div className="absolute bottom-3 left-3 right-3 text-white">
            <h4 className="text-lg font-extrabold leading-tight tracking-tight drop-shadow-sm">
              {isHindi && crop.hindiName ? crop.hindiName : crop.name}
            </h4>
            <p className="text-xs font-medium text-forest-200 drop-shadow-sm mt-0.5">
              {isHindi ? crop.name : crop.hindiName}
            </p>
          </div>
        </div>

        {/* Body Content */}
        <div className="p-5 space-y-4">
          <p className="text-xs text-charcoal-600 leading-relaxed font-normal">
            {crop.shortExplanation || crop.whyRecommended}
          </p>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 gap-2.5">
            <div className="p-2.5 rounded-xl bg-forest-50/60 border border-forest-100/70">
              <div className="flex items-center gap-1.5 text-xs text-charcoal-500 font-medium">
                <Droplets className="w-3.5 h-3.5 text-forest-600" />
                <span>{isHindi ? 'जल आवश्यकता' : 'Water Need'}</span>
              </div>
              <p className="mt-1 text-sm font-bold text-forest-900">
                {isHindi 
                  ? (crop.waterRequirement === 'Low' ? 'कम' : crop.waterRequirement === 'High' ? 'अधिक' : 'मध्यम')
                  : crop.waterRequirement}
              </p>
            </div>

            <div className="p-2.5 rounded-xl bg-forest-50/60 border border-forest-100/70">
              <div className="flex items-center gap-1.5 text-xs text-charcoal-500 font-medium">
                <Calendar className="w-3.5 h-3.5 text-forest-600" />
                <span>{isHindi ? 'अवधि' : 'Duration'}</span>
              </div>
              <p className="mt-1 text-sm font-bold text-forest-900">
                {crop.growingDurationDays} {isHindi ? 'दिन' : 'Days'}
              </p>
            </div>

            <div className="p-2.5 rounded-xl bg-saffron-50/60 border border-saffron-100">
              <div className="flex items-center gap-1.5 text-xs text-charcoal-500 font-medium">
                <Award className="w-3.5 h-3.5 text-saffron-600" />
                <span>{isHindi ? 'अपेक्षित पैदावार' : 'Expected Yield'}</span>
              </div>
              <p className="mt-1 text-sm font-bold text-charcoal-900">
                {crop.expectedYieldQuintalsPerAcre} {isHindi ? 'क्विंटल/एकड़' : 'q/acre'}
              </p>
            </div>

            <div className="p-2.5 rounded-xl bg-emerald-50/70 border border-emerald-100">
              <div className="flex items-center gap-1.5 text-xs text-charcoal-500 font-medium">
                <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                <span>{isHindi ? 'अनुमानित शुद्ध लाभ' : 'Est. Net Profit'}</span>
              </div>
              <p className="mt-1 text-sm font-bold text-emerald-800">
                ₹{crop.estimatedNetProfitPerAcre.toLocaleString()}{isHindi ? '/एकड़' : '/ac'}
              </p>
            </div>
          </div>

          {/* Mandi Economics Bar */}
          {crop.modalPricePerQuintal && crop.modalPricePerQuintal > 0 && (
            <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200/80 text-xs">
              <div className="flex items-center justify-between font-bold text-amber-950">
                <div className="flex items-center gap-1.5">
                  <Building2 className="w-3.5 h-3.5 text-amber-700" />
                  <span>{crop.mandiName || 'Regional APMC Mandi'}</span>
                </div>
                <span className="text-amber-800 font-extrabold">₹{crop.modalPricePerQuintal.toLocaleString()}/q</span>
              </div>
              <div className="mt-1.5 flex items-center justify-between text-[11px] text-amber-800/90 font-medium">
                <span>BCR: <strong>{crop.benefitCostRatio ?? 2.1}</strong></span>
                <span>Breakeven Yield: <strong>{crop.breakevenYieldPerAcre ?? 5.5} q/ac</strong></span>
                <span>Breakeven Price: <strong>₹{crop.breakevenPricePerQuintal ?? 1450}/q</strong></span>
              </div>
            </div>
          )}

          {/* Section 1: Verified RAG Knowledge Citations */}
          {crop.ragCitations && crop.ragCitations.length > 0 && (
            <div className="pt-2 border-t border-charcoal-100">
              <button
                type="button"
                onClick={() => setShowRAG(!showRAG)}
                className="w-full flex items-center justify-between text-xs font-bold text-forest-800 hover:text-forest-900 py-1"
              >
                <span className="flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-forest-700" />
                  <span>Verified University POP ({crop.ragCitations.length} Citations)</span>
                </span>
                {showRAG ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showRAG && (
                <div className="mt-2.5 space-y-2 animate-fade-in text-xs">
                  {crop.verifiedPackageOfPractices && crop.verifiedPackageOfPractices.length > 0 && (
                    <div className="p-2.5 rounded-xl bg-forest-50/50 border border-forest-100 space-y-1">
                      <p className="font-bold text-[11px] text-forest-900 uppercase tracking-wider">Agronomic Practices:</p>
                      {crop.verifiedPackageOfPractices.map((pop, idx) => (
                        <div key={idx} className="flex items-start gap-1.5 text-charcoal-700 text-[11px] leading-relaxed">
                          <CheckCircle2 className="w-3 h-3 text-forest-600 mt-0.5 shrink-0" />
                          <span>{pop}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="space-y-1.5">
                    {crop.ragCitations.map((cit, idx) => (
                      <div key={idx} className="p-2 rounded-lg bg-charcoal-50 border border-charcoal-100 text-[11px]">
                        <div className="flex items-center justify-between font-semibold text-charcoal-800">
                          <span className="truncate pr-2">{cit.documentTitle}</span>
                          <span className="text-[10px] font-bold text-forest-700 bg-white px-1.5 py-0.5 rounded border border-charcoal-200 shrink-0">
                            p. {cit.pageStart}{cit.pageEnd && cit.pageEnd !== cit.pageStart ? `-${cit.pageEnd}` : ''}
                          </span>
                        </div>
                        <p className="text-charcoal-500 text-[10px] mt-0.5 italic">
                          Publisher: {cit.publisher} ({Math.round(cit.retrievalScore * 100)}% match)
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Section 2: Explainable AI Accordion */}
          <div className="pt-2 border-t border-charcoal-100">
            <button
              type="button"
              onClick={() => setShowXai(!showXai)}
              className="w-full flex items-center justify-between text-xs font-bold text-forest-800 hover:text-forest-900 py-1"
            >
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-saffron-500" />
                Explainable AI: Key Influencing Factors
              </span>
              {showXai ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showXai && (
              <div className="mt-2.5 space-y-2 animate-fade-in text-xs">
                {crop.xaiInfluences.map((item, idx) => (
                  <div key={idx} className="p-2 rounded-lg bg-charcoal-50 border border-charcoal-100">
                    <div className="flex items-center justify-between font-semibold text-charcoal-800">
                      <span>{item.factor}</span>
                      <span className="text-emerald-700 font-bold">+{item.impact}% weight</span>
                    </div>
                    <p className="text-charcoal-500 text-[11px] mt-0.5 leading-normal">
                      {item.description}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Agromet & Elevation Risk Notice */}
          {crop.districtElevationAlert && (
            <div className="p-2 rounded-lg bg-blue-50/60 border border-blue-100 text-[11px] text-blue-900 flex items-start gap-1.5">
              <Info className="w-3.5 h-3.5 text-blue-600 mt-0.5 shrink-0" />
              <span>{crop.districtElevationAlert}</span>
            </div>
          )}

          {/* Economic Disclaimer */}
          {crop.economicDisclaimer && (
            <p className="text-[10px] text-charcoal-400 italic">
              * {crop.economicDisclaimer}
            </p>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-5 pt-0 mt-2 space-y-2">
        <div className="flex items-center gap-2">
          {onSelect && (
            <button
              type="button"
              onClick={onSelect}
              className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                isSelected
                  ? 'bg-forest-900 text-white'
                  : 'bg-forest-50 hover:bg-forest-100 text-forest-800'
              }`}
            >
              {isSelected ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {isHindi ? 'चयनित फसल' : 'Selected Choice'}
                </>
              ) : (
                isHindi ? 'फसल चुनें' : 'Select Crop'
              )}
            </button>
          )}

          {onAddToPlan && (
            <button
              type="button"
              onClick={onAddToPlan}
              className="py-2 px-3 rounded-xl text-xs font-semibold bg-saffron-50 hover:bg-saffron-100 text-saffron-900 border border-saffron-200 transition-all"
            >
              {isHindi ? 'योजना में जोड़ें' : 'Add to Plan'}
            </button>
          )}
        </div>

        <button
          type="button"
          onClick={handleAskAssistant}
          className="w-full py-2 px-3 rounded-xl text-xs font-bold bg-white hover:bg-forest-50 text-forest-900 border border-forest-200 transition-all flex items-center justify-center gap-1.5 shadow-xs"
        >
          <MessageSquare className="w-3.5 h-3.5 text-forest-700" />
          <span>
            {isHindi 
              ? `${(crop.hindiName || crop.name).split('(')[0].trim()} के बारे में एआई से पूछें` 
              : `Ask AI Assistant about ${crop.name.split('(')[0].trim()}`}
          </span>
        </button>
      </div>
    </div>
  );
};
