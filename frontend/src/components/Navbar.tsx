import React from 'react';
import { Bot, HelpCircle, Store, Bell, CheckCircle2, Volume2, ShieldCheck, Sun, Moon } from 'lucide-react';
import { Badge } from './Badge';
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
    <header className="sticky top-0 z-30 bg-white dark:bg-[#0B1528] border-b border-[#CDE5F7] dark:border-[#1E3A6E] shadow-xs transition-colors duration-200">
      {/* Paytm Signature Brand Accent Strip */}
      <div className="h-1.5 w-full bg-gradient-to-r from-[#002970] via-[#00BAF2] to-[#00B970]" />

      <div className="px-4 lg:px-8 py-3 flex items-center justify-between">
        {/* Left: Merchant Store Profile */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-[#002970] to-[#001A4E] text-white flex items-center justify-center font-black text-lg shadow-sm border border-[#00BAF2]/30 ring-2 ring-[#00BAF2]/10">
            VK
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-extrabold text-[#002970] dark:text-white tracking-tight">
                {t('store_name', 'Vyapar Kirana Store')}
              </h1>
              <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#E8F8F0] dark:bg-[#00B970]/20 text-[#008A54] dark:text-[#00E68A] border border-[#B6E8D0] dark:border-[#00B970]/30">
                <ShieldCheck className="w-3 h-3 text-[#00B970]" />
                {t('verified_merchant', 'Paytm Verified')}
              </span>
            </div>
            <p className="text-xs text-[#4F6A94] dark:text-blue-200 flex items-center gap-1.5 mt-0.5">
              <Store className="w-3.5 h-3.5 text-[#00BAF2]" />
              <span className="font-semibold text-[#002970] dark:text-blue-100">ID: M001</span> &bull; {t('store_category', 'FMCG, Retail & Kirana • Lucknow')}
            </p>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Soundbox Live Pill */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#F0F8FE] dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E] text-xs">
            <Volume2 className="w-4 h-4 text-[#00BAF2] animate-bounce" />
            <div className="text-[11px]">
              <span className="font-bold text-[#002970] dark:text-white">{t('soundbox_ready', 'Soundbox Ready:')}</span>{' '}
              <span className="text-[#008A54] dark:text-[#00E68A] font-semibold">{t('soundbox_instant', '100% Instant Audio Alert')}</span>
            </div>
          </div>

          {/* Theme Toggle (Dark / Light Mode) */}
          <button
            onClick={onToggleDarkMode}
            className="p-2 rounded-xl bg-[#F0F8FE] dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E] hover:border-[#00BAF2] text-[#002970] dark:text-[#FFB800] transition-all duration-200 shadow-2xs group relative"
            title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle Dark/Light Mode"
          >
            {isDarkMode ? (
              <Sun className="w-4 h-4 text-[#FFB800] animate-spin-slow transition-transform" />
            ) : (
              <Moon className="w-4 h-4 text-[#002970] transition-transform" />
            )}
          </button>

          {/* Language Selector */}
          <div className="flex items-center bg-[#F0F8FE] dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E] rounded-xl p-1 text-xs font-semibold shadow-xs">
            <button
              onClick={() => setLanguage('hinglish')}
              className={`px-2.5 sm:px-3 py-1 rounded-lg transition-all ${
                language === 'hinglish'
                  ? 'bg-[#00BAF2] text-white shadow-xs font-bold'
                  : 'text-[#002970] dark:text-blue-200 hover:text-[#00BAF2]'
              }`}
            >
              Hinglish
            </button>
            <button
              onClick={() => setLanguage('hindi')}
              className={`px-2.5 sm:px-3 py-1 rounded-lg transition-all ${
                language === 'hindi'
                  ? 'bg-[#00BAF2] text-white shadow-xs font-bold'
                  : 'text-[#002970] dark:text-blue-200 hover:text-[#00BAF2]'
              }`}
            >
              हिंदी
            </button>
            <button
              onClick={() => setLanguage('english')}
              className={`px-2.5 sm:px-3 py-1 rounded-lg transition-all ${
                language === 'english'
                  ? 'bg-[#00BAF2] text-white shadow-xs font-bold'
                  : 'text-[#002970] dark:text-blue-200 hover:text-[#00BAF2]'
              }`}
            >
              English
            </button>
          </div>

          {/* Quick Copilot CTA */}
          <button
            onClick={onOpenCopilot}
            className="inline-flex items-center gap-1.5 px-3 sm:px-3.5 py-2 text-xs font-bold rounded-xl bg-gradient-to-r from-[#002970] to-[#001F58] hover:from-[#00388F] hover:to-[#002970] text-white shadow-md shadow-[#002970]/20 border border-[#00BAF2]/40 transition-all active:scale-95"
          >
            <Bot className="w-4 h-4 text-[#00BAF2]" />
            <span className="hidden sm:inline">{t('ask_copilot', 'Ask Copilot')}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
