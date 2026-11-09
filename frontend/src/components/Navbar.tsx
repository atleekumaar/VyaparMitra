import React from 'react';
import { Bot, Store, Sun, Moon, LogOut } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import { UserProfile } from '../types';

interface NavbarProps {
  onOpenCopilot: () => void;
  isHealthy?: boolean;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
  userProfile?: UserProfile | null;
  onLogout?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenCopilot,
  isHealthy = true,
  isDarkMode,
  onToggleDarkMode,
  userProfile,
  onLogout,
}) => {
  const { language, setLanguage, t } = useLanguage();

  return (
    <header className="sticky top-0 z-30 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xs border-b border-slate-200/80 dark:border-slate-800 transition-colors duration-150">
      <div className="px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Merchant Store Identity */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-9 h-9 rounded-lg bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 border border-blue-200/60 dark:border-blue-800/60 flex items-center justify-center font-bold text-xs shrink-0 select-none">
            {userProfile?.avatarInitials || 'VM'}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-semibold text-slate-900 dark:text-white tracking-tight truncate leading-tight">
                {userProfile?.storeName || t('store_name', 'Vyapar Store')}
              </h1>
              {userProfile?.categoryLabel && (
                <span className="hidden sm:inline-flex px-1.5 py-0.2 rounded text-[10px] font-medium bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200/60 dark:border-blue-800/60 truncate">
                  {userProfile.categoryLabel}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mt-0.5 truncate leading-none">
              <Store className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span className="font-medium text-slate-600 dark:text-slate-300">
                ID: {userProfile?.id || 'M001'}
              </span>
              <span>&bull;</span>
              <span className="truncate">
                {userProfile?.city || t('store_category', 'FMCG & Retail • Lucknow')}
              </span>
            </p>
          </div>
        </div>

        {/* Right: Controls & Actions */}
        <div className="flex items-center gap-2 sm:gap-2.5 shrink-0">
          {/* Theme Toggle (Dark / Light Mode) */}
          <button
            onClick={onToggleDarkMode}
            className="w-8.5 h-8.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 text-slate-600 dark:text-amber-400 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center justify-center transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
            title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle Dark/Light Mode"
          >
            {isDarkMode ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-slate-600" />
            )}
          </button>

          {/* Language Selector */}
          <div className="flex items-center bg-slate-100 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80 rounded-lg p-0.5 text-xs font-medium">
            <button
              onClick={() => setLanguage('hinglish')}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                language === 'hinglish'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Hinglish
            </button>
            <button
              onClick={() => setLanguage('hindi')}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                language === 'hindi'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              हिंदी
            </button>
            <button
              onClick={() => setLanguage('english')}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                language === 'english'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              English
            </button>
          </div>

          {/* Quick Copilot CTA Button */}
          <button
            onClick={onOpenCopilot}
            className="inline-flex items-center gap-1.5 h-8.5 px-3 text-xs font-semibold rounded-lg bg-purple-600 hover:bg-purple-700 text-white shadow-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-600 active:scale-95 transition-all"
          >
            <Bot className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">{t('ask_copilot', 'Ask Copilot')}</span>
          </button>

          {/* Switch Account / Logout Button */}
          {onLogout && (
            <button
              onClick={onLogout}
              className="h-8.5 px-2.5 rounded-lg bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700/80 text-xs font-medium inline-flex items-center gap-1.5 transition-colors"
              title={t('switch_account', 'Switch Account / Logout')}
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden md:inline">{t('switch_account', 'Switch Account')}</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
