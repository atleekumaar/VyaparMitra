import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { MetricCardData } from '../types';

interface MetricCardProps {
  card: MetricCardData;
  icon?: React.ReactNode;
  accentColor?: 'cyan' | 'navy' | 'green' | 'orange';
}

export const MetricCard: React.FC<MetricCardProps> = ({ card, icon, accentColor = 'cyan' }) => {
  const isPositive = card.change_pct && card.change_pct > 0;
  const isNegative = card.change_pct && card.change_pct < 0;

  const topBorderColors = {
    cyan: 'border-t-4 border-t-[#00BAF2]',
    navy: 'border-t-4 border-t-[#002970] dark:border-t-[#00BAF2]',
    green: 'border-t-4 border-t-[#00B970]',
    orange: 'border-t-4 border-t-[#FF7A00]',
  };

  const iconBgColors = {
    cyan: 'bg-gradient-to-br from-[#E0F4FD] to-[#C9EDFC] dark:from-[#0B254A] dark:to-[#0F356B] text-[#00BAF2] border border-[#B3E3FA] dark:border-[#1A4B8C]',
    navy: 'bg-gradient-to-br from-[#E8F0FC] to-[#D5E5FA] dark:from-[#112447] dark:to-[#173263] text-[#002970] dark:text-[#00BAF2] border border-[#B8D5F8] dark:border-[#224685]',
    green: 'bg-gradient-to-br from-[#E8F8F0] to-[#CEF2DE] dark:from-[#0B3320] dark:to-[#104A2E] text-[#008A54] dark:text-[#00B970] border border-[#A7E5C0] dark:border-[#1B633F]',
    orange: 'bg-gradient-to-br from-[#FFF2E5] to-[#FFE0C4] dark:from-[#3D2005] dark:to-[#572E07] text-[#E06000] dark:text-[#FF9433] border border-[#FFCE9E] dark:border-[#7A410B]',
  };

  return (
    <div
      className={`bg-white dark:bg-[#0F1D38] rounded-2xl border border-[#CDE5F7] dark:border-[#1E3A6E] p-5 shadow-xs hover:shadow-paytm transition-all duration-200 ${topBorderColors[accentColor]}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-[#4F6A94] dark:text-blue-200">
          {card.label}
        </span>
        {icon && (
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-xs ${iconBgColors[accentColor]}`}>
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl lg:text-3xl font-black tracking-tight text-[#002970] dark:text-white">
          {card.formatted_value}
        </span>
      </div>

      {((card.change_pct !== null && card.change_pct !== undefined) || card.subtext) && (
        <div className="mt-3 flex items-center flex-wrap gap-1.5 text-xs text-[#4F6A94] dark:text-slate-400">
          {card.change_pct !== null && card.change_pct !== undefined && (
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-md font-bold text-xs ${
                isPositive
                  ? 'bg-[#E8F8F0] dark:bg-[#00B970]/20 text-[#008A54] dark:text-[#00E68A] border border-[#B6E8D0] dark:border-[#00B970]/30'
                  : isNegative
                  ? 'bg-[#FEECEB] dark:bg-[#FF4D4D]/20 text-[#D92D20] dark:text-[#FF8080] border border-[#FECDCA] dark:border-[#FF4D4D]/30'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
              }`}
            >
              {isPositive && <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />}
              {isNegative && <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />}
              {!isPositive && !isNegative && <Minus className="w-3.5 h-3.5 mr-0.5" />}
              {Math.abs(card.change_pct)}%
            </span>
          )}
          {card.subtext && <span className="truncate font-medium text-slate-500 dark:text-slate-400">{card.subtext}</span>}
        </div>
      )}
    </div>
  );
};
