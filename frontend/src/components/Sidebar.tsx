import React from 'react';
import {
  LayoutDashboard,
  BarChart3,
  Package,
  Users,
  TrendingUp,
  Sparkles,
  Bot,
  Settings,
  HelpCircle,
  X,
  Trophy,
  Volume2,
  Wifi,
  BatteryCharging,
  CheckCircle2,
} from 'lucide-react';

import { useLanguage } from '../i18n/LanguageContext';

export type NavTab =
  | 'dashboard'
  | 'compare'
  | 'analytics'
  | 'products'
  | 'customers'
  | 'forecasts'
  | 'recommendations'
  | 'copilot'
  | 'settings';

interface SidebarProps {
  currentTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  pendingActionsCount?: number;
  isOpenMobile: boolean;
  onToggleMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onTabChange,
  pendingActionsCount = 0,
  isOpenMobile,
  onToggleMobile,
}) => {
  const { t } = useLanguage();

  const navItems = [
    { id: 'dashboard', label: t('nav_dashboard', 'Dashboard'), icon: LayoutDashboard },
    { id: 'compare', label: t('nav_compare', 'Peers / Compare'), icon: Trophy, isNew: true },
    { id: 'analytics', label: t('nav_analytics', 'Analytics'), icon: BarChart3 },
    { id: 'products', label: t('nav_products', 'Products'), icon: Package },
    { id: 'customers', label: t('nav_customers', 'Customers'), icon: Users },
    { id: 'forecasts', label: t('nav_forecasts', 'Forecasts'), icon: TrendingUp },
    {
      id: 'recommendations',
      label: t('nav_recommendations', 'Action Center'),
      icon: Sparkles,
      badge: pendingActionsCount > 0 ? String(pendingActionsCount) : undefined,
    },
    { id: 'copilot', label: t('nav_copilot', 'AI Copilot'), icon: Bot, isHighlight: true },
    { id: 'settings', label: t('nav_settings', 'Settings'), icon: Settings },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 lg:hidden backdrop-blur-xs"
          onClick={onToggleMobile}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-gradient-to-b from-[#002970] via-[#00225D] to-[#001438] text-white border-r border-[#003882] flex flex-col transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full'
        } shadow-2xl lg:shadow-none`}
      >
        {/* Brand Header */}
        <div className="h-20 flex items-center justify-between px-5 border-b border-white/10 bg-[#001F58]/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00BAF2] to-[#008AC9] flex items-center justify-center text-white font-black text-base shadow-md shadow-[#00BAF2]/30 ring-2 ring-white/20">
              VM
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-xl text-white tracking-tight leading-none">
                  Vyapar<span className="text-[#00BAF2]">Mitra</span>
                </span>
              </div>
              <div className="flex items-center gap-1 mt-1">
                <span className="text-[9px] font-bold tracking-wider text-[#00BAF2] bg-[#00BAF2]/15 px-1.5 py-0.5 rounded border border-[#00BAF2]/30 uppercase">
                  Paytm Partner
                </span>
                <span className="w-1.5 h-1.5 rounded-full bg-[#00B970] animate-pulse" />
              </div>
            </div>
          </div>
          <button
            onClick={onToggleMobile}
            className="lg:hidden text-white/70 hover:text-white p-1 rounded-md"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => {
                  onTabChange(item.id as NavTab);
                  if (isOpenMobile) onToggleMobile();
                }}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group relative ${
                  isActive
                    ? 'bg-gradient-to-r from-[#00BAF2] to-[#009EDB] text-white font-bold shadow-lg shadow-[#00BAF2]/30 translate-x-1'
                    : 'text-blue-100/75 hover:bg-white/10 hover:text-white hover:translate-x-0.5'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center transition-colors ${
                      isActive
                        ? 'bg-white/20 text-white'
                        : 'bg-white/5 text-blue-200 group-hover:bg-white/10 group-hover:text-white'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <span>{item.label}</span>
                </div>

                <div className="flex items-center gap-1.5">
                  {item.badge && (
                    <span className="px-2 py-0.5 text-[11px] font-extrabold rounded-full bg-red-500 text-white shadow-xs">
                      {item.badge}
                    </span>
                  )}
                  {item.isHighlight && !item.badge && (
                    <span className="px-2 py-0.5 text-[10px] font-black uppercase tracking-wider rounded-md bg-[#00B970] text-white shadow-xs">
                      HINDI AI
                    </span>
                  )}
                  {item.isNew && (
                    <span className="px-1.5 py-0.5 text-[9px] font-black uppercase tracking-wider rounded bg-[#FFB800] text-[#002970]">
                      TOP
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </nav>

        {/* Paytm Soundbox 4.0 Live Status Widget */}
        <div className="p-3.5 border-t border-white/10 bg-[#001740]/80">
          <div className="rounded-xl p-3 bg-gradient-to-br from-[#002B7A] to-[#001F58] border border-[#00BAF2]/30 text-white shadow-md relative overflow-hidden">
            {/* Background subtle soundwave illustration */}
            <div className="absolute -right-3 -bottom-3 opacity-10 pointer-events-none">
              <Volume2 className="w-20 h-20 text-[#00BAF2]" />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-md bg-[#00BAF2]/20 border border-[#00BAF2]/40 flex items-center justify-center text-[#00BAF2]">
                  <Volume2 className="w-3.5 h-3.5 text-[#00BAF2]" />
                </div>
                <div>
                  <span className="text-xs font-bold text-white block leading-tight">Paytm Soundbox 4.0</span>
                  <span className="text-[10px] text-[#00B970] font-semibold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#00B970] animate-ping" />
                    Online &bull; 4G SIM
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-1 text-[10px] text-blue-200">
                <Wifi className="w-3 h-3 text-[#00BAF2]" />
                <span>Full</span>
              </div>
            </div>

            <div className="mt-2.5 pt-2 border-t border-white/10 flex items-center justify-between text-[10px] text-blue-200">
              <span>Instant UPI Audio Alert</span>
              <span className="text-[#00BAF2] font-bold">100% Sync</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
