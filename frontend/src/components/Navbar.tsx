import React from 'react';
import { Bot, HelpCircle, Store, Bell, CheckCircle2 } from 'lucide-react';
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
    <header className="sticky top-0 z-30 bg-white border-b border-paytm-border px-4 lg:px-8 py-3 flex items-center justify-between">
      {/* Left: Merchant Store Profile */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-paytm-dark flex items-center justify-center text-white font-bold text-lg shadow-xs">
          VM
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold text-paytm-dark tracking-tight">
              Vyapar Kirana Store
            </h1>
            <Badge variant="demo" className="hidden sm:inline-flex">
              Demo Mode
            </Badge>
          </div>
          <p className="text-xs text-paytm-muted flex items-center gap-1.5">
            <Store className="w-3 h-3" /> Merchant ID: M001 &bull; Retail & Grocery
          </p>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-3">
        {/* System Health Dot */}
        <div
          className="hidden md:flex items-center gap-1.5 text-xs text-paytm-muted px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200"
          title="Intelligence Engine Status"
        >
          <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
          <span className="font-medium text-slate-700">{isHealthy ? 'Models Active' : 'Offline'}</span>
        </div>

        {/* Language Selector */}
        <div className="flex items-center bg-paytm-light border border-paytm-border rounded-lg p-0.5 text-xs font-medium">
          <button
            onClick={() => onLanguageChange('hinglish')}
            className={`px-2.5 py-1 rounded-md transition-all ${
              currentLanguage === 'hinglish'
                ? 'bg-paytm-blue text-white shadow-xs'
                : 'text-paytm-text hover:text-paytm-blue'
            }`}
          >
            Hinglish
          </button>
          <button
            onClick={() => onLanguageChange('hindi')}
            className={`px-2.5 py-1 rounded-md transition-all ${
              currentLanguage === 'hindi'
                ? 'bg-paytm-blue text-white shadow-xs'
                : 'text-paytm-text hover:text-paytm-blue'
            }`}
          >
            हिंदी
          </button>
          <button
            onClick={() => onLanguageChange('english')}
            className={`px-2.5 py-1 rounded-md transition-all ${
              currentLanguage === 'english'
                ? 'bg-paytm-blue text-white shadow-xs'
                : 'text-paytm-text hover:text-paytm-blue'
            }`}
          >
            English
          </button>
        </div>

        {/* Quick Copilot CTA */}
        <button
          onClick={onOpenCopilot}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-paytm-dark hover:bg-slate-800 text-white shadow-xs transition-all"
        >
          <Bot className="w-4 h-4 text-paytm-blue" />
          <span>Ask Copilot</span>
        </button>
      </div>
    </header>
  );
};
