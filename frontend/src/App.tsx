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
    <div className="min-h-screen bg-[#F0F6FB] dark:bg-[#070E1A] text-[#0F2042] dark:text-slate-100 flex transition-colors duration-200">
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
        {/* Mobile menu bar */}
        <div className="lg:hidden flex items-center justify-between px-4 py-3 bg-white dark:bg-[#0B1528] border-b border-[#CDE5F7] dark:border-[#1E3A6E] transition-colors">
          <button
            onClick={() => setIsOpenMobile(true)}
            className="p-1.5 rounded-lg text-[#002970] dark:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5 text-[#002970] dark:text-[#00BAF2]" />
          </button>
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-base text-[#002970] dark:text-white">
              Vyapar<span className="text-[#00BAF2]">Mitra</span>
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
        <main className="flex-1 px-4 lg:px-8 py-4 lg:py-6 w-full">
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
