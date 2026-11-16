import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  MapPin,
  Sparkles,
  Bug,
  Bot,
  Compass,
  Repeat,
  CloudSun,
  TrendingUp,
  Satellite,
  BarChart3,
  MessageSquareHeart,
  Settings,
  HelpCircle,
  X,
  ChevronRight,
  Sprout,
  UserCheck
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  isCollapsed: boolean;
  setIsCollapsed: (val: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  isCollapsed,
}) => {
  const { activeFarm, t } = useApp();
  const location = useLocation();

  const navigationSections = [
    {
      title: 'OVERVIEW',
      items: [
        { label: t('nav.dashboard'), path: '/dashboard', icon: LayoutDashboard },
      ],
    },
    {
      title: 'FARM MANAGEMENT',
      items: [
        { label: t('nav.farms'), path: '/farms', icon: Sprout },
        { label: t('nav.farmerProfile'), path: '/farmer-profile', icon: UserCheck },
        { label: t('nav.regionIntel'), path: '/region-intelligence', icon: MapPin },
      ],
    },
    {
      title: 'AI INTELLIGENCE',
      items: [
        { label: t('nav.cropRec'), path: '/crop-recommendation', icon: Sparkles, badge: 'Ensemble' },
        { label: t('nav.disease'), path: '/advisory', icon: Bug, badge: 'IPM' },
        { label: t('nav.assistant'), path: '/ai-assistant', icon: Bot, badge: 'RAG' },
        { label: t('nav.advisor'), path: '/smart-advisor', icon: Compass },
        { label: t('nav.rotation'), path: '/crop-rotation', icon: Repeat },
      ],
    },
    {
      title: 'FIELD INTELLIGENCE',
      items: [
        { label: t('nav.weather'), path: '/weather', icon: CloudSun },
        { label: t('nav.market'), path: '/market-intelligence', icon: TrendingUp },
        { label: t('nav.satellite'), path: '/satellite-monitoring', icon: Satellite, badge: 'Preview' },
      ],
    },
    {
      title: 'PERFORMANCE',
      items: [
        { label: t('nav.analytics'), path: '/analytics', icon: BarChart3 },
        { label: t('nav.feedback'), path: '/feedback', icon: MessageSquareHeart },
      ],
    },
    {
      title: 'SYSTEM',
      items: [
        { label: t('nav.settings'), path: '/settings', icon: Settings },
        { label: 'Help & Support', path: '/help', icon: HelpCircle },
      ],
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-charcoal-900/60 backdrop-blur-sm lg:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col bg-forest-950 text-white transition-all duration-300 border-r border-forest-900 ${
          isCollapsed ? 'w-20' : 'w-64 xl:w-72'
        } ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between px-5 h-16 border-b border-forest-900/80 bg-forest-950/90">
          <NavLink to="/dashboard" className="flex items-center gap-3 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-forest-500/20 border border-forest-400/30 flex items-center justify-center text-saffron-400 shrink-0">
              <Sprout className="w-6 h-6" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col">
                <span className="text-lg font-black tracking-tight text-white flex items-center gap-1">
                  Kisan<span className="text-saffron-400">Mitra</span>
                </span>
                <span className="text-[10px] uppercase font-semibold tracking-wider text-forest-300">
                  Decision Intelligence
                </span>
              </div>
            )}
          </NavLink>

          {/* Mobile Close Button */}
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-forest-300 hover:text-white hover:bg-forest-900 lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Active Farm Context Pill */}
        {!isCollapsed && (
          <div className="mx-4 my-3 p-2.5 rounded-xl bg-forest-900/70 border border-forest-800/80 flex items-center justify-between">
            <div className="flex items-center gap-2 overflow-hidden">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0" />
              <div className="truncate">
                <p className="text-[10px] uppercase font-bold text-forest-300">Active Field</p>
                <p className="text-xs font-bold text-white truncate">{activeFarm.name}</p>
              </div>
            </div>
            <NavLink
              to="/farms"
              className="text-forest-300 hover:text-saffron-300 p-1"
              title="Manage farms"
            >
              <ChevronRight className="w-4 h-4" />
            </NavLink>
          </div>
        )}

        {/* Navigation Items List */}
        <div className="flex-1 overflow-y-auto px-3 py-3 space-y-6">
          {navigationSections.map((sec, sIdx) => (
            <div key={sIdx}>
              {!isCollapsed && (
                <p className="px-3 text-[10px] font-black uppercase tracking-wider text-forest-400/80 mb-1.5">
                  {sec.title}
                </p>
              )}
              <div className="space-y-0.5">
                {sec.items.map((item, iIdx) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <NavLink
                      key={iIdx}
                      to={item.path}
                      onClick={onClose}
                      className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all group ${
                        isActive
                          ? 'bg-forest-700/80 text-white shadow-sm border border-forest-500/40'
                          : 'text-forest-200 hover:bg-forest-900/60 hover:text-white'
                      }`}
                      title={isCollapsed ? item.label : undefined}
                    >
                      <Icon
                        className={`w-4 h-4 shrink-0 transition-colors ${
                          isActive
                            ? 'text-saffron-400'
                            : 'text-forest-300 group-hover:text-white'
                        }`}
                      />
                      {!isCollapsed && (
                        <div className="flex-1 flex items-center justify-between truncate">
                          <span className="truncate">{item.label}</span>
                          {item.badge && (
                            <span
                              className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                                item.badge === 'Ensemble'
                                  ? 'bg-saffron-500/20 text-saffron-300 border border-saffron-500/30'
                                  : item.badge === 'Vision'
                                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                  : 'bg-forest-800 text-forest-300'
                              }`}
                            >
                              {item.badge}
                            </span>
                          )}
                        </div>
                      )}
                    </NavLink>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Footer info */}
        <div className="p-3 border-t border-forest-900/80 bg-forest-950/70">
          {!isCollapsed ? (
            <div className="px-2 py-1 text-[11px] text-forest-400 flex items-center justify-between">
              <span>v1.0 • Uttarakhand Focus</span>
              <NavLink to="/" className="text-saffron-400 hover:underline font-medium">
                Public Site
              </NavLink>
            </div>
          ) : (
            <div className="flex justify-center text-[10px] text-forest-400">v1.0</div>
          )}
        </div>
      </aside>
    </>
  );
};
