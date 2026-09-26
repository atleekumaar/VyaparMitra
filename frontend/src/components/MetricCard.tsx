import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { MetricCardData } from '../types';

interface MetricCardProps {
  card: MetricCardData;
  icon?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({ card, icon }) => {
  const isPositive = card.change_pct && card.change_pct > 0;
  const isNegative = card.change_pct && card.change_pct < 0;

  return (
    <div className="bg-white rounded-xl border border-paytm-border p-5 shadow-xs hover:shadow-sm transition-shadow">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-paytm-muted">
          {card.label}
        </span>
        {icon && (
          <div className="w-8 h-8 rounded-lg bg-paytm-light text-paytm-blue flex items-center justify-center">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-paytm-dark">
          {card.formatted_value}
        </span>
      </div>

      {(card.change_pct !== null && card.change_pct !== undefined || card.subtext) && (
        <div className="mt-2.5 flex items-center text-xs text-paytm-muted">
          {card.change_pct !== null && card.change_pct !== undefined && (
            <span
              className={`inline-flex items-center font-semibold mr-1.5 ${
                isPositive
                  ? 'text-emerald-600'
                  : isNegative
                  ? 'text-red-600'
                  : 'text-slate-500'
              }`}
            >
              {isPositive && <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />}
              {isNegative && <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />}
              {!isPositive && !isNegative && <Minus className="w-3.5 h-3.5 mr-0.5" />}
              {Math.abs(card.change_pct)}%
            </span>
          )}
          {card.subtext && <span className="truncate">{card.subtext}</span>}
        </div>
      )}
    </div>
  );
};
