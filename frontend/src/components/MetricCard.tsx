import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { MetricCardData } from '../types';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';
import { MiniSparkline } from './charts/MiniSparkline';

interface MetricCardProps {
  card: MetricCardData;
  icon?: React.ReactNode;
  isHero?: boolean;
  loading?: boolean;
  sparklineData?: number[];
  variant?: 'blue' | 'purple' | 'amber' | 'emerald' | 'default';
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  card,
  icon,
  isHero = false,
  loading = false,
  sparklineData,
  variant = 'default',
  onClick,
}) => {
  const { language } = useLanguage();

  const variantStyles = {
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-950/50 dark:text-blue-400 border border-blue-200/50 dark:border-blue-900/50',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-950/50 dark:text-purple-400 border border-purple-200/50 dark:border-purple-900/50',
    amber: 'bg-amber-50 text-amber-600 dark:bg-amber-950/50 dark:text-amber-400 border border-amber-200/50 dark:border-amber-900/50',
    emerald: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-200/50 dark:border-emerald-900/50',
    default: 'bg-surface-muted text-text-muted border border-border/60',
  };

  if (loading) {
    return (
      <div className="bg-surface-card rounded-2xl border border-border p-5 sm:p-6 shadow-fintech animate-pulse flex flex-col justify-between min-h-[148px]">
        <div className="flex items-center justify-between">
          <div className="h-3.5 w-24 bg-surface-muted rounded" />
          <div className="w-8 h-8 rounded-xl bg-surface-muted" />
        </div>
        <div className="h-8 w-32 bg-surface-muted rounded-lg my-2" />
        <div className="h-4 w-40 bg-surface-muted rounded" />
      </div>
    );
  }

  const isPositive = typeof card.change_pct === 'number' && card.change_pct > 0;
  const isNegative = typeof card.change_pct === 'number' && card.change_pct < 0;

  const displayLabel = localizeDynamicText(card.label, language);
  const displaySubtext = localizeDynamicText(card.subtext, language);

  const isZeroOrEmpty =
    card.value === 0 ||
    card.value === '0' ||
    card.value === '₹0.00' ||
    card.value === '' ||
    card.value === null ||
    card.value === undefined;

  return (
    <div
      onClick={onClick}
      className={`bg-surface-card rounded-2xl border border-border p-5 sm:p-6 shadow-fintech hover:border-border-strong hover:shadow-fintech-md transition-all duration-150 flex flex-col justify-between min-h-[148px] group ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      <div>
        {/* Top: Label, Hero tag, and Icon */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-xs font-semibold text-text-muted leading-normal truncate">
              {displayLabel}
            </span>
            {isHero && (
              <span className="inline-flex px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-brand-soft text-brand border border-brand/20 uppercase tracking-wider shrink-0">
                Primary
              </span>
            )}
          </div>
          {icon && (
            <div className={`w-8.5 h-8.5 rounded-xl flex items-center justify-center shrink-0 transition-transform group-hover:scale-105 shadow-2xs ${variantStyles[variant]}`}>
              {icon}
            </div>
          )}
        </div>

        {/* Value: Large, Confident Tabular Numeral with optional mini sparkline */}
        <div className="mt-3 sm:mt-4 flex items-baseline justify-between gap-3">
          <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-text tabular-nums leading-none block">
            {isZeroOrEmpty && !card.formatted_value ? '—' : card.formatted_value || card.value}
          </span>
          {sparklineData && sparklineData.length >= 2 && (
            <div className="hidden sm:block">
              <MiniSparkline data={sparklineData} positive={isPositive} />
            </div>
          )}
        </div>
      </div>

      {/* Bottom: Trend Delta Chip & Subtext */}
      {((card.change_pct !== null && card.change_pct !== undefined) || card.subtext) && (
        <div className="mt-4 pt-3 border-t border-border/50 flex items-center flex-wrap gap-2 text-xs">
          {card.change_pct !== null && card.change_pct !== undefined ? (
            <span
              className={`inline-flex items-center px-1.5 py-0.5 rounded-full font-bold text-[11px] border tabular-nums ${
                isPositive
                  ? 'bg-success-soft text-success border-success/30'
                  : isNegative
                  ? 'bg-danger-soft text-danger border-danger/30'
                  : 'bg-surface-muted text-text-muted border-border'
              }`}
            >
              {isPositive && <ArrowUpRight className="w-3 h-3 mr-0.5" />}
              {isNegative && <ArrowDownRight className="w-3 h-3 mr-0.5" />}
              {!isPositive && !isNegative && <Minus className="w-3 h-3 mr-0.5" />}
              {Math.abs(card.change_pct)}%
            </span>
          ) : (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-semibold bg-surface-muted text-text-subtle border border-border">
              Baseline
            </span>
          )}
          {displaySubtext && (
            <span className="truncate font-medium text-text-muted text-[11px] leading-normal">
              {displaySubtext}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
