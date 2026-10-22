import React from 'react';
import { Bot, Store, ShieldCheck, Sun, Moon, Volume2 } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';

interface NavbarProps {
  onOpenCopilot: () => void;
  isHealthy?: boolean;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenCopilot,
  isHealthy = true,
  isDarkMode,
  onToggleDarkMode,
}) => {
  const { language, setLanguage, t } = useLanguage();

  return (
    <header className="sticky top-0 z-30 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-xs transition-colors duration-200">
      <div className="px-4 lg:px-8 py-2.5 flex items-center justify-between gap-4">
        {/* Left: Merchant Store Profile */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-800 text-blue-600 dark:text-blue-400 border border-slate-200 dark:border-slate-700 flex items-center justify-center font-bold text-sm shrink-0">
            VK
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white tracking-tight truncate">
                {t('store_name', 'Vyapar Store')}
              </h1>
              <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/60">
                <ShieldCheck className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                {t('verified_merchant', 'Verified Store')}
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mt-0.5 truncate">
              <Store className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span className="font-medium text-slate-700 dark:text-slate-300">ID: M001</span>
              <span>&bull;</span>
              <span className="truncate">{t('store_category', 'FMCG & Retail • Lucknow')}</span>
            </p>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2 sm:gap-2.5 shrink-0">
          {/* Soundbox Live Pill */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs">
            <Volume2 className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
            <div className="text-[11px] flex items-center gap-1.5">
              <span className="font-semibold text-slate-700 dark:text-slate-300">
                {t('soundbox_ready', 'Soundbox Ready:')}
              </span>
              <span className="text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Live
              </span>
            </div>
          </div>

          {/* Theme Toggle (Dark / Light Mode) */}
          <button
            onClick={onToggleDarkMode}
            className="p-1.5 sm:p-2 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-amber-400 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors shadow-2xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
            title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle Dark/Light Mode"
          >
            {isDarkMode ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-slate-700" />
            )}
          </button>

          {/* Language Selector */}
          <div className="flex items-center bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-0.5 text-xs font-medium">
            <button
              onClick={() => setLanguage('hinglish')}
              className={`px-2 py-1 rounded-md transition-colors ${
                language === 'hinglish'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Hinglish
            </button>
            <button
              onClick={() => setLanguage('hindi')}
              className={`px-2 py-1 rounded-md transition-colors ${
                language === 'hindi'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              हिंदी
            </button>
            <button
              onClick={() => setLanguage('english')}
              className={`px-2 py-1 rounded-md transition-colors ${
                language === 'english'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              English
            </button>
          </div>

          {/* Quick Copilot CTA (Purple AI accent) */}
          <button
            onClick={onOpenCopilot}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-purple-600 hover:bg-purple-700 text-white shadow-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-600 active:scale-95 transition-all"
          >
            <Bot className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">{t('ask_copilot', 'Ask Copilot')}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
