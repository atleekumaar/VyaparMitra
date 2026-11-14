import React, { useEffect, useRef } from 'react';
import { Bot, Store, Sun, Moon, LogOut, Search, Bell, Sparkles } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import { UserProfile } from '../types';

interface NavbarProps {
  onOpenCopilot: () => void;
  isHealthy?: boolean;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
  userProfile?: UserProfile | null;
  onLogout?: () => void;
  onOpenSearch?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenCopilot,
  isHealthy = true,
  isDarkMode,
  onToggleDarkMode,
  userProfile,
  onLogout,
  onOpenSearch,
}) => {
  const { language, setLanguage, t } = useLanguage();
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Global keyboard shortcut: '/' or 'Ctrl/Cmd+K' focuses search or triggers Copilot
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.key === '/' || (e.key === 'k' && (e.metaKey || e.ctrlKey))) && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
        e.preventDefault();
        if (onOpenSearch) {
          onOpenSearch();
        } else if (searchInputRef.current) {
          searchInputRef.current.focus();
        } else {
          onOpenCopilot();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onOpenSearch, onOpenCopilot]);

  const activeMerchantId = userProfile?.business_id || userProfile?.merchant_id || userProfile?.id || '—';

  return (
    <header className="sticky top-0 z-30 bg-surface-card/95 backdrop-blur-md border-b border-border transition-colors duration-150">
      <div className="px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Merchant Store Identity */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-9 h-9 rounded-xl bg-brand-soft text-brand border border-brand/20 flex items-center justify-center font-black text-xs shrink-0 select-none">
            {userProfile?.avatarInitials || 'VM'}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-text tracking-tight truncate leading-tight">
                {userProfile?.storeName || (userProfile?.name ? `${userProfile.name}'s Store` : t('store_name', 'Vyapar Store'))}
              </h1>
              {userProfile?.categoryLabel && (
                <span className="hidden sm:inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold bg-brand-soft text-brand border border-brand/20 truncate">
                  {userProfile.categoryLabel}
                </span>
              )}
            </div>
            <p className="text-xs text-text-muted flex items-center gap-1.5 mt-0.5 truncate leading-none">
              <Store className="w-3.5 h-3.5 text-text-subtle shrink-0" />
              <span className="font-semibold text-text-muted">
                ID: {activeMerchantId}
              </span>
              <span>&bull;</span>
              <span className="truncate">
                {userProfile?.city || 'India'}
              </span>
            </p>
          </div>
        </div>

        {/* Center: Quick Command / Search Bar */}
        <div className="hidden md:flex items-center flex-1 max-w-md mx-4">
          <div
            onClick={() => {
              if (onOpenSearch) onOpenSearch();
              else searchInputRef.current?.focus();
            }}
            className="w-full flex items-center gap-2 px-3 py-1.5 rounded-xl bg-surface-muted border border-border text-xs text-text-muted hover:border-border-strong cursor-pointer transition-colors"
          >
            <Search className="w-3.5 h-3.5 text-text-subtle shrink-0" />
            <input
              ref={searchInputRef}
              type="text"
              placeholder={t('search_command_placeholder', 'Search products, sales, customers, actions...')}
              className="bg-transparent text-xs text-text placeholder-text-subtle focus:outline-none w-full font-medium"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  onOpenCopilot();
                }
              }}
            />
            <kbd className="hidden lg:inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] font-mono bg-surface-card text-text-muted border border-border rounded-md shadow-2xs">
              /
            </kbd>
          </div>
        </div>

        {/* Right: Controls & Actions */}
        <div className="flex items-center gap-2 sm:gap-2.5 shrink-0">
          {/* Notifications Indicator */}
          <button
            type="button"
            className="w-8.5 h-8.5 rounded-xl bg-surface-card border border-border text-text-muted hover:text-text hover:bg-surface-muted flex items-center justify-center transition-colors relative"
            title="Notifications"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-brand" />
          </button>

          {/* Theme Toggle (Dark / Light Mode) */}
          <button
            type="button"
            onClick={onToggleDarkMode}
            className="w-8.5 h-8.5 rounded-xl bg-surface-card border border-border text-text-muted hover:text-text hover:bg-surface-muted flex items-center justify-center transition-colors"
            title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle Dark/Light Mode"
          >
            {isDarkMode ? (
              <Sun className="w-4 h-4 text-warning" />
            ) : (
              <Moon className="w-4 h-4 text-text-muted" />
            )}
          </button>

          {/* Language Selector */}
          <div className="flex items-center bg-surface-muted border border-border rounded-xl p-0.5 text-xs font-semibold">
            {(['hinglish', 'hindi', 'english'] as const).map((lang) => (
              <button
                key={lang}
                type="button"
                onClick={() => setLanguage(lang)}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  language === lang
                    ? 'bg-surface-card text-text shadow-2xs font-bold'
                    : 'text-text-muted hover:text-text'
                }`}
              >
                {lang === 'hinglish' ? 'Hinglish' : lang === 'hindi' ? 'हिंदी' : 'English'}
              </button>
            ))}
          </div>

          {/* Quick Copilot CTA Button */}
          <button
            type="button"
            onClick={onOpenCopilot}
            className="inline-flex items-center gap-1.5 h-8.5 px-3 text-xs font-bold rounded-xl bg-purple-600 hover:bg-purple-700 text-white shadow-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-600 active:scale-95 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">{t('ask_copilot', 'AI Copilot')}</span>
          </button>

          {/* Switch Account / Logout Button */}
          {onLogout && (
            <button
              type="button"
              onClick={onLogout}
              className="h-8.5 px-2.5 rounded-xl bg-surface-card hover:bg-surface-muted text-text-muted hover:text-danger border border-border text-xs font-semibold inline-flex items-center gap-1.5 transition-colors"
              title={t('switch_account', 'Switch Account / Logout')}
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden md:inline">{t('switch_account', 'Exit')}</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
