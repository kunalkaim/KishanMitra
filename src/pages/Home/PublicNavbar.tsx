import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Sprout, Menu, X, Globe, ArrowRight, ShieldCheck } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const PublicNavbar: React.FC<{ onOpenAuth: () => void }> = ({ onOpenAuth }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { language, setLanguage } = useApp();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-forest-950/80 backdrop-blur-md border-b border-forest-800/40 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand Logo */}
        <NavLink to="/" className="flex items-center gap-3 group">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-forest-500 to-forest-700 border border-forest-400/40 flex items-center justify-center text-saffron-300 shadow-md transition-transform group-hover:scale-105">
            <Sprout className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xl font-extrabold tracking-tight text-white flex items-center gap-1">
              Kisan<span className="text-saffron-400">Mitra</span>
            </span>
            <p className="text-[10px] uppercase font-bold tracking-widest text-forest-300">
              Smart Agri-Intelligence
            </p>
          </div>
        </NavLink>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-forest-100">
          <NavLink to="/" className={({ isActive }) => isActive ? 'text-saffron-400' : 'hover:text-white transition-colors'}>
            Home
          </NavLink>
          <a href="#about" className="hover:text-white transition-colors">
            About KisanMitra
          </a>
          <a href="#features" className="hover:text-white transition-colors">
            Core Features
          </a>
          <a href="#how-it-works" className="hover:text-white transition-colors">
            How It Works
          </a>
          <a href="#impact" className="hover:text-white transition-colors">
            Regional Focus
          </a>
          <a href="#contact" className="hover:text-white transition-colors">
            Helpline & Support
          </a>
        </nav>

        {/* Right CTA Area */}
        <div className="hidden sm:flex items-center gap-3">
          {/* Language Toggle */}
          <button
            onClick={() => setLanguage(language === 'en' ? 'hi' : 'en')}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-bold bg-forest-900/80 hover:bg-forest-800 border border-forest-700/60 transition-colors"
          >
            <Globe className="w-3.5 h-3.5 text-saffron-400" />
            <span>{language === 'en' ? 'हिन्दी' : 'English'}</span>
          </button>

          {/* Farmer Portal CTA */}
          <NavLink
            to="/dashboard"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-xs bg-saffron-500 hover:bg-saffron-400 text-charcoal-900 shadow-lg shadow-saffron-500/20 transition-all active:scale-95"
          >
            <span>Farmer Portal</span>
            <ArrowRight className="w-4 h-4" />
          </NavLink>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 rounded-xl text-forest-200 hover:text-white hover:bg-forest-900 md:hidden"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-forest-950 border-b border-forest-800 px-5 py-6 space-y-4 animate-fade-in text-sm font-semibold">
          <NavLink
            to="/"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-white py-1"
          >
            Home
          </NavLink>
          <a
            href="#about"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-forest-200 hover:text-white py-1"
          >
            About KisanMitra
          </a>
          <a
            href="#features"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-forest-200 hover:text-white py-1"
          >
            Core Features
          </a>
          <a
            href="#how-it-works"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-forest-200 hover:text-white py-1"
          >
            How It Works
          </a>
          <a
            href="#contact"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-forest-200 hover:text-white py-1"
          >
            Helpline & Contact
          </a>

          <div className="pt-4 border-t border-forest-900 flex flex-col gap-3">
            <button
              onClick={() => {
                setLanguage(language === 'en' ? 'hi' : 'en');
                setMobileMenuOpen(false);
              }}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-bold bg-forest-900 text-white"
            >
              <Globe className="w-4 h-4 text-saffron-400" />
              <span>Switch to {language === 'en' ? 'हिन्दी (Hindi)' : 'English'}</span>
            </button>
            <NavLink
              to="/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full py-3 rounded-xl font-bold text-xs bg-saffron-500 text-charcoal-900 text-center shadow-md"
            >
              Enter Farmer Dashboard
            </NavLink>
          </div>
        </div>
      )}
    </header>
  );
};
