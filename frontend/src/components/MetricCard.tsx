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
    navy: 'border-t-4 border-t-[#002970]',
    green: 'border-t-4 border-t-[#00B970]',
    orange: 'border-t-4 border-t-[#FF7A00]',
  };

  const iconBgColors = {
    cyan: 'bg-gradient-to-br from-[#E0F4FD] to-[#C9EDFC] text-[#00BAF2] border border-[#B3E3FA]',
    navy: 'bg-gradient-to-br from-[#E8F0FC] to-[#D5E5FA] text-[#002970] border border-[#B8D5F8]',
    green: 'bg-gradient-to-br from-[#E8F8F0] to-[#CEF2DE] text-[#008A54] border border-[#A7E5C0]',
    orange: 'bg-gradient-to-br from-[#FFF2E5] to-[#FFE0C4] text-[#E06000] border border-[#FFCE9E]',
  };

  return (
    <div
      className={`bg-white rounded-2xl border border-[#CDE5F7] p-5 shadow-xs hover:shadow-paytm transition-all duration-200 ${topBorderColors[accentColor]}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-[#4F6A94]">
          {card.label}
        </span>
        {icon && (
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-xs ${iconBgColors[accentColor]}`}>
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl lg:text-3xl font-black tracking-tight text-[#002970]">
          {card.formatted_value}
        </span>
      </div>

      {((card.change_pct !== null && card.change_pct !== undefined) || card.subtext) && (
        <div className="mt-3 flex items-center flex-wrap gap-1.5 text-xs text-[#4F6A94]">
          {card.change_pct !== null && card.change_pct !== undefined && (
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-md font-bold text-xs ${
                isPositive
                  ? 'bg-[#E8F8F0] text-[#008A54] border border-[#B6E8D0]'
                  : isNegative
                  ? 'bg-[#FEECEB] text-[#D92D20] border border-[#FECDCA]'
                  : 'bg-slate-100 text-slate-600 border border-slate-200'
              }`}
            >
              {isPositive && <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />}
              {isNegative && <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />}
              {!isPositive && !isNegative && <Minus className="w-3.5 h-3.5 mr-0.5" />}
              {Math.abs(card.change_pct)}%
            </span>
          )}
          {card.subtext && <span className="truncate font-medium text-slate-500">{card.subtext}</span>}
        </div>
      )}
    </div>
  );
};
