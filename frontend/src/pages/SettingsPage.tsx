import React, { useEffect, useState } from 'react';
import { Settings, Shield, Store, Globe, Server, CheckCircle2, RefreshCw } from 'lucide-react';
import { api } from '../api/client';
import { HealthStatus } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { CardSkeleton } from '../components/LoadingSkeleton';

interface SettingsPageProps {
  currentLanguage: string;
  onLanguageChange: (lang: string) => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  currentLanguage,
  onLanguageChange,
}) => {
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
        <h2 className="text-xl font-bold text-paytm-dark">Merchant Settings & Diagnostics</h2>
        <p className="text-xs text-paytm-muted mt-0.5">
          Configure language preferences, store identity, and review intelligence engine status.
        </p>
      </div>

      {/* Demo Mode Notice */}
      <div className="bg-paytm-light rounded-xl border border-paytm-border p-5">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-paytm-blue" />
          <h3 className="text-sm font-bold text-paytm-dark">Demo Mode Active</h3>
          <Badge variant="demo">Synthetic Data Foundation</Badge>
        </div>
        <p className="text-xs text-paytm-text mt-2 leading-relaxed">
          VyaparMitra is operating on a validated synthetic dataset mirroring Indian small merchant operations
          (kirana, electronics, apparel). Real telemetry, live payment rails, and production deployment are intentionally
          isolated in this release.
        </p>
      </div>

      {/* Store Identity */}
      <div className="bg-white rounded-xl border border-paytm-border p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2 border-b border-paytm-border pb-3">
          <Store className="w-4 h-4 text-paytm-blue" />
          <h3 className="text-sm font-bold text-paytm-dark">Store Profile</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="text-paytm-muted font-medium">Merchant ID</label>
            <p className="font-semibold text-paytm-dark mt-0.5">M001</p>
          </div>
          <div>
            <label className="text-paytm-muted font-medium">Store Legal Name</label>
            <p className="font-semibold text-paytm-dark mt-0.5">Vyapar Kirana & General Store</p>
          </div>
          <div>
            <label className="text-paytm-muted font-medium">Primary Category</label>
            <p className="font-semibold text-paytm-dark mt-0.5">Grocery, Snacks & FMCG</p>
          </div>
          <div>
            <label className="text-paytm-muted font-medium">Currency & Locale</label>
            <p className="font-semibold text-paytm-dark mt-0.5">₹ INR (Indian Rupee)</p>
          </div>
        </div>
      </div>

      {/* Language Preference */}
      <div className="bg-white rounded-xl border border-paytm-border p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2 border-b border-paytm-border pb-3">
          <Globe className="w-4 h-4 text-paytm-blue" />
          <h3 className="text-sm font-bold text-paytm-dark">Language Preference</h3>
        </div>

        <p className="text-xs text-paytm-muted">
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
              onClick={() => onLanguageChange(lang.id)}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                currentLanguage === lang.id
                  ? 'border-paytm-blue bg-paytm-light ring-2 ring-paytm-blue/20'
                  : 'border-paytm-border bg-white hover:border-slate-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-paytm-dark">{lang.label}</span>
                {currentLanguage === lang.id && (
                  <CheckCircle2 className="w-4 h-4 text-paytm-blue" />
                )}
              </div>
              <p className="text-[11px] text-paytm-muted mt-1">{lang.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* System Diagnostics & Backend Health */}
      <div className="bg-white rounded-xl border border-paytm-border p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-paytm-border pb-3">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-paytm-blue" />
            <h3 className="text-sm font-bold text-paytm-dark">Backend Engine Health</h3>
          </div>
          <Button variant="secondary" size="sm" onClick={fetchHealth}>
            <RefreshCw className="w-3.5 h-3.5 mr-1" />
            Refresh
          </Button>
        </div>

        {loadingHealth ? (
          <CardSkeleton />
        ) : health ? (
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-paytm-dark font-medium">API Status</span>
              <Badge variant="success">● {health.status.toUpperCase()}</Badge>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-paytm-dark font-medium">Intelligence Artifacts (Phases 1-4)</span>
              <Badge variant={health.artifacts_ready ? 'success' : 'critical'}>
                {health.artifacts_ready ? 'Available & Mounted' : 'Missing Artifacts'}
              </Badge>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-paytm-dark font-medium">Active Copilot Sessions</span>
              <span className="font-mono text-paytm-dark">{health.active_copilot_sessions} sessions</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-paytm-dark font-medium">API Version &amp; Environment</span>
              <span className="font-mono text-paytm-muted">{health.version} ({health.app_env})</span>
            </div>
          </div>
        ) : (
          <p className="text-xs text-red-600">Could not retrieve system health from /api/health.</p>
        )}
      </div>
    </div>
  );
};
