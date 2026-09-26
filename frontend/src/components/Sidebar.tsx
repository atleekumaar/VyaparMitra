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
  Menu,
  X,
  Trophy,
} from 'lucide-react';

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
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'compare', label: 'Peers / Compare', icon: Trophy },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'products', label: 'Products', icon: Package },
    { id: 'customers', label: 'Customers', icon: Users },
    { id: 'forecasts', label: 'Forecasts', icon: TrendingUp },
    {
      id: 'recommendations',
      label: 'Action Center',
      icon: Sparkles,
      badge: pendingActionsCount > 0 ? String(pendingActionsCount) : undefined,
    },
    { id: 'copilot', label: 'AI Copilot', icon: Bot, isHighlight: true },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 lg:hidden"
          onClick={onToggleMobile}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-white border-r border-paytm-border flex flex-col transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-paytm-border">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-paytm-blue flex items-center justify-center text-white font-extrabold text-sm shadow-xs">
              VM
            </div>
            <div>
              <span className="font-bold text-lg text-paytm-dark tracking-tight leading-none block">
                Vyapar<span className="text-paytm-blue">Mitra</span>
              </span>
              <span className="text-[10px] font-medium tracking-wide text-paytm-muted block mt-0.5 uppercase">
                Command Center
              </span>
            </div>
          </div>
          <button
            onClick={onToggleMobile}
            className="lg:hidden text-paytm-muted hover:text-paytm-text"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
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
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-paytm-light text-paytm-blue font-semibold shadow-xs'
                    : 'text-paytm-text hover:bg-slate-50 hover:text-paytm-dark'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? 'text-paytm-blue' : 'text-slate-400 group-hover:text-paytm-text'
                    }`}
                  />
                  <span>{item.label}</span>
                </div>

                {item.badge && (
                  <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-red-100 text-red-700">
                    {item.badge}
                  </span>
                )}
                {item.isHighlight && !item.badge && (
                  <span className="px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded bg-paytm-blue/10 text-paytm-blue">
                    AI
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer info */}
        <div className="p-4 border-t border-paytm-border bg-paytm-light/50">
          <div className="rounded-lg p-3 bg-white border border-paytm-border text-xs text-paytm-muted space-y-1">
            <p className="font-semibold text-paytm-dark">VyaparMitra AI v1.0</p>
            <p className="text-[11px]">Paytm-Inspired Fintech UI System</p>
            <div className="pt-1 flex items-center justify-between text-[11px] text-emerald-600 font-medium">
              <span>● Offline Verified</span>
              <span>128/128 Tests</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
