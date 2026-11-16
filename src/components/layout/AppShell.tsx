import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { useApp } from '../../context/AppContext';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export const AppShell: React.FC = () => {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { toast } = useApp();

  return (
    <div className="min-h-screen bg-kisan-bg flex">
      {/* Sidebar */}
      <Sidebar
        isOpen={mobileSidebarOpen}
        onClose={() => setMobileSidebarOpen(false)}
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          isCollapsed ? 'lg:pl-20' : 'lg:pl-64 xl:pl-72'
        }`}
      >
        <Topbar
          onOpenMobileSidebar={() => setMobileSidebarOpen(true)}
          isCollapsed={isCollapsed}
          setIsCollapsed={setIsCollapsed}
        />

        {/* Global Toast Notification */}
        {toast && (
          <div className="fixed bottom-6 right-6 z-50 animate-bounce-short">
            <div
              className={`flex items-center gap-2.5 px-4 py-3 rounded-2xl shadow-xl border text-xs font-semibold backdrop-blur-md ${
                toast.type === 'success'
                  ? 'bg-emerald-900/95 text-white border-emerald-500/30'
                  : toast.type === 'error'
                  ? 'bg-rose-900/95 text-white border-rose-500/30'
                  : 'bg-forest-900/95 text-white border-forest-500/30'
              }`}
            >
              {toast.type === 'success' && <CheckCircle2 className="w-4 h-4 text-emerald-300" />}
              {toast.type === 'error' && <AlertCircle className="w-4 h-4 text-rose-300" />}
              {toast.type === 'info' && <Info className="w-4 h-4 text-saffron-300" />}
              <span>{toast.message}</span>
            </div>
          </div>
        )}

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
