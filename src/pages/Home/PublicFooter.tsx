import React from 'react';
import { NavLink } from 'react-router-dom';
import { Sprout, Phone, Mail, MapPin, Heart, Shield, Award, ExternalLink } from 'lucide-react';

export const PublicFooter: React.FC = () => {
  return (
    <footer className="bg-forest-950 text-forest-200 border-t border-forest-900 pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-forest-900/80">
          {/* Brand Info */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-forest-600/30 border border-forest-500/40 flex items-center justify-center text-saffron-400">
                <Sprout className="w-6 h-6" />
              </div>
              <span className="text-xl font-extrabold text-white">
                Kisan<span className="text-saffron-400">Mitra</span>
              </span>
            </div>
            <p className="mt-4 text-xs text-forest-300 leading-relaxed max-w-sm">
              AI-Powered Smart Agriculture & Farmer Decision Intelligence Platform. Empowering Indian growers with Explainable AI recommendations, geo-spatial soil profiling, live mandi analytics, and plant health diagnostics.
            </p>

            <div className="mt-6 flex flex-wrap gap-2 text-[11px] text-forest-300">
              <span className="px-3 py-1 rounded-full bg-forest-900 border border-forest-800">
                🌱 Uttarakhand Pioneer Focus
              </span>
              <span className="px-3 py-1 rounded-full bg-forest-900 border border-forest-800">
                🇮🇳 All-India Architecture
              </span>
              <span className="px-3 py-1 rounded-full bg-forest-900 border border-forest-800">
                🤖 Explainable Hybrid AI
              </span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs font-black uppercase tracking-wider text-white">
              Application Modules
            </h4>
            <ul className="mt-4 space-y-2.5 text-xs text-forest-300">
              <li>
                <NavLink to="/dashboard" className="hover:text-saffron-400 transition-colors">
                  Overview Dashboard
                </NavLink>
              </li>
              <li>
                <NavLink to="/crop-recommendation" className="hover:text-saffron-400 transition-colors">
                  Hybrid Crop Recommendation
                </NavLink>
              </li>
              <li>
                <NavLink to="/advisory" className="hover:text-saffron-400 transition-colors">
                  Pest & Disease Advisory
                </NavLink>
              </li>
              <li>
                <NavLink to="/region-intelligence" className="hover:text-saffron-400 transition-colors">
                  Region & District Intelligence
                </NavLink>
              </li>
              <li>
                <NavLink to="/weather" className="hover:text-saffron-400 transition-colors">
                  Agricultural Weather
                </NavLink>
              </li>
              <li>
                <NavLink to="/market-intelligence" className="hover:text-saffron-400 transition-colors">
                  Mandi Price Explorer
                </NavLink>
              </li>
            </ul>
          </div>

          {/* Advisory & Support */}
          <div>
            <h4 className="text-xs font-black uppercase tracking-wider text-white">
              Farmer Advisory
            </h4>
            <ul className="mt-4 space-y-2.5 text-xs text-forest-300">
              <li>
                <NavLink to="/smart-advisor" className="hover:text-saffron-400 transition-colors">
                  NPK & Soil Health Guide
                </NavLink>
              </li>
              <li>
                <NavLink to="/crop-rotation" className="hover:text-saffron-400 transition-colors">
                  Multi-Season Rotation Planner
                </NavLink>
              </li>
              <li>
                <NavLink to="/ai-assistant" className="hover:text-saffron-400 transition-colors">
                  RAG Agronomic Assistant
                </NavLink>
              </li>
              <li>
                <NavLink to="/satellite-monitoring" className="hover:text-saffron-400 transition-colors">
                  Satellite NDVI Monitoring
                </NavLink>
              </li>
              <li>
                <NavLink to="/feedback" className="hover:text-saffron-400 transition-colors">
                  Farmer Harvest Feedback
                </NavLink>
              </li>
              <li>
                <NavLink to="/farms" className="hover:text-saffron-400 transition-colors">
                  Soil Profile Registration
                </NavLink>
              </li>
            </ul>
          </div>

          {/* Helplines */}
          <div>
            <h4 className="text-xs font-black uppercase tracking-wider text-white">
              Official Helplines
            </h4>
            <div className="mt-4 space-y-3 text-xs text-forest-300">
              <div className="p-3 rounded-xl bg-forest-900/60 border border-forest-800">
                <p className="font-bold text-white text-xs flex items-center gap-1.5">
                  <Phone className="w-3.5 h-3.5 text-saffron-400" />
                  Kisan Call Center (Govt)
                </p>
                <p className="text-sm font-black text-saffron-300 mt-1">1800-180-1551</p>
                <p className="text-[10px] text-forest-400">Toll Free • 6:00 AM - 10:00 PM</p>
              </div>

              <div className="p-3 rounded-xl bg-forest-900/60 border border-forest-800">
                <p className="font-bold text-white text-xs flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-saffron-400" />
                  Uttarakhand KVK Hub
                </p>
                <p className="text-[11px] text-forest-300 mt-1">
                  GBPUAT Pantnagar & VPKAS Almora Extension
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-forest-400 gap-4">
          <p>
            © 2026 KisanMitra. Built for Indian Agricultural Excellence & National Hackathon Innovation.
          </p>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1 text-forest-300">
              Made with <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" /> for Indian Farmers
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
