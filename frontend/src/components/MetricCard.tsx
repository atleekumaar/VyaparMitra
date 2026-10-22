import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { MetricCardData } from '../types';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';

interface MetricCardProps {
  card: MetricCardData;
  icon?: React.ReactNode;
  accentColor?: 'cyan' | 'navy' | 'green' | 'orange' | 'blue' | 'purple';
}

export const MetricCard: React.FC<MetricCardProps> = ({ card, icon, accentColor = 'blue' }) => {
  const { language } = useLanguage();
  const isPositive = card.change_pct && card.change_pct > 0;
  const isNegative = card.change_pct && card.change_pct < 0;

  const displayLabel = localizeDynamicText(card.label, language);
  const displaySubtext = localizeDynamicText(card.subtext, language);

  const iconColors: Record<string, string> = {
    cyan: 'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-400',
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-400',
    navy: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
    green: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400',
    orange: 'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-400',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-950/40 dark:text-purple-400',
  };

  const iconClass = iconColors[accentColor] || iconColors.blue;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-xs hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {displayLabel}
        </span>
        {icon && (
          <div className={`w-9 h-9 rounded-lg flex items-center justify-center transition-colors ${iconClass}`}>
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
          {card.formatted_value}
        </span>
      </div>

      {((card.change_pct !== null && card.change_pct !== undefined) || card.subtext) && (
        <div className="mt-3 flex items-center flex-wrap gap-2 text-xs text-slate-500 dark:text-slate-400">
          {card.change_pct !== null && card.change_pct !== undefined && (
            <span
              className={`inline-flex items-center px-1.5 py-0.5 rounded font-semibold text-xs border ${
                isPositive
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200/80 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/50'
                  : isNegative
                  ? 'bg-red-50 text-red-700 border-red-200/80 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800/50'
                  : 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700'
              }`}
            >
              {isPositive && <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />}
              {isNegative && <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />}
              {!isPositive && !isNegative && <Minus className="w-3.5 h-3.5 mr-0.5" />}
              {Math.abs(card.change_pct)}%
            </span>
          )}
          {displaySubtext && (
            <span className="truncate font-medium text-slate-500 dark:text-slate-400">
              {displaySubtext}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
