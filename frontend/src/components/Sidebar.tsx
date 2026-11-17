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
  Store,
  LogOut,
  Wallet,
  Truck,
  Printer,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import { UserProfile } from '../types';

export type NavTab =
  | 'dashboard'
  | 'compare'
  | 'analytics'
  | 'products'
  | 'customers'
  | 'suppliers'
  | 'finance'
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
  userProfile?: UserProfile | null;
  onLogout?: () => void;
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
  userProfile,
  onLogout,
}) => {
  const { t, language } = useLanguage();

  const navItems: NavItemConfig[] = [
    // Overview
    { id: 'dashboard', label: t('nav_dashboard', 'Dashboard'), icon: LayoutDashboard, section: 'overview' },
    { id: 'analytics', label: t('nav_analytics', 'Analytics'), icon: BarChart3, section: 'overview' },
    { id: 'compare', label: t('nav_compare', 'Peer Benchmark'), icon: Trophy, section: 'overview' },

    // Operations
    { id: 'products', label: t('nav_products', 'Products & Stock'), icon: Package, section: 'operations' },
    { id: 'customers', label: t('nav_customers', 'Customers & Khata'), icon: Users, section: 'operations' },
    { id: 'suppliers', label: language === 'hindi' ? 'सप्लायर व खरीद' : 'Suppliers & PO', icon: Truck, section: 'operations' },
    { id: 'finance', label: language === 'hindi' ? 'वित्त व लाभ-हानि' : 'Finance & P&L', icon: Wallet, section: 'operations' },
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
    <div className="px-3 pt-3.5 pb-1 text-[11px] font-bold uppercase tracking-wider text-text-subtle">
      {title}
    </div>
  );

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-xs lg:hidden transition-opacity"
          onClick={onToggleMobile}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-surface-card text-text border-r border-border flex flex-col transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full'
        } shadow-fintech-lg lg:shadow-none`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-border/80 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8.5 h-8.5 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-xs select-none">
              <Store className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-1">
                <span className="font-extrabold text-base text-text tracking-tight">
                  Vyapar<span className="text-blue-600 dark:text-blue-400">Mitra</span>
                </span>
              </div>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="text-[10px] font-semibold text-text-muted">
                  Merchant OS
                </span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[9px] font-bold text-emerald-600 dark:text-emerald-400">Online</span>
              </div>
            </div>
          </div>
          <button
            onClick={onToggleMobile}
            className="lg:hidden text-text-muted hover:text-text p-1 rounded-lg"
            aria-label="Close navigation menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation & Store Info Body */}
        <div className="flex-1 px-3 py-2 overflow-y-auto flex flex-col justify-between">
          {/* Main Navigation Links */}
          <nav className="space-y-1">
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
                    type="button"
                    onClick={() => {
                      onTabChange(item.id);
                      if (isOpenMobile) onToggleMobile();
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all group relative ${
                      isActive
                        ? item.isCopilot
                          ? 'bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 font-bold shadow-2xs border border-purple-200/50 dark:border-purple-800/40'
                          : 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-bold shadow-2xs border border-blue-200/50 dark:border-blue-800/40'
                        : 'text-text-muted hover:bg-surface-muted hover:text-text'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <Icon
                        className={`w-4 h-4 shrink-0 transition-colors ${
                          isActive
                            ? item.isCopilot
                              ? 'text-purple-600 dark:text-purple-400'
                              : 'text-blue-600 dark:text-blue-400'
                            : 'text-text-subtle group-hover:text-text'
                        }`}
                      />
                      <span className="truncate">{item.label}</span>
                    </div>

                    {item.badge && (
                      <span className="px-1.5 py-0.2 text-[10px] font-bold rounded-full bg-blue-600 text-white shrink-0">
                        {item.badge}
                      </span>
                    )}
                  </button>
                </React.Fragment>
              );
            })}
          </nav>

          {/* Store Terminal & Device Status Card (Fills gap meaningfully) */}
          <div className="mt-4 mb-2 p-3 rounded-2xl bg-surface-muted/60 border border-border/80 text-text shadow-2xs">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-extrabold text-blue-600 dark:text-blue-400 uppercase tracking-wider flex items-center gap-1">
                <Zap className="w-3 h-3 text-blue-600 dark:text-blue-400" />
                POS Devices
              </span>
              <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Connected
              </span>
            </div>
            <div className="space-y-1.5 text-[11px] text-text-muted">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-text-muted">
                  <Printer className="w-3 h-3 text-text-subtle" />
                  Thermal Printer
                </span>
                <span className="text-[10px] font-semibold text-text">80mm Ready</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-text-muted">
                  <ShieldCheck className="w-3 h-3 text-text-subtle" />
                  Cloud Khata
                </span>
                <span className="text-[10px] font-semibold text-emerald-600 dark:text-emerald-400">Synced</span>
              </div>
            </div>
          </div>
        </div>

        {/* Consolidated Footer: User Profile + Smart Soundbox */}
        <div className="p-3 border-t border-border/80 bg-surface-muted/30 shrink-0 space-y-2">
          {/* User Profile Card */}
          {userProfile && (
            <div className="flex items-center justify-between gap-2 p-2 rounded-xl bg-surface-card border border-border shadow-2xs">
              <div className="flex items-center gap-2 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-blue-600/10 text-blue-600 dark:text-blue-400 border border-blue-500/20 flex items-center justify-center font-bold text-xs shrink-0 select-none">
                  {userProfile.avatarInitials || userProfile.name?.slice(0, 2).toUpperCase() || 'ME'}
                </div>
                <div className="min-w-0">
                  <span className="text-xs font-bold text-text truncate block leading-tight">
                    {userProfile.name}
                  </span>
                  <span className="text-[10px] text-text-muted truncate block">
                    ID: {userProfile.business_id || userProfile.id}
                  </span>
                </div>
              </div>
              {onLogout && (
                <button
                  type="button"
                  onClick={onLogout}
                  title="Log out"
                  className="p-1.5 rounded-lg text-text-muted hover:text-red-600 hover:bg-red-500/10 transition-colors shrink-0 cursor-pointer"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              )}
            </div>
          )}

          {/* Smart Soundbox Status Bar */}
          <div className="flex items-center justify-between px-2.5 py-1.5 rounded-xl bg-surface-card border border-border/70 text-text shadow-2xs">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-5 h-5 rounded-md bg-blue-600/10 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
                <Volume2 className="w-3 h-3" />
              </div>
              <span className="text-[11px] font-semibold text-text truncate">
                Smart Soundbox
              </span>
            </div>
            <div className="flex items-center gap-1.5 shrink-0">
              <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                4G Online
              </span>
              <Wifi className="w-3 h-3 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
