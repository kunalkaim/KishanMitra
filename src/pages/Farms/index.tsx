import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import { Farm } from '../../types';
import { ConfirmationDialog } from '../../components/common/ConfirmationDialog';
import {
  Sprout,
  Plus,
  MapPin,
  Edit2,
  Trash2,
  Layers,
  Droplets,
  Calendar,
  CheckCircle2,
  DollarSign,
  ChevronRight,
  X,
  Compass,
  Sparkles
} from 'lucide-react';
import { uttarakhandDistricts } from '../../data/demoData';

export const FarmsPage: React.FC = () => {
  const { farms, activeFarmId, setActiveFarmId, addFarm, updateFarm, deleteFarm } = useApp();
  const [searchParams, setSearchParams] = useSearchParams();

  // Dialog & Form states
  const [isAddModalOpen, setIsAddModalOpen] = useState(searchParams.get('add') === 'true');
  const [editingFarm, setEditingFarm] = useState<Farm | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  // Multi-step form step (1: General/Location, 2: Soil Profile, 3: Water/Irrigation, 4: Crop/Budget)
  const [formStep, setFormStep] = useState(1);

  // Form State
  const [formData, setFormData] = useState<Omit<Farm, 'id'>>({
    name: '',
    size: 2.5,
    sizeUnit: 'acres',
    state: 'Uttarakhand',
    district: 'Dehradun',
    block: 'Raipur',
    village: '',
    latitude: 30.3165,
    longitude: 78.0322,
    elevation: 650,
    soilType: 'loamy',
    soilPh: 6.8,
    nitrogen: 140,
    phosphorus: 45,
    potassium: 200,
    organicCarbon: 0.85,
    electricalConductivity: 0.40,
    irrigationType: 'drip',
    waterAvailability: 'abundant',
    previousCrops: ['Wheat', 'Rice'],
    currentSeason: 'Kharif',
    availableBudget: 50000,
  });

  const openAddModal = () => {
    setEditingFarm(null);
    setFormStep(1);
    setFormData({
      name: '',
      size: 2.5,
      sizeUnit: 'acres',
      state: 'Uttarakhand',
      district: 'Dehradun',
      block: 'Raipur',
      village: '',
      latitude: 30.3165,
      longitude: 78.0322,
      elevation: 650,
      soilType: 'loamy',
      soilPh: 6.8,
      nitrogen: 140,
      phosphorus: 45,
      potassium: 200,
      organicCarbon: 0.85,
      electricalConductivity: 0.40,
      irrigationType: 'drip',
      waterAvailability: 'abundant',
      previousCrops: ['Wheat'],
      currentSeason: 'Kharif',
      availableBudget: 50000,
    });
    setIsAddModalOpen(true);
  };

  const openEditModal = (farm: Farm) => {
    setEditingFarm(farm);
    setFormStep(1);
    setFormData({
      name: farm.name,
      size: farm.size,
      sizeUnit: farm.sizeUnit,
      state: farm.state,
      district: farm.district,
      block: farm.block,
      village: farm.village,
      latitude: farm.latitude || 30.3165,
      longitude: farm.longitude || 78.0322,
      elevation: farm.elevation || 650,
      soilType: farm.soilType,
      soilPh: farm.soilPh,
      nitrogen: farm.nitrogen,
      phosphorus: farm.phosphorus,
      potassium: farm.potassium,
      organicCarbon: farm.organicCarbon,
      electricalConductivity: farm.electricalConductivity,
      irrigationType: farm.irrigationType,
      waterAvailability: farm.waterAvailability,
      previousCrops: farm.previousCrops,
      currentSeason: farm.currentSeason,
      availableBudget: farm.availableBudget,
    });
    setIsAddModalOpen(true);
  };

  const handleSaveForm = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert('Please enter a Farm or Plot Name');
      return;
    }

    if (editingFarm) {
      updateFarm(editingFarm.id, formData);
    } else {
      addFarm(formData);
    }
    setIsAddModalOpen(false);
    setEditingFarm(null);
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-charcoal-100">
        <div>
          <h1 className="text-2xl font-black text-forest-900 tracking-tight">
            My Registered Farms & Land Parcels
          </h1>
          <p className="text-xs text-charcoal-400 mt-1">
            Manage your agricultural land holdings, soil test cards, and micro-climate parameters
          </p>
        </div>

        <button
          onClick={openAddModal}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl font-bold text-xs bg-forest-900 hover:bg-forest-800 text-white shadow-md transition-all active:scale-95"
        >
          <Plus className="w-4 h-4 text-saffron-400" />
          <span>Register New Farm</span>
        </button>
      </div>

      {/* Farms Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {farms.map((farm) => {
          const isActive = farm.id === activeFarmId;
          return (
            <div
              key={farm.id}
              className={`rounded-3xl bg-white border transition-all duration-200 shadow-soft overflow-hidden ${
                isActive
                  ? 'border-forest-600 ring-2 ring-forest-500/20'
                  : 'border-charcoal-100 hover:border-forest-200'
              }`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-bold text-forest-900">{farm.name}</h3>
                      {isActive && (
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-forest-100 text-forest-900 border border-forest-200">
                          Active Selection
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-charcoal-500 mt-1 flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-forest-600" />
                      <span>{farm.village || 'Village'}, {farm.block} Block, {farm.district}, {farm.state}</span>
                    </p>
                  </div>

                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => openEditModal(farm)}
                      className="p-2 rounded-xl text-charcoal-500 hover:text-forest-900 hover:bg-forest-50 transition-colors"
                      title="Edit farm details"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setDeleteConfirmId(farm.id)}
                      className="p-2 rounded-xl text-charcoal-500 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                      title="Delete farm"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Key Spec Badges */}
                <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-center">
                  <div className="p-2.5 rounded-xl bg-forest-50/60 border border-forest-100">
                    <p className="text-[10px] uppercase font-bold text-charcoal-400">Total Area</p>
                    <p className="text-sm font-black text-forest-900 mt-0.5">
                      {farm.size} {farm.sizeUnit}
                    </p>
                  </div>

                  <div className="p-2.5 rounded-xl bg-forest-50/60 border border-forest-100">
                    <p className="text-[10px] uppercase font-bold text-charcoal-400">Elevation</p>
                    <p className="text-sm font-black text-forest-900 mt-0.5">
                      {farm.elevation || 640} m
                    </p>
                  </div>

                  <div className="p-2.5 rounded-xl bg-forest-50/60 border border-forest-100">
                    <p className="text-[10px] uppercase font-bold text-charcoal-400">Soil Type</p>
                    <p className="text-sm font-black text-forest-900 mt-0.5 capitalize">
                      {farm.soilType}
                    </p>
                  </div>

                  <div className="p-2.5 rounded-xl bg-forest-50/60 border border-forest-100">
                    <p className="text-[10px] uppercase font-bold text-charcoal-400">Soil pH</p>
                    <p className="text-sm font-black text-forest-900 mt-0.5">
                      {farm.soilPh}
                    </p>
                  </div>
                </div>

                {/* Soil Nutrients Breakdown */}
                <div className="mt-4 p-4 rounded-2xl bg-charcoal-50 border border-charcoal-100">
                  <p className="text-[11px] font-bold text-charcoal-400 uppercase tracking-wider mb-2">
                    Soil Nutrients & Chemical Metrics
                  </p>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <span className="text-charcoal-400 text-[11px]">Nitrogen (N):</span>
                      <p className="font-bold text-forest-900">{farm.nitrogen} kg/ha</p>
                    </div>
                    <div>
                      <span className="text-charcoal-400 text-[11px]">Phosphorus (P):</span>
                      <p className="font-bold text-forest-900">{farm.phosphorus} kg/ha</p>
                    </div>
                    <div>
                      <span className="text-charcoal-400 text-[11px]">Potassium (K):</span>
                      <p className="font-bold text-forest-900">{farm.potassium} kg/ha</p>
                    </div>
                  </div>

                  <div className="mt-3 pt-2 border-t border-charcoal-200/60 flex items-center justify-between text-xs">
                    <span>
                      Organic Carbon: <strong>{farm.organicCarbon}%</strong>
                    </span>
                    <span>
                      EC: <strong>{farm.electricalConductivity} dS/m</strong>
                    </span>
                  </div>
                </div>

                {/* Irrigation & Previous Crops */}
                <div className="mt-4 space-y-2 text-xs text-charcoal-600">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5 font-medium">
                      <Droplets className="w-3.5 h-3.5 text-forest-600" />
                      Irrigation Type:
                    </span>
                    <strong className="text-forest-900 capitalize">
                      {farm.irrigationType} ({farm.waterAvailability} water)
                    </strong>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5 font-medium">
                      <Calendar className="w-3.5 h-3.5 text-forest-600" />
                      Historical Crops:
                    </span>
                    <strong className="text-forest-900">
                      {farm.previousCrops.join(', ')}
                    </strong>
                  </div>
                </div>

                {/* Card Actions */}
                <div className="mt-5 pt-4 border-t border-charcoal-100 flex items-center justify-between">
                  {!isActive ? (
                    <button
                      onClick={() => setActiveFarmId(farm.id)}
                      className="px-4 py-2 rounded-xl text-xs font-bold bg-forest-50 hover:bg-forest-100 text-forest-900 border border-forest-200 transition-colors"
                    >
                      Set as Active Farm
                    </button>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-700">
                      <CheckCircle2 className="w-4 h-4" /> Active Farm Context
                    </span>
                  )}

                  <button
                    onClick={() => openEditModal(farm)}
                    className="text-xs font-bold text-forest-800 hover:text-forest-900 underline"
                  >
                    Edit Profile
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={deleteConfirmId !== null}
        title="Delete Farm Parcel?"
        message="Are you sure you want to remove this farm from your registry? All localized soil cards and history will be cleared."
        confirmLabel="Delete Parcel"
        isDestructive={true}
        onConfirm={() => {
          if (deleteConfirmId) {
            deleteFarm(deleteConfirmId);
            setDeleteConfirmId(null);
          }
        }}
        onCancel={() => setDeleteConfirmId(null)}
      />

      {/* ================= MULTI-STEP REGISTRATION MODAL ================= */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-charcoal-100 overflow-hidden flex flex-col max-h-[90vh]">
            {/* Modal Header */}
            <div className="p-6 border-b border-charcoal-100 flex items-center justify-between bg-forest-950 text-white">
              <div>
                <h3 className="text-lg font-bold text-white">
                  {editingFarm ? 'Edit Farm Parcel' : 'Multi-Step Farm Registration'}
                </h3>
                <p className="text-xs text-forest-300 mt-0.5">
                  Step {formStep} of 4: {formStep === 1 ? 'Location & Geography' : formStep === 2 ? 'Soil Health Card Metrics' : formStep === 3 ? 'Irrigation & Water Sources' : 'Crop History & Budget'}
                </p>
              </div>

              <button
                onClick={() => setIsAddModalOpen(false)}
                className="p-2 rounded-xl text-forest-300 hover:text-white hover:bg-forest-900 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Step Progress Bar */}
            <div className="grid grid-cols-4 border-b border-charcoal-100 text-center text-xs font-bold">
              <button
                type="button"
                onClick={() => setFormStep(1)}
                className={`py-2.5 transition-colors ${formStep === 1 ? 'bg-forest-50 text-forest-900 border-b-2 border-forest-800' : 'text-charcoal-400'}`}
              >
                1. Location
              </button>
              <button
                type="button"
                onClick={() => setFormStep(2)}
                className={`py-2.5 transition-colors ${formStep === 2 ? 'bg-forest-50 text-forest-900 border-b-2 border-forest-800' : 'text-charcoal-400'}`}
              >
                2. Soil Health
              </button>
              <button
                type="button"
                onClick={() => setFormStep(3)}
                className={`py-2.5 transition-colors ${formStep === 3 ? 'bg-forest-50 text-forest-900 border-b-2 border-forest-800' : 'text-charcoal-400'}`}
              >
                3. Water
              </button>
              <button
                type="button"
                onClick={() => setFormStep(4)}
                className={`py-2.5 transition-colors ${formStep === 4 ? 'bg-forest-50 text-forest-900 border-b-2 border-forest-800' : 'text-charcoal-400'}`}
              >
                4. Economics
              </button>
            </div>

            {/* Form Content */}
            <form onSubmit={handleSaveForm} className="p-6 overflow-y-auto flex-1 space-y-4">
              {/* STEP 1: LOCATION */}
              {formStep === 1 && (
                <div className="space-y-4 animate-fade-in text-xs">
                  <div>
                    <label className="block font-bold text-charcoal-800 mb-1">Farm / Plot Name *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Shivalik Terraced Field (Plot B)"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Farm Size</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0.1"
                        required
                        value={formData.size}
                        onChange={(e) => setFormData({ ...formData, size: parseFloat(e.target.value) || 1 })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Unit</label>
                      <select
                        value={formData.sizeUnit}
                        onChange={(e) => setFormData({ ...formData, sizeUnit: e.target.value as 'acres' | 'hectares' })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      >
                        <option value="acres">Acres</option>
                        <option value="hectares">Hectares</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">State</label>
                      <input
                        type="text"
                        value={formData.state}
                        readOnly
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 bg-charcoal-50 text-xs font-semibold text-charcoal-500"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">District</label>
                      <select
                        value={formData.district}
                        onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      >
                        {uttarakhandDistricts.map(d => (
                          <option key={d.id} value={d.name}>{d.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Block / Tehsil</label>
                      <input
                        type="text"
                        placeholder="e.g. Raipur / Bhimtal"
                        value={formData.block}
                        onChange={(e) => setFormData({ ...formData, block: e.target.value })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Village</label>
                      <input
                        type="text"
                        placeholder="e.g. Maldevta"
                        value={formData.village}
                        onChange={(e) => setFormData({ ...formData, village: e.target.value })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Latitude</label>
                      <input
                        type="number"
                        step="0.0001"
                        value={formData.latitude}
                        onChange={(e) => setFormData({ ...formData, latitude: parseFloat(e.target.value) || 0 })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Longitude</label>
                      <input
                        type="number"
                        step="0.0001"
                        value={formData.longitude}
                        onChange={(e) => setFormData({ ...formData, longitude: parseFloat(e.target.value) || 0 })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Elevation (m)</label>
                      <input
                        type="number"
                        value={formData.elevation}
                        onChange={(e) => setFormData({ ...formData, elevation: parseInt(e.target.value) || 600 })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 2: SOIL PROFILE */}
              {formStep === 2 && (
                <div className="space-y-4 animate-fade-in text-xs">
                  <div>
                    <label className="block font-bold text-charcoal-800 mb-1">Soil Texture / Type</label>
                    <select
                      value={formData.soilType}
                      onChange={(e) => setFormData({ ...formData, soilType: e.target.value as any })}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                    >
                      <option value="loamy">Loamy Soil (Fertile & balanced)</option>
                      <option value="alluvial">Alluvial Soil (River basin / Valley)</option>
                      <option value="mountain">Mountain Soil (Brown Forest soil)</option>
                      <option value="clayey">Clayey Soil (High moisture retention)</option>
                      <option value="red">Red Soil</option>
                      <option value="sandy">Sandy Loam</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Soil pH (0–14)</label>
                      <input
                        type="number"
                        step="0.1"
                        min="3.5"
                        max="9.5"
                        value={formData.soilPh}
                        onChange={(e) => setFormData({ ...formData, soilPh: parseFloat(e.target.value) || 7 })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Organic Carbon (%)</label>
                      <input
                        type="number"
                        step="0.05"
                        value={formData.organicCarbon}
                        onChange={(e) => setFormData({ ...formData, organicCarbon: parseFloat(e.target.value) || 0.8 })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Nitrogen (kg/ha)</label>
                      <input
                        type="number"
                        value={formData.nitrogen}
                        onChange={(e) => setFormData({ ...formData, nitrogen: parseInt(e.target.value) || 100 })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Phosphorus (kg/ha)</label>
                      <input
                        type="number"
                        value={formData.phosphorus}
                        onChange={(e) => setFormData({ ...formData, phosphorus: parseInt(e.target.value) || 30 })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Potassium (kg/ha)</label>
                      <input
                        type="number"
                        value={formData.potassium}
                        onChange={(e) => setFormData({ ...formData, potassium: parseInt(e.target.value) || 150 })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block font-bold text-charcoal-800 mb-1">Electrical Conductivity (dS/m)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.electricalConductivity}
                      onChange={(e) => setFormData({ ...formData, electricalConductivity: parseFloat(e.target.value) || 0.4 })}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                    />
                  </div>
                </div>
              )}

              {/* STEP 3: WATER & IRRIGATION */}
              {formStep === 3 && (
                <div className="space-y-4 animate-fade-in text-xs">
                  <div>
                    <label className="block font-bold text-charcoal-800 mb-1">Primary Irrigation System</label>
                    <select
                      value={formData.irrigationType}
                      onChange={(e) => setFormData({ ...formData, irrigationType: e.target.value as any })}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                    >
                      <option value="drip">Drip Irrigation (High efficiency)</option>
                      <option value="sprinkler">Sprinkler System</option>
                      <option value="canal">Canal / Gul Gravity Stream</option>
                      <option value="borewell">Borewell / Tube-well</option>
                      <option value="rainfed">Rainfed (Dependent on monsoons)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block font-bold text-charcoal-800 mb-1">Water Availability</label>
                    <select
                      value={formData.waterAvailability}
                      onChange={(e) => setFormData({ ...formData, waterAvailability: e.target.value as any })}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                    >
                      <option value="abundant">Abundant (Year-round stream or canal)</option>
                      <option value="moderate">Moderate (Seasonal or limited hours)</option>
                      <option value="scarce">Scarce (Severe dry season deficit)</option>
                    </select>
                  </div>
                </div>
              )}

              {/* STEP 4: CROPS & BUDGET */}
              {formStep === 4 && (
                <div className="space-y-4 animate-fade-in text-xs">
                  <div>
                    <label className="block font-bold text-charcoal-800 mb-1">Previous Crop in Rotation</label>
                    <input
                      type="text"
                      placeholder="e.g. Wheat, Basmati Rice, Potato"
                      value={formData.previousCrops.join(', ')}
                      onChange={(e) => setFormData({ ...formData, previousCrops: e.target.value.split(',').map(s => s.trim()) })}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Target Season</label>
                      <select
                        value={formData.currentSeason}
                        onChange={(e) => setFormData({ ...formData, currentSeason: e.target.value as any })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      >
                        <option value="Kharif">Kharif (Monsoon / Autumn)</option>
                        <option value="Rabi">Rabi (Winter / Spring)</option>
                        <option value="Zaid">Zaid (Summer)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block font-bold text-charcoal-800 mb-1">Available Budget (₹)</label>
                      <input
                        type="number"
                        step="5000"
                        value={formData.availableBudget}
                        onChange={(e) => setFormData({ ...formData, availableBudget: parseInt(e.target.value) || 50000 })}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs font-semibold focus:ring-2 focus:ring-forest-600 focus:outline-none"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Footer Controls */}
              <div className="pt-4 border-t border-charcoal-100 flex items-center justify-between">
                {formStep > 1 ? (
                  <button
                    type="button"
                    onClick={() => setFormStep(formStep - 1)}
                    className="px-4 py-2 rounded-xl text-xs font-bold text-charcoal-600 hover:bg-charcoal-50"
                  >
                    Back
                  </button>
                ) : <div />}

                <div className="flex items-center gap-2">
                  {formStep < 4 ? (
                    <button
                      type="button"
                      onClick={() => setFormStep(formStep + 1)}
                      className="px-5 py-2 rounded-xl text-xs font-bold bg-forest-900 text-white hover:bg-forest-800"
                    >
                      Next Step
                    </button>
                  ) : (
                    <button
                      type="submit"
                      className="px-6 py-2 rounded-xl text-xs font-bold bg-saffron-500 hover:bg-saffron-400 text-charcoal-900 shadow-md"
                    >
                      {editingFarm ? 'Save Changes' : 'Complete Registration'}
                    </button>
                  )}
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
