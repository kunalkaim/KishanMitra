import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { FarmerProfile } from '../../types';
import {
  UserCheck,
  Phone,
  MapPin,
  Calendar,
  Save,
  CheckCircle2,
  Shield,
  FileText,
  Award,
  Globe
} from 'lucide-react';

export const FarmerProfilePage: React.FC = () => {
  const { profile, updateProfile, t } = useApp();
  const [formData, setFormData] = useState<FarmerProfile>(profile);
  const [isSaved, setIsSaved] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfile(formData);
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-charcoal-100">
        <div>
          <h1 className="text-2xl font-black text-forest-900 tracking-tight">
            Farmer Profile & Agricultural KYC
          </h1>
          <p className="text-xs text-charcoal-400 mt-1">
            Maintain your personal credentials, farming experience, and official Soil Health Card records
          </p>
        </div>

        {isSaved && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-100 text-emerald-800 text-xs font-bold animate-fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Profile Saved!</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left: Avatar & KYC Status Card */}
        <div className="rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft flex flex-col items-center text-center">
          <div className="relative">
            <img
              src={formData.avatarUrl}
              alt={formData.name}
              className="w-28 h-28 rounded-2xl object-cover ring-4 ring-forest-50 shadow-md"
            />
            <span className="absolute bottom-1 right-1 p-1 rounded-full bg-emerald-500 text-white ring-2 ring-white">
              <Shield className="w-3.5 h-3.5" />
            </span>
          </div>

          <h3 className="mt-4 text-base font-bold text-forest-900">{formData.name}</h3>
          <p className="text-xs text-charcoal-400 font-medium">Progressive Hill Farmer</p>

          <div className="mt-4 w-full pt-4 border-t border-charcoal-100 text-left space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-charcoal-400">KYC Status:</span>
              <span className="font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                Verified
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-charcoal-400">Soil Health Card:</span>
              <span className="font-mono text-[11px] font-bold text-forest-900">
                {formData.soilHealthCardNumber || 'SHC-UK-2024'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-charcoal-400">Experience:</span>
              <span className="font-bold text-forest-900">
                {formData.farmingExperienceYears} Years
              </span>
            </div>
          </div>
        </div>

        {/* Right: Form Editor */}
        <div className="md:col-span-2 rounded-3xl bg-white border border-charcoal-100 p-6 shadow-soft">
          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">Full Legal Name</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-bold text-charcoal-700 mb-1">Age</label>
                <input
                  type="number"
                  value={formData.age || ''}
                  onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-bold text-charcoal-700 mb-1">Mobile Phone</label>
                <input
                  type="text"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block font-bold text-charcoal-700 mb-1">State</label>
                <input
                  type="text"
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                />
              </div>
              <div>
                <label className="block font-bold text-charcoal-700 mb-1">District</label>
                <input
                  type="text"
                  value={formData.district}
                  onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                />
              </div>
              <div>
                <label className="block font-bold text-charcoal-700 mb-1">Village</label>
                <input
                  type="text"
                  value={formData.village}
                  onChange={(e) => setFormData({ ...formData, village: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-bold text-charcoal-700 mb-1">
                  Farming Practices
                </label>
                <select
                  value={formData.farmingPractices}
                  onChange={(e) => setFormData({ ...formData, farmingPractices: e.target.value as any })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                >
                  <option value="integrated">Integrated Farming (Modern + Organic)</option>
                  <option value="organic">100% Certified Organic</option>
                  <option value="natural">Natural Farming (Subhash Palekar ZBNF)</option>
                  <option value="conventional">Conventional High-Yield Farming</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-charcoal-700 mb-1">
                  Years of Farming Experience
                </label>
                <input
                  type="number"
                  value={formData.farmingExperienceYears}
                  onChange={(e) => setFormData({ ...formData, farmingExperienceYears: parseInt(e.target.value) || 1 })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Soil Health Card Registry No.
              </label>
              <input
                type="text"
                placeholder="e.g. SHC-UK-DDN-2024-8841"
                value={formData.soilHealthCardNumber || ''}
                onChange={(e) => setFormData({ ...formData, soilHealthCardNumber: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
              />
            </div>

            <div className="pt-4 border-t border-charcoal-100 flex justify-end">
              <button
                type="submit"
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold bg-forest-900 hover:bg-forest-800 text-white shadow-md transition-all active:scale-95"
              >
                <Save className="w-4 h-4 text-saffron-400" />
                <span>Save Farmer Profile</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
