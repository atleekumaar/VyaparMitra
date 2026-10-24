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
  X,
  Trophy,
  Volume2,
  Wifi,
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

interface NavItemConfig {
  id: NavTab;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  section?: 'overview' | 'operations' | 'intelligence' | 'system';
  badge?: string;
  isCopilot?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onTabChange,
  pendingActionsCount = 0,
  isOpenMobile,
  onToggleMobile,
}) => {
  const { t } = useLanguage();

  const navItems: NavItemConfig[] = [
    // Overview
    { id: 'dashboard', label: t('nav_dashboard', 'Dashboard'), icon: LayoutDashboard, section: 'overview' },
    { id: 'analytics', label: t('nav_analytics', 'Analytics'), icon: BarChart3, section: 'overview' },
    { id: 'compare', label: t('nav_compare', 'Peer Benchmark'), icon: Trophy, section: 'overview' },

    // Operations
    { id: 'products', label: t('nav_products', 'Products'), icon: Package, section: 'operations' },
    { id: 'customers', label: t('nav_customers', 'Customers'), icon: Users, section: 'operations' },
    { id: 'forecasts', label: t('nav_forecasts', 'Forecasts'), icon: TrendingUp, section: 'operations' },

    // Intelligence
    {
      id: 'recommendations',
      label: t('nav_recommendations', 'Action Center'),
      icon: Sparkles,
      badge: pendingActionsCount > 0 ? String(pendingActionsCount) : undefined,
      section: 'intelligence',
    },
    {
      id: 'copilot',
      label: t('nav_copilot', 'AI Copilot'),
      icon: Bot,
      isCopilot: true,
      section: 'intelligence',
    },

    // System
    { id: 'settings', label: t('nav_settings', 'Settings'), icon: Settings, section: 'system' },
  ];

  const renderSectionHeader = (title: string) => (
    <div className="px-3 pt-4 pb-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
      {title}
    </div>
  );

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs lg:hidden transition-opacity"
          onClick={onToggleMobile}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 border-r border-slate-200/80 dark:border-slate-800 flex flex-col transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full'
        } shadow-lg lg:shadow-none`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8.5 h-8.5 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-xs select-none">
              VM
            </div>
            <div>
              <div className="flex items-center gap-1">
                <span className="font-bold text-base text-slate-900 dark:text-white tracking-tight">
                  Vyapar<span className="text-blue-600 dark:text-blue-400">Mitra</span>
                </span>
              </div>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="text-[10px] font-medium text-slate-500 dark:text-slate-400">
                  Merchant Portal
                </span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              </div>
            </div>
          </div>
          <button
            onClick={onToggleMobile}
            className="lg:hidden text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-white p-1 rounded-md"
            aria-label="Close navigation menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-3 space-y-0.5 overflow-y-auto">
          {navItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            const prevSection = index > 0 ? navItems[index - 1].section : null;
            const isNewSection = item.section && item.section !== prevSection;

            return (
              <React.Fragment key={item.id}>
                {isNewSection && (
                  <>
                    {item.section === 'operations' && renderSectionHeader('Operations')}
                    {item.section === 'intelligence' && renderSectionHeader('AI & Insights')}
                    {item.section === 'system' && renderSectionHeader('Preferences')}
                  </>
                )}

                <button
                  onClick={() => {
                    onTabChange(item.id);
                    if (isOpenMobile) onToggleMobile();
                  }}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors group relative ${
                    isActive
                      ? item.isCopilot
                        ? 'bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 font-semibold'
                        : 'bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 font-semibold'
                      : item.isCopilot
                      ? 'text-slate-600 dark:text-slate-400 hover:bg-purple-50/50 dark:hover:bg-purple-950/20 hover:text-purple-700 dark:hover:text-purple-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Icon
                      className={`w-4 h-4 shrink-0 transition-colors ${
                        isActive
                          ? item.isCopilot
                            ? 'text-purple-600 dark:text-purple-400'
                            : 'text-blue-600 dark:text-blue-400'
                          : item.isCopilot
                          ? 'text-purple-500/80 group-hover:text-purple-600 dark:group-hover:text-purple-300'
                          : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300'
                      }`}
                    />
                    <span className="truncate">{item.label}</span>
                  </div>

                  {item.badge && (
                    <span className="px-1.5 py-0.5 text-[11px] font-semibold rounded-full bg-blue-600 text-white shrink-0">
                      {item.badge}
                    </span>
                  )}
                </button>
              </React.Fragment>
            );
          })}
        </nav>

        {/* Smart Soundbox Status Bar */}
        <div className="p-3 border-t border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
          <div className="rounded-lg p-2.5 bg-white dark:bg-slate-850 border border-slate-200/80 dark:border-slate-800 text-slate-800 dark:text-slate-200 shadow-2xs">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 min-w-0">
                <div className="w-6 h-6 rounded-md bg-blue-50 dark:bg-blue-950/50 border border-blue-200/60 dark:border-blue-800/60 flex items-center justify-center text-blue-600 dark:text-blue-400 shrink-0">
                  <Volume2 className="w-3.5 h-3.5" />
                </div>
                <div className="min-w-0">
                  <span className="text-xs font-semibold text-slate-900 dark:text-white block leading-tight truncate">
                    Smart Soundbox
                  </span>
                  <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Online &bull; 4G
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-1 text-[10px] text-slate-400 shrink-0">
                <Wifi className="w-3 h-3 text-blue-600 dark:text-blue-400" />
                <span>Sync</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
