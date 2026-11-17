import React, { useState, useEffect } from 'react';
import { Sidebar, NavTab } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { LoginPage } from './pages/LoginPage';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { ComparePage } from './pages/ComparePage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ProductsPage } from './pages/ProductsPage';
import { CustomersPage } from './pages/CustomersPage';
import { SuppliersPage } from './pages/SuppliersPage';
import { FinancePage } from './pages/FinancePage';
import { ForecastsPage } from './pages/ForecastsPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { CopilotPage } from './pages/CopilotPage';
import { SettingsPage } from './pages/SettingsPage';
import { api, clearAuthSession } from './api/client';
import { Menu } from 'lucide-react';
import { UserProfile } from './types';
import { ToastProvider } from './components/Toast';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');
  const [isOpenMobile, setIsOpenMobile] = useState<boolean>(false);
  const [isHealthy, setIsHealthy] = useState<boolean>(true);
  const [pendingActionsCount, setPendingActionsCount] = useState<number>(0);
  const [selectedActionId, setSelectedActionId] = useState<string | null>(null);
  const [copilotQuery, setCopilotQuery] = useState<string | null>(null);

  // Authenticated User Profile State
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('vyaparmitra_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return null;
      }
    }
    return null;
  });

  // Public Landing / Login Navigation
  const [publicView, setPublicView] = useState<'landing' | 'login'>('landing');
  const [initialAuthMode, setInitialAuthMode] = useState<'login' | 'signup' | 'otp_login'>('login');

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

  const handleLogin = (profile: UserProfile) => {
    setCurrentUser(profile);
    localStorage.setItem('vyaparmitra_user', JSON.stringify(profile));
  };

  const handleLogout = () => {
    setCurrentUser(null);
    clearAuthSession();
    setPublicView('login');
  };

  // Listen for unauthorized 401 events to cleanly wipe session and redirect to login
  useEffect(() => {
    const onUnauthorized = () => {
      setCurrentUser(null);
      clearAuthSession();
      setPublicView('login');
    };
    window.addEventListener('vyaparmitra:unauthorized', onUnauthorized);
    return () => window.removeEventListener('vyaparmitra:unauthorized', onUnauthorized);
  }, []);

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

  // Synchronize dynamic document.title with active tab
  useEffect(() => {
    const titles: Record<NavTab, string> = {
      dashboard: 'Dashboard | VyaparMitra',
      compare: 'Peer Benchmarks | VyaparMitra',
      analytics: 'Analytics & Insights | VyaparMitra',
      products: 'Products & Inventory | VyaparMitra',
      customers: 'Customers & Khata | VyaparMitra',
      suppliers: 'Suppliers & PO | VyaparMitra',
      finance: 'Finance & P&L | VyaparMitra',
      forecasts: 'Sales & Demand Forecasts | VyaparMitra',
      recommendations: 'Action Center | VyaparMitra',
      copilot: 'AI Business Copilot | VyaparMitra',
      settings: 'Merchant Settings | VyaparMitra',
    };
    document.title = titles[currentTab] || 'VyaparMitra';
  }, [currentTab]);

  // Global Keyboard Shortcuts: / to search, Cmd/Ctrl+K for copilot
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const activeEl = document.activeElement;
      const isInput =
        activeEl instanceof HTMLInputElement ||
        activeEl instanceof HTMLTextAreaElement ||
        (activeEl as HTMLElement)?.isContentEditable;

      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setCurrentTab((prev) => (prev === 'copilot' ? 'dashboard' : 'copilot'));
      } else if (e.key === '/' && !isInput) {
        e.preventDefault();
        const searchInput = document.querySelector<HTMLInputElement>(
          'input[type="text"][placeholder*="Search"], input[type="text"][placeholder*="Khojein"]'
        );
        if (searchInput) {
          searchInput.focus();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSelectAction = (actionId: string) => {
    setSelectedActionId(actionId);
    setCurrentTab('recommendations');
  };

  const handleQuickCopilot = (query: string) => {
    setCopilotQuery(query);
    setCurrentTab('copilot');
  };

  // Render Landing Page or Login Page if not logged in
  if (!currentUser) {
    if (publicView === 'landing') {
      return (
        <LandingPage
          onGetStarted={() => {
            setInitialAuthMode('signup');
            setPublicView('login');
          }}
          onLogin={() => {
            setInitialAuthMode('login');
            setPublicView('login');
          }}
          isDarkMode={isDarkMode}
          onToggleDarkMode={toggleDarkMode}
        />
      );
    }

    return (
      <LoginPage
        onLogin={handleLogin}
        isDarkMode={isDarkMode}
        onToggleDarkMode={toggleDarkMode}
        onGoToLanding={() => setPublicView('landing')}
        initialAuthMode={initialAuthMode}
      />
    );
  }

  return (
    <ToastProvider>
      <div className="min-h-screen bg-surface-muted dark:bg-surface bg-ambient-mesh text-text flex transition-colors duration-200">
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
          userProfile={currentUser}
          onLogout={handleLogout}
        />

        {/* Main content wrapper */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Mobile topbar */}
          <div className="lg:hidden flex items-center justify-between px-4 py-2.5 bg-surface border-b border-border transition-colors">
            <button
              onClick={() => setIsOpenMobile(true)}
              className="p-1.5 rounded-lg text-text-muted hover:bg-surface-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand"
              aria-label="Open navigation menu"
            >
              <Menu className="w-5 h-5 text-text" />
            </button>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base text-text">
                Vyapar<span className="text-brand">Mitra</span>
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
            userProfile={currentUser}
            onLogout={handleLogout}
          />

          {/* Main Content Area */}
          <main className="flex-1 px-4 sm:px-6 lg:px-8 py-6 lg:py-8 max-w-7xl w-full mx-auto">
            {currentTab === 'dashboard' && (
              <DashboardPage
                onNavigateTab={(tab) => setCurrentTab(tab as NavTab)}
                onSelectAction={handleSelectAction}
                onQuickCopilot={handleQuickCopilot}
                currentUser={currentUser}
              />
            )}

            {currentTab === 'compare' && (
              <ComparePage
                onNavigateTab={(tab) => setCurrentTab(tab as NavTab)}
                onQuickCopilot={handleQuickCopilot}
                currentUser={currentUser}
              />
            )}

            {currentTab === 'analytics' && <AnalyticsPage currentUser={currentUser} />}

            {currentTab === 'products' && <ProductsPage />}

            {currentTab === 'customers' && <CustomersPage />}

            {currentTab === 'suppliers' && <SuppliersPage />}

            {currentTab === 'finance' && <FinancePage />}

            {currentTab === 'forecasts' && (
              <ForecastsPage
                onNavigateTab={(tab) => setCurrentTab(tab as NavTab)}
              />
            )}

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
                currentUser={currentUser}
              />
            )}
          </main>
        </div>
      </div>
    </ToastProvider>
  );
};

export default App;
