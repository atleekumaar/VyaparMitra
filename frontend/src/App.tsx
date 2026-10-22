import React, { useState, useEffect } from 'react';
import { Sidebar, NavTab } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { ComparePage } from './pages/ComparePage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ProductsPage } from './pages/ProductsPage';
import { CustomersPage } from './pages/CustomersPage';
import { ForecastsPage } from './pages/ForecastsPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { CopilotPage } from './pages/CopilotPage';
import { SettingsPage } from './pages/SettingsPage';
import { api } from './api/client';
import { Menu } from 'lucide-react';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');
  const [isOpenMobile, setIsOpenMobile] = useState<boolean>(false);
  const [isHealthy, setIsHealthy] = useState<boolean>(true);
  const [pendingActionsCount, setPendingActionsCount] = useState<number>(0);
  const [selectedActionId, setSelectedActionId] = useState<string | null>(null);
  const [copilotQuery, setCopilotQuery] = useState<string | null>(null);

  // Theme Dark / Light Mode State
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    const saved = localStorage.getItem('vyaparmitra_theme');
    if (saved) return saved === 'dark';
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Apply dark mode class to root HTML
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('vyaparmitra_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('vyaparmitra_theme', 'light');
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode((prev) => !prev);
  };

  // Poll health and pending actions
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const liveRes = await api.getHealth();
        setIsHealthy(liveRes.status === 'healthy' || liveRes.status === 'ok');
      } catch {
        setIsHealthy(false);
      }

      try {
        const recsRes = await api.getRecommendations();
        const pending = (recsRes.recommendations || []).filter(
          (r: any) => r.status === 'GENERATED' || r.status === 'VIEWED'
        ).length;
        setPendingActionsCount(pending);
      } catch {
        // Silently catch in case of startup delay
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectAction = (actionId: string) => {
    setSelectedActionId(actionId);
    setCurrentTab('recommendations');
  };

  const handleQuickCopilot = (query: string) => {
    setCopilotQuery(query);
    setCurrentTab('copilot');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0B0F19] text-slate-900 dark:text-slate-100 flex transition-colors duration-200">
      {/* Sidebar navigation */}
      <Sidebar
        currentTab={currentTab}
        onTabChange={(tab) => {
          setCurrentTab(tab);
          if (tab !== 'recommendations') {
            setSelectedActionId(null);
          }
          if (tab !== 'copilot') {
            setCopilotQuery(null);
          }
        }}
        pendingActionsCount={pendingActionsCount}
        isOpenMobile={isOpenMobile}
        onToggleMobile={() => setIsOpenMobile((prev) => !prev)}
      />

      {/* Main content wrapper */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile topbar */}
        <div className="lg:hidden flex items-center justify-between px-4 py-2.5 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 transition-colors">
          <button
            onClick={() => setIsOpenMobile(true)}
            className="p-1.5 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5 text-slate-700 dark:text-slate-200" />
          </button>
          <div className="flex items-center gap-2">
            <span className="font-bold text-base text-slate-900 dark:text-white">
              Vyapar<span className="text-blue-600 dark:text-blue-400">Mitra</span>
            </span>
          </div>
          <div className="w-6" /> {/* Spacer */}
        </div>

        {/* Global top navigation bar */}
        <Navbar
          onOpenCopilot={() => {
            setCopilotQuery(null);
            setCurrentTab('copilot');
          }}
          isHealthy={isHealthy}
          isDarkMode={isDarkMode}
          onToggleDarkMode={toggleDarkMode}
        />

        {/* Main Content Area */}
        <main className="flex-1 px-4 sm:px-6 lg:px-8 py-6 lg:py-8 max-w-7xl w-full mx-auto">
          {currentTab === 'dashboard' && (
            <DashboardPage
              onNavigateTab={(tab) => setCurrentTab(tab as NavTab)}
              onSelectAction={handleSelectAction}
              onQuickCopilot={handleQuickCopilot}
            />
          )}

          {currentTab === 'compare' && (
            <ComparePage
              onNavigateTab={(tab) => setCurrentTab(tab as NavTab)}
              onQuickCopilot={handleQuickCopilot}
            />
          )}

          {currentTab === 'analytics' && <AnalyticsPage />}

          {currentTab === 'products' && <ProductsPage />}

          {currentTab === 'customers' && <CustomersPage />}

          {currentTab === 'forecasts' && <ForecastsPage />}

          {currentTab === 'recommendations' && (
            <RecommendationsPage
              initialActionId={selectedActionId}
            />
          )}

          {currentTab === 'copilot' && (
            <CopilotPage
              initialQuery={copilotQuery}
            />
          )}

          {currentTab === 'settings' && (
            <SettingsPage
              isDarkMode={isDarkMode}
              onToggleDarkMode={toggleDarkMode}
            />
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
