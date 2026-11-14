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
} from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import { UserProfile } from '../types';

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
  const { t } = useLanguage();

  const navItems: NavItemConfig[] = [
    // Overview
    { id: 'dashboard', label: t('nav_dashboard', 'Dashboard'), icon: LayoutDashboard, section: 'overview' },
    { id: 'analytics', label: t('nav_analytics', 'Analytics'), icon: BarChart3, section: 'overview' },
    { id: 'compare', label: t('nav_compare', 'Peer Benchmark'), icon: Trophy, section: 'overview' },

    // Operations
    { id: 'products', label: t('nav_products', 'Products & Stock'), icon: Package, section: 'operations' },
    { id: 'customers', label: t('nav_customers', 'Customers & Khata'), icon: Users, section: 'operations' },
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
    <div className="px-3 pt-4 pb-1.5 text-[11px] font-bold uppercase tracking-wider text-text-subtle">
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
        <div className="h-16 flex items-center justify-between px-5 border-b border-border/80">
          <div className="flex items-center gap-2.5">
            <div className="w-8.5 h-8.5 rounded-xl bg-brand text-white flex items-center justify-center font-black text-sm shadow-xs select-none">
              VM
            </div>
            <div>
              <div className="flex items-center gap-1">
                <span className="font-extrabold text-base text-text tracking-tight">
                  Vyapar<span className="text-brand">Mitra</span>
                </span>
                {userProfile?.is_demo && (
                  <span className="px-1.5 py-0.2 rounded-full text-[9px] font-bold bg-amber-500/10 text-amber-500 border border-amber-500/30">
                    Demo
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="text-[10px] font-medium text-text-muted">
                  Fintech Merchant OS
                </span>
                <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
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

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-3 space-y-1 overflow-y-auto">
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
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all group relative ${
                    isActive
                      ? item.isCopilot
                        ? 'bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 font-bold'
                        : 'bg-brand-soft text-brand font-bold shadow-2xs'
                      : 'text-text-muted hover:bg-surface-muted hover:text-text'
                  }`}
                >
                  {/* Left Active Indicator Bar */}
                  {isActive && (
                    <span
                      className={`absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full ${
                        item.isCopilot ? 'bg-purple-600' : 'bg-brand'
                      }`}
                    />
                  )}

                  <div className="flex items-center gap-2.5 min-w-0">
                    <Icon
                      className={`w-4 h-4 shrink-0 transition-colors ${
                        isActive
                          ? item.isCopilot
                            ? 'text-purple-600 dark:text-purple-400'
                            : 'text-brand'
                          : 'text-text-subtle group-hover:text-text'
                      }`}
                    />
                    <span className="truncate">{item.label}</span>
                  </div>

                  {item.badge && (
                    <span className="px-1.5 py-0.2 text-[10px] font-bold rounded-full bg-brand text-white shrink-0">
                      {item.badge}
                    </span>
                  )}
                </button>
              </React.Fragment>
            );
          })}
        </nav>

        {/* Profile / Store Switcher Chip */}
        {userProfile && (
          <div className="p-3 border-t border-border/80 bg-surface-muted/40">
            <div className="flex items-center justify-between gap-2 p-2 rounded-xl bg-surface-card border border-border shadow-2xs">
              <div className="flex items-center gap-2 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-brand-soft text-brand border border-brand/20 flex items-center justify-center font-bold text-xs shrink-0 select-none">
                  {userProfile.avatarInitials || 'ME'}
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
                  className="p-1.5 rounded-lg text-text-muted hover:text-danger hover:bg-danger-soft transition-colors shrink-0"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        )}

        {/* Smart Soundbox Status Bar */}
        <div className="p-3 border-t border-border/60 bg-surface-muted/20">
          <div className="rounded-xl p-2 bg-surface-card border border-border/70 text-text shadow-2xs">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 min-w-0">
                <div className="w-6 h-6 rounded-md bg-brand-soft border border-brand/20 flex items-center justify-center text-brand shrink-0">
                  <Volume2 className="w-3.5 h-3.5" />
                </div>
                <div className="min-w-0">
                  <span className="text-xs font-semibold text-text block leading-tight truncate">
                    Smart Soundbox
                  </span>
                  <span className="text-[10px] text-success font-medium flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
                    Online &bull; 4G POS
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-1 text-[10px] text-text-subtle shrink-0">
                <Wifi className="w-3 h-3 text-brand" />
                <span>Sync</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
