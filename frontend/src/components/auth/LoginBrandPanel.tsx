import React from 'react';
import { Store, ShieldCheck, Volume2, Sparkles, TrendingUp, CheckCircle2 } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageContext';

export const LoginBrandPanel: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div className="relative hidden lg:flex flex-col justify-between p-12 bg-gradient-to-br from-brand to-brand-hover text-white overflow-hidden rounded-3xl m-3 select-none">
      {/* Subtle background decorative shapes */}
      <div className="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-white/10 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -right-24 w-96 h-96 rounded-full bg-blue-900/30 blur-3xl pointer-events-none" />

      {/* Brand Header */}
      <div className="relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-white text-brand flex items-center justify-center font-black text-base shadow-fintech-md">
            VM
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight">
              Vyapar<span className="text-blue-200">Mitra</span>
            </h1>
            <span className="text-[11px] font-medium text-blue-100 uppercase tracking-wider block">
              Fintech Operating System for Bharat Merchants
            </span>
          </div>
        </div>
      </div>

      {/* Center Value Proposition */}
      <div className="relative z-10 space-y-6 my-auto py-10 max-w-md">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 backdrop-blur-md text-xs font-semibold border border-white/20">
          <Sparkles className="w-3.5 h-3.5 text-amber-300" />
          <span>AI-Powered Commerce &amp; Smart Khata</span>
        </div>

        <h2 className="text-3xl font-extrabold leading-tight tracking-tight">
          Aapki dukan ka digital munim aur smart business partner.
        </h2>

        <p className="text-sm text-blue-100 leading-relaxed font-normal">
          Real-time inventory alerts, daily sales tracking, automated UPI soundbox notifications,
          aur multi-lingual AI business copilot ek single unified platform par.
        </p>

        {/* Feature bullets */}
        <div className="space-y-3 pt-2">
          {[
            { title: 'Zero Commission Billing & Cash Register', icon: Store },
            { title: 'Instant 4G Smart Audio Soundbox alerts', icon: Volume2 },
            { title: 'Multi-Tenant Data Privacy & ISO Bank Grade Security', icon: ShieldCheck },
            { title: 'Predictive 7-Day Demand & Reorder Forecasts', icon: TrendingUp },
          ].map((item, idx) => (
            <div key={idx} className="flex items-center gap-3 text-xs font-medium text-white/95">
              <div className="w-6 h-6 rounded-lg bg-white/20 flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-3.5 h-3.5 text-white" />
              </div>
              <span>{item.title}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Trust Guarantee */}
      <div className="relative z-10 pt-6 border-t border-white/15 flex items-center justify-between text-xs text-blue-100">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-300" />
          <span>100% Encrypted &amp; Secure Cloud Storage</span>
        </div>
        <span className="text-[11px] text-blue-200">v1.0.0 Fintech</span>
      </div>
    </div>
  );
};
