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
  const [currentLanguage, setCurrentLanguage] = useState<string>('hinglish');
  const [isOpenMobile, setIsOpenMobile] = useState<boolean>(false);
  const [isHealthy, setIsHealthy] = useState<boolean>(true);
  const [pendingActionsCount, setPendingActionsCount] = useState<number>(0);
  const [selectedActionId, setSelectedActionId] = useState<string | null>(null);
  const [copilotQuery, setCopilotQuery] = useState<string | null>(null);

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
    <div className="min-h-screen bg-slate-50 flex">
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
        <div className="lg:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-paytm-border">
          <button
            onClick={() => setIsOpenMobile(true)}
            className="p-1.5 rounded-md text-paytm-text hover:bg-slate-100"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5 text-paytm-dark" />
          </button>
          <div className="flex items-center gap-2">
            <span className="font-bold text-base text-paytm-dark">
              Vyapar<span className="text-paytm-blue">Mitra</span>
            </span>
          </div>
          <div className="w-6" /> {/* Spacer */}
        </div>

        {/* Global top navigation bar */}
        <Navbar
          currentLanguage={currentLanguage}
          onLanguageChange={setCurrentLanguage}
          onOpenCopilot={() => {
            setCurrentTab('copilot');
            setCopilotQuery(null);
          }}
          isHealthy={isHealthy}
        />

        {/* Tab view area */}
        <main className="flex-1 p-4 lg:p-8 max-w-7xl w-full mx-auto">
          {currentTab === 'dashboard' && (
            <DashboardPage
              onNavigateTab={(tab) => setCurrentTab(tab as NavTab)}
              onSelectAction={handleSelectAction}
              onQuickCopilot={handleQuickCopilot}
            />
          )}

          {currentTab === 'compare' && (
            <ComparePage
              currentLanguage={currentLanguage}
              onNavigateTab={(tab) => setCurrentTab(tab as NavTab)}
              onQuickCopilot={handleQuickCopilot}
            />
          )}

          {currentTab === 'analytics' && <AnalyticsPage />}

          {currentTab === 'products' && <ProductsPage />}

          {currentTab === 'customers' && <CustomersPage />}

          {currentTab === 'forecasts' && <ForecastsPage />}

          {currentTab === 'recommendations' && (
            <RecommendationsPage initialActionId={selectedActionId} />
          )}

          {currentTab === 'copilot' && (
            <CopilotPage
              initialQuery={copilotQuery}
              currentLanguage={currentLanguage}
              onLanguageChange={setCurrentLanguage}
            />
          )}

          {currentTab === 'settings' && (
            <SettingsPage
              currentLanguage={currentLanguage}
              onLanguageChange={setCurrentLanguage}
            />
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
