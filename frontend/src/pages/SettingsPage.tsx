import React, { useEffect, useState } from 'react';
import { Settings, Shield, Store, Globe, Server, CheckCircle2, RefreshCw, Sun, Moon, Palette } from 'lucide-react';
import { api } from '../api/client';
import { HealthStatus } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { CardSkeleton } from '../components/LoadingSkeleton';
import { useLanguage } from '../i18n/LanguageContext';

interface SettingsPageProps {
  currentLanguage?: string;
  onLanguageChange?: (lang: string) => void;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  isDarkMode,
  onToggleDarkMode,
  onLanguageChange,
}) => {
  const { language: currentLanguage, setLanguage, t } = useLanguage();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loadingHealth, setLoadingHealth] = useState<boolean>(true);

  const fetchHealth = async () => {
    setLoadingHealth(true);
    try {
      const res = await api.getHealth();
      setHealth(res);
    } catch {
      setHealth(null);
    } finally {
      setLoadingHealth(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="space-y-6 max-w-4xl animate-in fade-in-50 duration-200">
      <div>
        <h2 className="text-xl lg:text-2xl font-black text-[#002970] dark:text-white">Merchant Settings &amp; Diagnostics</h2>
        <p className="text-xs text-[#4F6A94] dark:text-blue-200 mt-0.5 font-medium">
          Configure theme, language preferences, store identity, and review intelligence engine status.
        </p>
      </div>

      {/* Theme / Appearance Card */}
      <div className="bg-white dark:bg-[#0F1D38] rounded-2xl border-2 border-[#CDE5F7] dark:border-[#1E3A6E] p-6 shadow-paytm space-y-4 transition-colors">
        <div className="flex items-center gap-2.5 border-b border-[#E8F4FD] dark:border-[#1E3A6E] pb-3">
          <Palette className="w-5 h-5 text-[#00BAF2]" />
          <h3 className="text-base font-extrabold text-[#002970] dark:text-white">Appearance &amp; Theme</h3>
        </div>

        <p className="text-xs text-[#4F6A94] dark:text-blue-200 font-medium">
          Choose between Paytm Light Mode and Midnight Dark Mode.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div
            onClick={() => {
              if (isDarkMode) onToggleDarkMode();
            }}
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex items-center justify-between ${
              !isDarkMode
                ? 'border-[#00BAF2] bg-[#F0F8FE] shadow-sm'
                : 'border-[#CDE5F7] dark:border-[#1E3A6E] bg-white dark:bg-[#132342] opacity-75 hover:opacity-100'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-white text-[#002970] flex items-center justify-center shadow-xs border border-[#CDE5F7]">
                <Sun className="w-5 h-5 text-[#FFB800]" />
              </div>
              <div>
                <span className="font-extrabold text-sm text-[#002970] dark:text-white block">Light Mode</span>
                <span className="text-[11px] text-[#4F6A94] dark:text-blue-200">Paytm Signature Ice Blue</span>
              </div>
            </div>
            {!isDarkMode && <CheckCircle2 className="w-5 h-5 text-[#00BAF2]" />}
          </div>

          <div
            onClick={() => {
              if (!isDarkMode) onToggleDarkMode();
            }}
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex items-center justify-between ${
              isDarkMode
                ? 'border-[#00BAF2] bg-[#0B254A] shadow-sm'
                : 'border-[#CDE5F7] bg-white hover:border-[#00BAF2] opacity-75 hover:opacity-100'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-[#001D52] text-[#00BAF2] flex items-center justify-center shadow-xs border border-[#00BAF2]/30">
                <Moon className="w-5 h-5 text-[#00BAF2]" />
              </div>
              <div>
                <span className="font-extrabold text-sm text-[#002970] dark:text-white block">Dark Mode</span>
                <span className="text-[11px] text-[#4F6A94] dark:text-blue-200">Midnight Fintech Navy</span>
              </div>
            </div>
            {isDarkMode && <CheckCircle2 className="w-5 h-5 text-[#00BAF2]" />}
          </div>
        </div>
      </div>

      {/* Demo Mode Notice */}
      <div className="bg-[#F0F8FE] dark:bg-[#132342] rounded-2xl border-2 border-[#CDE5F7] dark:border-[#1E3A6E] p-5 shadow-xs transition-colors">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-[#00BAF2]" />
          <h3 className="text-sm font-extrabold text-[#002970] dark:text-white">Demo Mode Active</h3>
          <Badge variant="demo">Synthetic Data Foundation</Badge>
        </div>
        <p className="text-xs text-[#0F2042] dark:text-blue-100 mt-2 leading-relaxed font-medium">
          VyaparMitra is operating on a validated synthetic dataset mirroring Indian small merchant operations
          (kirana, electronics, apparel). Real telemetry, live payment rails, and production deployment are intentionally
          isolated in this release.
        </p>
      </div>

      {/* Store Identity */}
      <div className="bg-white dark:bg-[#0F1D38] rounded-2xl border-2 border-[#CDE5F7] dark:border-[#1E3A6E] p-6 shadow-paytm space-y-4 transition-colors">
        <div className="flex items-center gap-2.5 border-b border-[#E8F4FD] dark:border-[#1E3A6E] pb-3">
          <Store className="w-5 h-5 text-[#00BAF2]" />
          <h3 className="text-base font-extrabold text-[#002970] dark:text-white">Store Profile</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="text-[#4F6A94] dark:text-blue-200 font-semibold">Merchant ID</label>
            <p className="font-black text-[#002970] dark:text-white mt-0.5 text-sm">M001</p>
          </div>
          <div>
            <label className="text-[#4F6A94] dark:text-blue-200 font-semibold">Store Legal Name</label>
            <p className="font-bold text-[#002970] dark:text-white mt-0.5 text-sm">Vyapar Kirana &amp; General Store</p>
          </div>
          <div>
            <label className="text-[#4F6A94] dark:text-blue-200 font-semibold">Primary Category</label>
            <p className="font-bold text-[#002970] dark:text-white mt-0.5 text-sm">Grocery, Snacks &amp; FMCG</p>
          </div>
          <div>
            <label className="text-[#4F6A94] dark:text-blue-200 font-semibold">Currency &amp; Locale</label>
            <p className="font-bold text-[#002970] dark:text-white mt-0.5 text-sm">₹ INR (Indian Rupee)</p>
          </div>
        </div>
      </div>

      {/* Language Preference */}
      <div className="bg-white dark:bg-[#0F1D38] rounded-2xl border-2 border-[#CDE5F7] dark:border-[#1E3A6E] p-6 shadow-paytm space-y-4 transition-colors">
        <div className="flex items-center gap-2.5 border-b border-[#E8F4FD] dark:border-[#1E3A6E] pb-3">
          <Globe className="w-5 h-5 text-[#00BAF2]" />
          <h3 className="text-base font-extrabold text-[#002970] dark:text-white">Language Preference</h3>
        </div>

        <p className="text-xs text-[#4F6A94] dark:text-blue-200 font-medium">
          Select the default dialect for the AI Business Copilot and morning audio/text briefings.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            { id: 'hinglish', label: 'Hinglish (Default)', desc: 'Natural Latin Hindi mix for retail merchants' },
            { id: 'hindi', label: 'हिंदी (Devanagari)', desc: 'Pure Devanagari script responses' },
            { id: 'english', label: 'English', desc: 'Standard business English' },
          ].map((lang) => (
            <div
              key={lang.id}
              onClick={() => {
                setLanguage(lang.id as any);
                if (onLanguageChange) onLanguageChange(lang.id);
              }}
              className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                currentLanguage === lang.id
                  ? 'border-[#00BAF2] bg-[#F0F8FE] dark:bg-[#0B254A] ring-2 ring-[#00BAF2]/30 shadow-xs'
                  : 'border-[#CDE5F7] dark:border-[#1E3A6E] bg-white dark:bg-[#132342] hover:border-[#00BAF2]'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-[#002970] dark:text-white">{lang.label}</span>
                {currentLanguage === lang.id && (
                  <CheckCircle2 className="w-4 h-4 text-[#00BAF2]" />
                )}
              </div>
              <p className="text-[11px] text-[#4F6A94] dark:text-blue-200 mt-1">{lang.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* System Diagnostics & Backend Health */}
      <div className="bg-white dark:bg-[#0F1D38] rounded-2xl border-2 border-[#CDE5F7] dark:border-[#1E3A6E] p-6 shadow-paytm space-y-4 transition-colors">
        <div className="flex items-center justify-between border-b border-[#E8F4FD] dark:border-[#1E3A6E] pb-3">
          <div className="flex items-center gap-2.5">
            <Server className="w-5 h-5 text-[#00BAF2]" />
            <h3 className="text-base font-extrabold text-[#002970] dark:text-white">Backend Engine Health</h3>
          </div>
          <Button variant="secondary" size="sm" onClick={fetchHealth} className="dark:bg-[#132342] dark:border-[#1E3A6E] dark:text-white">
            <RefreshCw className="w-3.5 h-3.5 mr-1" />
            Refresh
          </Button>
        </div>

        {loadingHealth ? (
          <CardSkeleton />
        ) : health ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <label className="text-[#4F6A94] dark:text-blue-200 font-semibold">Engine Status</label>
              <p className="font-extrabold text-[#008A54] dark:text-[#00E68A] mt-0.5 uppercase tracking-wide">
                ● {health.status}
              </p>
            </div>
            <div>
              <label className="text-[#4F6A94] dark:text-blue-200 font-semibold">Version</label>
              <p className="font-bold text-[#002970] dark:text-white mt-0.5">v{health.version}</p>
            </div>
            <div>
              <label className="text-[#4F6A94] dark:text-blue-200 font-semibold">Environment</label>
              <p className="font-bold text-[#002970] dark:text-white mt-0.5 capitalize">{health.app_env}</p>
            </div>
            <div>
              <label className="text-[#4F6A94] dark:text-blue-200 font-semibold">Artifacts</label>
              <p className="font-bold text-[#008A54] dark:text-[#00E68A] mt-0.5">
                {health.artifacts_ready ? '✓ All Ready' : 'Pending'}
              </p>
            </div>
          </div>
        ) : (
          <p className="text-xs text-red-500 font-medium">Could not reach backend health endpoint.</p>
        )}
      </div>
    </div>
  );
};
