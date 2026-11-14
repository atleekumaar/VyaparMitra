import React, { useEffect, useState } from 'react';
import { Settings, Shield, Store, Globe, Server, CheckCircle2, RefreshCw, Sun, Moon, Palette, User, Phone, Mail } from 'lucide-react';
import { api } from '../api/client';
import { HealthStatus, UserProfile } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { PageHeader } from '../components/PageHeader';
import { SectionHeader } from '../components/SectionHeader';
import { CardSkeleton } from '../components/LoadingSkeleton';
import { useLanguage } from '../i18n/LanguageContext';

interface SettingsPageProps {
  currentLanguage?: string;
  onLanguageChange?: (lang: string) => void;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
  currentUser?: UserProfile | null;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  isDarkMode,
  onToggleDarkMode,
  onLanguageChange,
  currentUser,
}) => {
  const { language: currentLanguage, setLanguage } = useLanguage();
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

  const isDemo = currentUser?.is_demo ?? true;
  const merchantId = currentUser?.merchant_id || currentUser?.business_id || 'M001';
  const storeName = currentUser?.storeName || (isDemo ? 'Vyapar Kirana & General Store' : 'My Vyapar Store');
  const ownerName = currentUser?.name || (isDemo ? 'Demo Merchant' : 'Store Owner');
  const phone = currentUser?.phone || '—';
  const email = currentUser?.email || '—';

  return (
    <div className="space-y-6 max-w-5xl animate-in fade-in-50 duration-200">
      <PageHeader
        title="Merchant Settings & Diagnostics"
        subtitle="Manage appearance, dialect preferences, store profile, and intelligence telemetry status."
      />

      {/* Account / Tenant Status Notice */}
      <Card
        className={
          isDemo
            ? 'bg-amber-500/5 border-amber-500/20'
            : 'bg-emerald-500/5 border-emerald-500/20'
        }
      >
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div
              className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                isDemo
                  ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400'
                  : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
              }`}
            >
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-text">
                  {isDemo ? 'Demo Mode Active' : 'Dedicated Tenant Workspace'}
                </h3>
                <Badge variant={isDemo ? 'demo' : 'success'}>
                  {isDemo ? 'Simulated Dataset' : 'Active Merchant'}
                </Badge>
              </div>
              <p className="text-xs text-text-muted mt-0.5">
                {isDemo
                  ? 'Operating on benchmark retail kirana data. Switch to a personal login for isolated tenant records.'
                  : `Authenticated tenant (${merchantId}). Operational data is scoped to your merchant account.`}
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Store Identity & Profile */}
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <Store className="w-4 h-4 text-brand" />
          <SectionHeader
            title="Store Profile & Identity"
            subtitle="Registered merchant information used for invoice headers, customer ledger and tax receipts."
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-surface-muted/60 border border-border/50">
            <label className="text-text-muted font-medium block">Merchant ID / Business ID</label>
            <p className="font-bold text-text mt-1 text-sm font-mono tracking-tight">{merchantId}</p>
          </div>

          <div className="p-3.5 rounded-xl bg-surface-muted/60 border border-border/50">
            <label className="text-text-muted font-medium block">Store Legal Name</label>
            <p className="font-bold text-text mt-1 text-sm">{storeName}</p>
          </div>

          <div className="p-3.5 rounded-xl bg-surface-muted/60 border border-border/50">
            <label className="text-text-muted font-medium block">Owner / Authorized Name</label>
            <div className="flex items-center gap-1.5 mt-1">
              <User className="w-3.5 h-3.5 text-text-muted" />
              <p className="font-bold text-text text-sm">{ownerName}</p>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-surface-muted/60 border border-border/50">
            <label className="text-text-muted font-medium block">Contact Number</label>
            <div className="flex items-center gap-1.5 mt-1">
              <Phone className="w-3.5 h-3.5 text-text-muted" />
              <p className="font-semibold text-text text-sm">{phone}</p>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-surface-muted/60 border border-border/50">
            <label className="text-text-muted font-medium block">Email Address</label>
            <div className="flex items-center gap-1.5 mt-1">
              <Mail className="w-3.5 h-3.5 text-text-muted" />
              <p className="font-semibold text-text text-sm truncate">{email}</p>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-surface-muted/60 border border-border/50">
            <label className="text-text-muted font-medium block">Currency &amp; Accounting</label>
            <p className="font-semibold text-text mt-1 text-sm">₹ INR (Indian Rupee) • FY 2026-27</p>
          </div>
        </div>
      </Card>

      {/* Theme / Appearance Card */}
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <Palette className="w-4 h-4 text-brand" />
          <SectionHeader
            title="Appearance & Theme"
            subtitle="Choose between Day Light Mode and Midnight Fintech Dark Mode."
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div
            onClick={() => {
              if (isDarkMode) onToggleDarkMode();
            }}
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex items-center justify-between ${
              !isDarkMode
                ? 'border-brand bg-brand-soft/40 shadow-xs ring-1 ring-brand/30'
                : 'border-border bg-surface-muted/40 hover:border-brand/50'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-500 flex items-center justify-center border border-amber-500/20">
                <Sun className="w-5 h-5" />
              </div>
              <div>
                <span className="font-bold text-sm text-text block">Light Mode</span>
                <span className="text-xs text-text-muted">Fintech White &amp; Neutral Slate</span>
              </div>
            </div>
            {!isDarkMode && <CheckCircle2 className="w-5 h-5 text-brand" />}
          </div>

          <div
            onClick={() => {
              if (!isDarkMode) onToggleDarkMode();
            }}
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex items-center justify-between ${
              isDarkMode
                ? 'border-brand bg-brand-soft/40 shadow-xs ring-1 ring-brand/30'
                : 'border-border bg-surface-muted/40 hover:border-brand/50'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-brand/10 text-brand flex items-center justify-center border border-brand/20">
                <Moon className="w-5 h-5" />
              </div>
              <div>
                <span className="font-bold text-sm text-text block">Dark Mode</span>
                <span className="text-xs text-text-muted">Midnight Deep Navy</span>
              </div>
            </div>
            {isDarkMode && <CheckCircle2 className="w-5 h-5 text-brand" />}
          </div>
        </div>
      </Card>

      {/* Language Preference */}
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <Globe className="w-4 h-4 text-brand" />
          <SectionHeader
            title="Language & Dialect Preference"
            subtitle="Select dialect for AI Business Copilot answers and morning voice briefings."
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { id: 'hinglish', label: 'Hinglish (Recommended)', desc: 'Natural Hindi-English mix spoken by retail shop owners' },
            { id: 'hindi', label: 'हिंदी (Devanagari)', desc: 'Pure Devanagari script and terminology' },
            { id: 'english', label: 'English', desc: 'Standard business English syntax' },
          ].map((lang) => (
            <div
              key={lang.id}
              onClick={() => {
                setLanguage(lang.id as any);
                if (onLanguageChange) onLanguageChange(lang.id);
              }}
              className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                currentLanguage === lang.id
                  ? 'border-brand bg-brand-soft/40 ring-1 ring-brand/30 shadow-xs'
                  : 'border-border bg-surface-muted/40 hover:border-brand/50'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-text">{lang.label}</span>
                {currentLanguage === lang.id && (
                  <CheckCircle2 className="w-4 h-4 text-brand" />
                )}
              </div>
              <p className="text-xs text-text-muted mt-1.5 leading-relaxed">{lang.desc}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* System Diagnostics & Backend Health */}
      <Card>
        <div className="flex items-center justify-between border-b border-border pb-4 mb-4">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-brand" />
            <SectionHeader
              title="Backend Engine Health"
              subtitle="Real-time telemetry from FastAPI and ML pipeline components."
              className="mb-0"
            />
          </div>
          <Button variant="secondary" size="sm" onClick={fetchHealth}>
            <RefreshCw className="w-3.5 h-3.5 mr-1" />
            Refresh
          </Button>
        </div>

        {loadingHealth ? (
          <CardSkeleton />
        ) : health ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-3 rounded-xl bg-surface-muted/50 border border-border/50">
              <label className="text-text-muted font-medium block">Engine Status</label>
              <p className="font-bold text-success mt-1 uppercase tracking-wide flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-success inline-block animate-pulse" />
                {health.status}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-surface-muted/50 border border-border/50">
              <label className="text-text-muted font-medium block">Core Version</label>
              <p className="font-bold text-text mt-1">v{health.version}</p>
            </div>
            <div className="p-3 rounded-xl bg-surface-muted/50 border border-border/50">
              <label className="text-text-muted font-medium block">Environment</label>
              <p className="font-bold text-text mt-1 capitalize">{health.app_env}</p>
            </div>
            <div className="p-3 rounded-xl bg-surface-muted/50 border border-border/50">
              <label className="text-text-muted font-medium block">Pipeline Artifacts</label>
              <p className="font-bold text-success mt-1">
                {health.artifacts_ready ? '✓ All Loaded' : 'Pending Sync'}
              </p>
            </div>
          </div>
        ) : (
          <p className="text-xs text-danger font-medium">Could not reach backend health endpoint.</p>
        )}
      </Card>
    </div>
  );
};
