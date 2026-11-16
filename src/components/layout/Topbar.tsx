import React, { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Menu,
  ChevronDown,
  Globe,
  Bell,
  Sun,
  Plus,
  MapPin,
  Check,
  User,
  LogOut,
  ExternalLink,
  Settings,
  Sparkles,
  Sprout
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

interface TopbarProps {
  onOpenMobileSidebar: () => void;
  isCollapsed: boolean;
  setIsCollapsed: (val: boolean) => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  onOpenMobileSidebar,
}) => {
  const {
    farms,
    activeFarmId,
    setActiveFarmId,
    activeFarm,
    profile,
    language,
    setLanguage,
    weather,
    notifications,
    markNotificationAsRead,
    clearAllNotifications,
  } = useApp();

  const navigate = useNavigate();

  const [farmMenuOpen, setFarmMenuOpen] = useState(false);
  const [langMenuOpen, setLangMenuOpen] = useState(false);
  const [notifyOpen, setNotifyOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const farmRef = useRef<HTMLDivElement>(null);
  const langRef = useRef<HTMLDivElement>(null);
  const notifyRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter(n => !n.read).length;

  // Close menus on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (farmRef.current && !farmRef.current.contains(e.target as Node)) setFarmMenuOpen(false);
      if (langRef.current && !langRef.current.contains(e.target as Node)) setLangMenuOpen(false);
      if (notifyRef.current && !notifyRef.current.contains(e.target as Node)) setNotifyOpen(false);
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) setProfileOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/95 backdrop-blur-md border-b border-charcoal-100 px-4 sm:px-6 flex items-center justify-between">
      {/* Left Area: Mobile Menu & Active Farm Selector */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="p-2 rounded-xl text-charcoal-600 hover:text-forest-900 hover:bg-forest-50 lg:hidden transition-colors"
          aria-label="Open Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Farm Switcher Dropdown */}
        <div className="relative" ref={farmRef}>
          <button
            onClick={() => setFarmMenuOpen(!farmMenuOpen)}
            className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-forest-50/70 hover:bg-forest-100/70 border border-forest-200/80 text-forest-900 transition-all text-left"
          >
            <div className="w-7 h-7 rounded-lg bg-forest-900 text-white flex items-center justify-center shrink-0">
              <Sprout className="w-4 h-4 text-saffron-400" />
            </div>
            <div className="hidden sm:block">
              <p className="text-[10px] uppercase font-bold text-charcoal-400 leading-none">
                Selected Farm
              </p>
              <p className="text-xs font-bold text-forest-900 max-w-[150px] md:max-w-[200px] truncate leading-tight mt-0.5">
                {activeFarm.name}
              </p>
            </div>
            <ChevronDown className="w-4 h-4 text-forest-700" />
          </button>

          {/* Farm Switcher Dropdown Menu */}
          {farmMenuOpen && (
            <div className="absolute top-full left-0 mt-2 w-72 bg-white rounded-2xl shadow-xl border border-charcoal-100 p-2 z-50 animate-fade-in">
              <div className="px-3 py-2 border-b border-charcoal-100 mb-1">
                <p className="text-xs font-bold text-forest-900">Switch Registered Farm</p>
                <p className="text-[11px] text-charcoal-400">Context applies across recommendations & weather</p>
              </div>

              <div className="max-h-56 overflow-y-auto space-y-1">
                {farms.map((farm) => {
                  const isCurrent = farm.id === activeFarmId;
                  return (
                    <button
                      key={farm.id}
                      onClick={() => {
                        setActiveFarmId(farm.id);
                        setFarmMenuOpen(false);
                      }}
                      className={`w-full flex items-center justify-between p-2.5 rounded-xl text-xs transition-all ${
                        isCurrent
                          ? 'bg-forest-50 text-forest-900 font-bold border border-forest-200'
                          : 'hover:bg-charcoal-50 text-charcoal-700'
                      }`}
                    >
                      <div className="text-left truncate mr-2">
                        <p className="truncate font-semibold">{farm.name}</p>
                        <p className="text-[11px] text-charcoal-400">
                          {farm.size} {farm.sizeUnit} • {farm.district}, {farm.state}
                        </p>
                      </div>
                      {isCurrent && <Check className="w-4 h-4 text-forest-700 shrink-0" />}
                    </button>
                  );
                })}
              </div>

              <div className="mt-2 pt-2 border-t border-charcoal-100">
                <button
                  onClick={() => {
                    setFarmMenuOpen(false);
                    navigate('/farms?add=true');
                  }}
                  className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-xs font-bold bg-forest-900 hover:bg-forest-800 text-white transition-all"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Register New Farm
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right Area: Weather pill, Language, Notifications, Actions, Profile */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Weather Mini-Pill (Clickable to /weather) */}
        <NavLink
          to="/weather"
          className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-charcoal-50 hover:bg-forest-50 border border-charcoal-100 text-charcoal-700 hover:text-forest-900 transition-all text-xs"
          title="View detailed 7-day agricultural weather forecast"
        >
          <Sun className="w-4 h-4 text-saffron-500 animate-spin-slow" />
          <span className="font-semibold">{weather.location.split(' ')[0]}: {weather.temperature}°C</span>
          <span className="text-[11px] text-charcoal-400">({weather.condition})</span>
        </NavLink>

        {/* Quick AI Recommendation Button */}
        <NavLink
          to="/crop-recommendation"
          className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-saffron-500 hover:bg-saffron-400 text-charcoal-900 shadow-sm transition-all active:scale-95"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>AI Crop Plan</span>
        </NavLink>

        {/* Language Selector (EN / HI) */}
        <div className="relative" ref={langRef}>
          <button
            onClick={() => setLangMenuOpen(!langMenuOpen)}
            className="flex items-center gap-1.5 p-2 rounded-xl text-xs font-bold text-charcoal-700 hover:bg-charcoal-50 border border-charcoal-100 transition-colors"
            title="Switch Language"
          >
            <Globe className="w-4 h-4 text-forest-700" />
            <span className="uppercase">{language}</span>
            <ChevronDown className="w-3 h-3 text-charcoal-400" />
          </button>

          {langMenuOpen && (
            <div className="absolute top-full right-0 mt-2 w-36 bg-white rounded-xl shadow-lg border border-charcoal-100 p-1.5 z-50 animate-fade-in text-xs font-semibold">
              <button
                onClick={() => {
                  setLanguage('en');
                  setLangMenuOpen(false);
                }}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg ${
                  language === 'en' ? 'bg-forest-50 text-forest-900 font-bold' : 'hover:bg-charcoal-50 text-charcoal-700'
                }`}
              >
                <span>English</span>
                {language === 'en' && <Check className="w-3.5 h-3.5 text-forest-700" />}
              </button>
              <button
                onClick={() => {
                  setLanguage('hi');
                  setLangMenuOpen(false);
                }}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg ${
                  language === 'hi' ? 'bg-forest-50 text-forest-900 font-bold' : 'hover:bg-charcoal-50 text-charcoal-700'
                }`}
              >
                <span>हिन्दी (Hindi)</span>
                {language === 'hi' && <Check className="w-3.5 h-3.5 text-forest-700" />}
              </button>
            </div>
          )}
        </div>

        {/* Notifications Bell Dropdown */}
        <div className="relative" ref={notifyRef}>
          <button
            onClick={() => setNotifyOpen(!notifyOpen)}
            className="relative p-2 rounded-xl text-charcoal-600 hover:text-forest-900 hover:bg-forest-50 border border-charcoal-100 transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-saffron-500 text-charcoal-900 text-[10px] font-black flex items-center justify-center border-2 border-white">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Flyout */}
          {notifyOpen && (
            <div className="absolute top-full right-0 mt-2 w-80 sm:w-96 bg-white rounded-2xl shadow-xl border border-charcoal-100 p-3 z-50 animate-fade-in">
              <div className="flex items-center justify-between px-2 py-1.5 border-b border-charcoal-100 mb-2">
                <div className="flex items-center gap-1.5">
                  <h4 className="text-xs font-bold text-forest-900">Notifications & Alerts</h4>
                  {unreadCount > 0 && (
                    <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-saffron-100 text-saffron-800">
                      {unreadCount} new
                    </span>
                  )}
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={clearAllNotifications}
                    className="text-[11px] font-semibold text-forest-700 hover:underline"
                  >
                    Mark all as read
                  </button>
                )}
              </div>

              <div className="max-h-72 overflow-y-auto space-y-2">
                {notifications.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => {
                      markNotificationAsRead(item.id);
                      if (item.link) {
                        setNotifyOpen(false);
                        navigate(item.link);
                      }
                    }}
                    className={`p-2.5 rounded-xl text-xs cursor-pointer transition-all border ${
                      item.read
                        ? 'bg-white border-charcoal-100 opacity-75 hover:opacity-100'
                        : 'bg-forest-50/70 border-forest-100 font-medium'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-1">
                      <p className="font-bold text-forest-900 text-xs">{item.title}</p>
                      <span className="text-[10px] text-charcoal-400 shrink-0">{item.timestamp}</span>
                    </div>
                    <p className="text-[11px] text-charcoal-600 mt-1 leading-snug">
                      {item.message}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Farmer Profile Avatar & Dropdown */}
        <div className="relative" ref={profileRef}>
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex items-center gap-2 p-1 pl-1.5 rounded-xl hover:bg-charcoal-50 border border-transparent hover:border-charcoal-100 transition-all"
          >
            <img
              src={profile.avatarUrl}
              alt={profile.name}
              className="w-8 h-8 rounded-lg object-cover ring-1 ring-forest-600/30"
            />
            <div className="hidden xl:block text-left">
              <p className="text-xs font-bold text-forest-900 leading-none truncate max-w-[120px]">
                {profile.name}
              </p>
              <p className="text-[10px] text-charcoal-400 mt-0.5">Hill Farmer</p>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-charcoal-400 hidden sm:block" />
          </button>

          {profileOpen && (
            <div className="absolute top-full right-0 mt-2 w-64 bg-white rounded-2xl shadow-xl border border-charcoal-100 p-2 z-50 animate-fade-in text-xs">
              <div className="p-3 border-b border-charcoal-100 bg-forest-50/50 rounded-xl mb-1.5">
                <p className="font-bold text-forest-900">{profile.name}</p>
                <p className="text-[11px] text-charcoal-500">{profile.phone}</p>
                <div className="mt-2 flex items-center gap-1.5 text-[11px] text-forest-700 font-semibold">
                  <MapPin className="w-3.5 h-3.5" />
                  <span>{profile.village}, {profile.district}</span>
                </div>
              </div>

              <NavLink
                to="/farmer-profile"
                onClick={() => setProfileOpen(false)}
                className="flex items-center gap-2 px-3 py-2 rounded-xl text-charcoal-700 hover:bg-charcoal-50 transition-colors font-medium"
              >
                <User className="w-4 h-4 text-forest-700" />
                <span>Farmer Profile & KYC</span>
              </NavLink>

              <NavLink
                to="/settings"
                onClick={() => setProfileOpen(false)}
                className="flex items-center gap-2 px-3 py-2 rounded-xl text-charcoal-700 hover:bg-charcoal-50 transition-colors font-medium"
              >
                <Settings className="w-4 h-4 text-forest-700" />
                <span>Account & Preferences</span>
              </NavLink>

              <NavLink
                to="/"
                onClick={() => setProfileOpen(false)}
                className="flex items-center gap-2 px-3 py-2 rounded-xl text-charcoal-700 hover:bg-charcoal-50 transition-colors font-medium"
              >
                <ExternalLink className="w-4 h-4 text-forest-700" />
                <span>Public Website</span>
              </NavLink>

              <div className="mt-1 pt-1 border-t border-charcoal-100">
                <button
                  onClick={() => {
                    setProfileOpen(false);
                    navigate('/');
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-rose-600 hover:bg-rose-50 transition-colors font-semibold"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Exit to Landing Page</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
