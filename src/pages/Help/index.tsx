import React, { useState } from 'react';
import {
  HelpCircle,
  Phone,
  Mail,
  MapPin,
  ChevronDown,
  ChevronUp,
  FileText,
  ExternalLink,
  ShieldCheck,
  Sprout
} from 'lucide-react';

export const HelpPage: React.FC = () => {
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const faqs = [
    {
      q: 'How does KisanMitra determine crop suitability for my field?',
      a: 'KisanMitra uses a 3-expert hybrid ensemble combining Fuzzy Logic (agronomic threshold rules), Gaussian Naive Bayes (historical regional climate-yield likelihoods), and Decision Trees (deterministic constraint partitioning). The final recommendation synthesizes all three outputs with explainable feature importance.'
    },
    {
      q: 'How does the Pest & Disease Advisory module generate recommendations?',
      a: 'The advisory workspace analyzes reported symptoms, growth stage, and microclimate conditions against verified ICAR-VPKAS Almora and GBPUAT Pantnagar plant protection data to diagnose suspected pathogens and suggest biological and organic IPM remedies.'
    },
    {
      q: 'How can I add multiple terraced farm parcels?',
      a: 'Navigate to "My Farms & Fields" in the sidebar and click "+ Register New Farm". You can specify distinct micro-climates, soil pH, and irrigation types for each parcel, then switch between them seamlessly using the topbar dropdown.'
    },
    {
      q: 'What government subsidies are covered in the platform?',
      a: 'KisanMitra includes advisory information on PM-KISAN, Pradhan Mantri Fasal Bima Yojana (PMFBY), Paramparagat Krishi Vikas Yojana (PKVY), and the Uttarakhand State Millet Mission bonus procurement scheme.'
    }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16 animate-fade-in">
      <div className="pb-4 border-b border-charcoal-100">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-xs font-bold text-forest-800 mb-1.5">
          <HelpCircle className="w-3.5 h-3.5 text-forest-700" />
          <span>Agricultural Extension & Technical Support</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
          Help & Farmer Support Center
        </h1>
        <p className="text-xs text-charcoal-400 mt-1">
          Government agricultural helplines, Krishi Vigyan Kendra directory, and frequently asked platform questions
        </p>
      </div>

      {/* Emergency Helpline Banner */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-6 rounded-3xl bg-forest-950 text-white shadow-soft flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-forest-800 text-saffron-400 flex items-center justify-center shrink-0">
            <Phone className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold text-saffron-300">Govt. of India Toll Free</span>
            <h3 className="text-xl font-black text-white mt-0.5">1800-180-1551</h3>
            <p className="text-xs text-forest-200 mt-1">
              Kisan Call Center (KCC) • Available in Hindi & Regional Languages • 06:00 AM – 10:00 PM Daily
            </p>
          </div>
        </div>

        <div className="p-6 rounded-3xl bg-white border border-charcoal-100 shadow-soft flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-forest-50 text-forest-700 flex items-center justify-center shrink-0">
            <MapPin className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold text-charcoal-400">Uttarakhand KVK Hub</span>
            <h3 className="text-base font-extrabold text-forest-900 mt-0.5">GBPUAT Pantnagar</h3>
            <p className="text-xs text-charcoal-500 mt-1">
              Directorate of Agricultural Extension • Pantnagar & VPKAS Almora Hill Campus
            </p>
          </div>
        </div>
      </div>

      {/* FAQ Accordion */}
      <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-8 shadow-soft space-y-4">
        <h3 className="text-base font-extrabold text-forest-900 mb-2">
          Frequently Asked Questions
        </h3>

        <div className="space-y-3">
          {faqs.map((faq, idx) => {
            const isOpen = openFaq === idx;
            return (
              <div
                key={idx}
                className="rounded-2xl border border-charcoal-100 overflow-hidden transition-all text-xs"
              >
                <button
                  type="button"
                  onClick={() => setOpenFaq(isOpen ? null : idx)}
                  className="w-full p-4 text-left font-bold text-forest-900 flex items-center justify-between hover:bg-forest-50/50"
                >
                  <span>{faq.q}</span>
                  {isOpen ? <ChevronUp className="w-4 h-4 text-forest-700" /> : <ChevronDown className="w-4 h-4 text-charcoal-400" />}
                </button>

                {isOpen && (
                  <div className="px-4 pb-4 pt-1 text-charcoal-600 leading-relaxed bg-forest-50/30 border-t border-charcoal-100/50">
                    {faq.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
