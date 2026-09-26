import React from 'react';
import { Bot, HelpCircle, Store, Bell, CheckCircle2, Volume2, ShieldCheck } from 'lucide-react';
import { Badge } from './Badge';

interface NavbarProps {
  currentLanguage: string;
  onLanguageChange: (lang: string) => void;
  onOpenCopilot: () => void;
  isHealthy?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentLanguage,
  onLanguageChange,
  onOpenCopilot,
  isHealthy = true,
}) => {
  return (
    <header className="sticky top-0 z-30 bg-white border-b border-[#CDE5F7] shadow-xs">
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
              <h1 className="text-base font-extrabold text-[#002970] tracking-tight">
                Vyapar Kirana Store
              </h1>
              <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#E8F8F0] text-[#008A54] border border-[#B6E8D0]">
                <ShieldCheck className="w-3 h-3 text-[#00B970]" />
                Paytm Verified
              </span>
            </div>
            <p className="text-xs text-[#4F6A94] flex items-center gap-1.5 mt-0.5">
              <Store className="w-3.5 h-3.5 text-[#00BAF2]" />
              <span className="font-semibold text-[#002970]">ID: M001</span> &bull; FMCG, Retail & Kirana &bull; Lucknow
            </p>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          {/* Soundbox Live Pill */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#F0F8FE] border border-[#CDE5F7] text-xs">
            <Volume2 className="w-4 h-4 text-[#00BAF2] animate-bounce" />
            <div className="text-[11px]">
              <span className="font-bold text-[#002970]">Soundbox Ready:</span>{' '}
              <span className="text-[#008A54] font-semibold">100% Instant Audio Alert</span>
            </div>
          </div>

          {/* System Health Dot */}
          <div
            className="hidden md:flex items-center gap-1.5 text-xs text-[#4F6A94] px-2.5 py-1.5 rounded-xl bg-[#F0F8FE] border border-[#CDE5F7]"
            title="Intelligence Engine Status"
          >
            <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-[#00B970] animate-pulse' : 'bg-red-500'}`} />
            <span className="font-bold text-[#002970]">{isHealthy ? 'AI Active' : 'Offline'}</span>
          </div>

          {/* Language Selector */}
          <div className="flex items-center bg-[#F0F8FE] border border-[#CDE5F7] rounded-xl p-1 text-xs font-semibold shadow-xs">
            <button
              onClick={() => onLanguageChange('hinglish')}
              className={`px-3 py-1 rounded-lg transition-all ${
                currentLanguage === 'hinglish'
                  ? 'bg-[#00BAF2] text-white shadow-xs font-bold'
                  : 'text-[#002970] hover:text-[#00BAF2]'
              }`}
            >
              Hinglish
            </button>
            <button
              onClick={() => onLanguageChange('hindi')}
              className={`px-3 py-1 rounded-lg transition-all ${
                currentLanguage === 'hindi'
                  ? 'bg-[#00BAF2] text-white shadow-xs font-bold'
                  : 'text-[#002970] hover:text-[#00BAF2]'
              }`}
            >
              हिंदी
            </button>
            <button
              onClick={() => onLanguageChange('english')}
              className={`px-3 py-1 rounded-lg transition-all ${
                currentLanguage === 'english'
                  ? 'bg-[#00BAF2] text-white shadow-xs font-bold'
                  : 'text-[#002970] hover:text-[#00BAF2]'
              }`}
            >
              English
            </button>
          </div>

          {/* Quick Copilot CTA */}
          <button
            onClick={onOpenCopilot}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl bg-gradient-to-r from-[#002970] to-[#001F58] hover:from-[#00388F] hover:to-[#002970] text-white shadow-md shadow-[#002970]/20 border border-[#00BAF2]/40 transition-all active:scale-95"
          >
            <Bot className="w-4 h-4 text-[#00BAF2]" />
            <span>Ask Copilot</span>
          </button>
        </div>
      </div>
    </header>
  );
};
