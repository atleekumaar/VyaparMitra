import React from 'react';
import { Store, TrendingUp, Sparkles, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageContext';

export const LoginBrandPanel: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div className="relative hidden lg:flex flex-col justify-between p-10 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white overflow-hidden rounded-3xl m-2 select-none shadow-2xl min-h-[580px]">
      {/* Ambient pastel mesh glow */}
      <div className="absolute -top-24 -left-24 w-80 h-80 rounded-full bg-pink-400/25 blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 -right-20 w-80 h-80 rounded-full bg-cyan-300/30 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-20 left-1/4 w-80 h-80 rounded-full bg-purple-500/30 blur-3xl pointer-events-none" />

      {/* Top Value Prop Pill */}
      <div className="relative z-10">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/20 backdrop-blur-md text-xs font-semibold border border-white/30 text-white shadow-xs">
          <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-pulse" />
          <span>AI-Powered Business Assistant</span>
        </div>
      </div>

      {/* Center 3D Retail Store Showcase with Floating Badges */}
      <div className="relative z-10 flex flex-col items-center justify-center my-auto py-4">
        <div className="relative w-72 h-64 flex items-center justify-center">
          
          {/* Floating Sky Blue Chart Badge (Top Left) */}
          <div className="absolute -top-3 -left-4 z-20 bg-white/95 text-slate-800 rounded-2xl p-3 shadow-xl border border-white/60 backdrop-blur-md flex items-center gap-2.5 animate-bounce [animation-duration:4s]">
            <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
              <TrendingUp className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] text-slate-500 font-semibold block uppercase">Sales Growth</span>
              <span className="text-xs font-black text-emerald-600">+28.4%</span>
            </div>
          </div>

          {/* Floating Golden Rupee Badge (Bottom Left) */}
          <div className="absolute -bottom-2 -left-6 z-20 bg-amber-400 text-slate-900 rounded-2xl p-3 shadow-xl border border-amber-300/60 flex items-center justify-center animate-bounce [animation-duration:5s] [animation-delay:1s]">
            <div className="w-9 h-9 rounded-xl bg-amber-300/50 flex items-center justify-center text-xl font-black">
              ₹
            </div>
          </div>

          {/* Floating Royal Purple AI Badge (Bottom Right) */}
          <div className="absolute -bottom-3 -right-4 z-20 bg-gradient-to-tr from-purple-700 to-indigo-500 text-white rounded-2xl p-3 shadow-xl border border-purple-400/40 flex items-center gap-2 animate-bounce [animation-duration:4.5s] [animation-delay:0.5s]">
            <div className="w-8 h-8 rounded-xl bg-white/20 flex items-center justify-center font-bold">
              <Sparkles className="w-4 h-4 text-amber-300" />
            </div>
            <div>
              <span className="text-[10px] text-purple-200 font-semibold block uppercase">AI Model</span>
              <span className="text-xs font-black tracking-wide">Ai+</span>
            </div>
          </div>

          {/* 3D Illustrated Retail Storefront Card ("My Store") */}
          <div className="w-56 bg-white rounded-2xl shadow-2xl p-4 border border-white/80 relative text-slate-800">
            {/* Store Signboard */}
            <div className="mx-auto w-24 py-1 rounded-md bg-blue-600 text-white text-[11px] font-bold text-center tracking-wide mb-2 shadow-xs">
              My Store
            </div>

            {/* Striped Awning */}
            <div className="flex h-5 rounded-t-md overflow-hidden shadow-inner">
              <div className="flex-1 bg-blue-600" />
              <div className="flex-1 bg-white" />
              <div className="flex-1 bg-blue-600" />
              <div className="flex-1 bg-white" />
              <div className="flex-1 bg-blue-600" />
              <div className="flex-1 bg-white" />
              <div className="flex-1 bg-blue-600" />
            </div>

            {/* Storefront Window and Door */}
            <div className="bg-slate-50 border border-slate-200 rounded-b-md p-3 flex items-end justify-between gap-3 h-28">
              {/* Shop Window */}
              <div className="w-16 h-18 bg-sky-100 rounded border border-sky-200 flex flex-col justify-between p-1.5">
                <div className="w-full h-1.5 bg-sky-200 rounded-full" />
                <div className="w-2/3 h-1.5 bg-sky-200 rounded-full" />
                <div className="w-full h-1 bg-amber-400 rounded-full" />
              </div>

              {/* Shop Door */}
              <div className="w-12 h-20 bg-blue-700 rounded-t border-t border-x border-blue-800 flex items-center justify-end pr-1 shadow-inner">
                <div className="w-1.5 h-1.5 rounded-full bg-amber-300" />
              </div>
            </div>
          </div>

        </div>

        {/* Caption */}
        <h3 className="text-xl font-extrabold text-center tracking-tight mt-6">
          Grow Your Business with AI
        </h3>
        <p className="text-xs text-blue-100 text-center max-w-xs mt-1.5 font-normal leading-relaxed">
          Intelligent kirana command center — track sales, automate inventory restock, and predict 7-day demand.
        </p>
      </div>

      {/* Bottom Trust Guarantee */}
      <div className="relative z-10 pt-4 border-t border-white/20 flex items-center justify-between text-xs text-blue-100">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-300" />
          <span>Bank-Grade Encryption</span>
        </div>
        <span className="text-[11px] text-blue-200 font-mono">VyaparMitra AI</span>
      </div>
    </div>
  );
};
