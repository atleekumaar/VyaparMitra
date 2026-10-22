import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { MetricCardData } from '../types';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';

interface MetricCardProps {
  card: MetricCardData;
  icon?: React.ReactNode;
  accentColor?: 'cyan' | 'navy' | 'green' | 'orange' | 'blue' | 'purple';
  isHero?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  card,
  icon,
  accentColor = 'blue',
  isHero = false,
}) => {
  const { language } = useLanguage();
  const isPositive = card.change_pct && card.change_pct > 0;
  const isNegative = card.change_pct && card.change_pct < 0;

  const displayLabel = localizeDynamicText(card.label, language);
  const displaySubtext = localizeDynamicText(card.subtext, language);

  const iconColors: Record<string, string> = {
    cyan: 'bg-blue-50 text-blue-600 dark:bg-blue-950/50 dark:text-blue-400 border-blue-200/60 dark:border-blue-800/60',
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-950/50 dark:text-blue-400 border-blue-200/60 dark:border-blue-800/60',
    navy: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200/80 dark:border-slate-700/80',
    green: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400 border-emerald-200/60 dark:border-emerald-800/60',
    orange: 'bg-amber-50 text-amber-600 dark:bg-amber-950/50 dark:text-amber-400 border-amber-200/60 dark:border-amber-800/60',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-950/50 dark:text-purple-400 border-purple-200/60 dark:border-purple-800/60',
  };

  const iconClass = iconColors[accentColor] || iconColors.blue;

  return (
    <div
      className={`bg-white dark:bg-slate-900 rounded-xl border p-5 shadow-xs transition-all duration-150 flex flex-col justify-between min-h-[142px] ${
        isHero
          ? 'border-slate-200/80 dark:border-slate-800 border-l-4 border-l-blue-600 dark:border-l-blue-500 hover:border-slate-300 dark:hover:border-slate-700'
          : 'border-slate-200/80 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
      }`}
    >
      <div>
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 truncate">
              {displayLabel}
            </span>
            {isHero && (
              <span className="inline-flex px-1.5 py-0.2 rounded text-[9px] font-extrabold uppercase tracking-wider bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 border border-blue-200/60 dark:border-blue-800/60">
                Primary
              </span>
            )}
          </div>
          {icon && (
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border ${iconClass}`}>
              {icon}
            </div>
          )}
        </div>

        <div className="mt-2.5">
          <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white tabular-nums block">
            {card.formatted_value}
          </span>
        </div>
      </div>

      {((card.change_pct !== null && card.change_pct !== undefined) || card.subtext) && (
        <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800/60 flex items-center flex-wrap gap-2 text-xs">
          {card.change_pct !== null && card.change_pct !== undefined && (
            <span
              className={`inline-flex items-center px-1.5 py-0.5 rounded-full font-bold text-[11px] border ${
                isPositive
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200/80 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/50'
                  : isNegative
                  ? 'bg-red-50 text-red-700 border-red-200/80 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800/50'
                  : 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700'
              }`}
            >
              {isPositive && <ArrowUpRight className="w-3 h-3 mr-0.5" />}
              {isNegative && <ArrowDownRight className="w-3 h-3 mr-0.5" />}
              {!isPositive && !isNegative && <Minus className="w-3 h-3 mr-0.5" />}
              {Math.abs(card.change_pct)}%
            </span>
          )}
          {displaySubtext && (
            <span className="truncate font-medium text-slate-500 dark:text-slate-400 text-xs">
              {displaySubtext}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
