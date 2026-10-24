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
  const isPositive = typeof card.change_pct === 'number' && card.change_pct > 0;
  const isNegative = typeof card.change_pct === 'number' && card.change_pct < 0;

  const displayLabel = localizeDynamicText(card.label, language);
  const displaySubtext = localizeDynamicText(card.subtext, language);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 p-5 sm:p-6 shadow-xs hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150 flex flex-col justify-between min-h-[148px]">
      <div>
        {/* Top: Label and Icon */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-[13px] font-medium text-slate-500 dark:text-slate-400 leading-normal truncate">
              {displayLabel}
            </span>
            {isHero && (
              <span className="inline-flex px-1.5 py-0.5 rounded text-[10px] font-semibold bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 border border-blue-200/70 dark:border-blue-800/60 uppercase tracking-wider shrink-0">
                Primary
              </span>
            )}
          </div>
          {icon && (
            <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200/60 dark:border-slate-700/60">
              {icon}
            </div>
          )}
        </div>

        {/* Value: Large, Confident Tabular Numeral */}
        <div className="mt-3 sm:mt-4">
          <span className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white tabular-nums leading-none block">
            {card.formatted_value}
          </span>
        </div>
      </div>

      {/* Bottom: Trend and Subtext */}
      {((card.change_pct !== null && card.change_pct !== undefined) || card.subtext) && (
        <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60 flex items-center flex-wrap gap-2 text-xs">
          {card.change_pct !== null && card.change_pct !== undefined && (
            <span
              className={`inline-flex items-center px-1.5 py-0.5 rounded-md font-medium text-xs border tabular-nums ${
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
            <span className="truncate font-normal text-slate-500 dark:text-slate-400 text-xs leading-normal">
              {displaySubtext}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
