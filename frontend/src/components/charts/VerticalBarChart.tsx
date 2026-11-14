import React, { useState } from 'react';
import { formatCurrency, formatNumber } from '../../utils/formatters';
import { BarChart2, AlertCircle } from 'lucide-react';

export interface VerticalBarPoint {
  label: string;
  value: number;
  subtext?: string;
  tooltip?: string;
}

interface VerticalBarChartProps {
  data: VerticalBarPoint[];
  title?: string;
  subtitle?: string;
  currency?: boolean;
  height?: number;
  loading?: boolean;
  error?: string | null;
  emptyMessage?: string;
}

export const VerticalBarChart: React.FC<VerticalBarChartProps> = ({
  data = [],
  title,
  subtitle,
  currency = true,
  height = 240,
  loading = false,
  error = null,
  emptyMessage = 'No sales series data available',
}) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  if (loading) {
    return (
      <div className="w-full flex flex-col justify-between animate-pulse space-y-4" style={{ height }}>
        {title && (
          <div>
            <div className="h-4 w-36 bg-surface-muted rounded-md" />
            {subtitle && <div className="h-3 w-48 bg-surface-muted rounded-md mt-1" />}
          </div>
        )}
        <div className="flex-1 flex items-end justify-between gap-2 px-2 pb-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="flex-1 bg-surface-muted rounded-t-xl"
              style={{ height: `${20 + ((i * 17) % 75)}%` }}
            />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full flex flex-col items-center justify-center p-6 text-center space-y-2" style={{ height }}>
        <AlertCircle className="w-6 h-6 text-danger" />
        <p className="text-xs font-semibold text-text">Error loading chart</p>
        <p className="text-[11px] text-text-muted">{error}</p>
      </div>
    );
  }

  const maxValue = Math.max(...data.map((d) => d.value), 1);
  const hasData = data.length > 0 && data.some((d) => d.value > 0);

  if (!hasData) {
    return (
      <div className="w-full flex flex-col items-center justify-center p-6 text-center space-y-2" style={{ height }}>
        <div className="w-10 h-10 rounded-xl bg-surface-muted text-text-muted flex items-center justify-center mb-1">
          <BarChart2 className="w-5 h-5 text-text-subtle" />
        </div>
        <p className="text-xs text-text-muted">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="w-full flex flex-col justify-between" style={{ minHeight: height }}>
      {title && (
        <div className="mb-4">
          <h4 className="text-sm font-bold text-text tracking-tight">{title}</h4>
          {subtitle && <p className="text-xs text-text-muted mt-0.5">{subtitle}</p>}
        </div>
      )}

      {/* Chart Canvas Area */}
      <div className="relative flex-1 flex items-end justify-between gap-2 sm:gap-3 pt-6 pb-2 px-1">
        {data.map((item, idx) => {
          const heightPct = Math.max(Math.round((item.value / maxValue) * 100), item.value > 0 ? 6 : 2);
          const isHovered = hoveredIndex === idx;

          return (
            <div
              key={idx}
              className="relative flex-1 flex flex-col items-center group h-full justify-end cursor-pointer"
              onMouseEnter={() => setHoveredIndex(idx)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {/* Tooltip on Hover */}
              {isHovered && (
                <div className="absolute -top-10 z-20 px-2.5 py-1 rounded-lg bg-slate-900 text-white text-[11px] font-semibold whitespace-nowrap shadow-lg animate-in fade-in-50 zoom-in-95 pointer-events-none">
                  <div className="text-center">
                    <span className="text-blue-300 font-bold">
                      {currency ? formatCurrency(item.value) : formatNumber(item.value)}
                    </span>
                    {item.subtext && <span className="text-[10px] text-slate-400 block">{item.subtext}</span>}
                  </div>
                  {/* Tooltip arrow */}
                  <div className="w-2 h-2 bg-slate-900 rotate-45 mx-auto -mb-1 mt-0.5" />
                </div>
              )}

              {/* Column Bar with Gradient & Smooth Top Rounded Corners */}
              <div
                className={`w-full max-w-[42px] rounded-t-xl sm:rounded-t-2xl transition-all duration-300 ease-out ${
                  isHovered
                    ? 'bg-gradient-to-t from-blue-700 to-sky-400 shadow-md scale-y-105'
                    : 'bg-gradient-to-t from-blue-600 via-blue-500 to-sky-400 dark:from-blue-700 dark:via-blue-600 dark:to-sky-500 opacity-90 group-hover:opacity-100'
                }`}
                style={{ height: `${heightPct}%` }}
              />

              {/* X-Axis Label */}
              <div className="mt-2 text-[10px] font-semibold text-text-muted truncate max-w-full text-center group-hover:text-text transition-colors">
                {item.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

