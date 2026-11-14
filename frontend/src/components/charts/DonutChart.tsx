import React, { useState, useMemo } from 'react';
import { formatCurrency, formatPercent } from '../../utils/formatters';
import { PieChart, AlertCircle } from 'lucide-react';

export interface DonutSegment {
  label: string;
  value: number;
  color?: string;
  subtext?: string;
}

interface DonutChartProps {
  data: DonutSegment[];
  title?: string;
  subtitle?: string;
  totalLabel?: string;
  currency?: boolean;
  loading?: boolean;
  error?: string | null;
  emptyMessage?: string;
}

const DEFAULT_PALETTE = [
  '#2563EB', // Brand blue
  '#16A34A', // Success green
  '#D97706', // Warning amber
  '#8B5CF6', // Purple
  '#0EA5E9', // Sky blue
  '#F43F5E', // Rose
  '#64748B', // Slate
];

export const DonutChart: React.FC<DonutChartProps> = ({
  data = [],
  title = 'Distribution Split',
  subtitle = 'Category & method share breakdown',
  totalLabel = 'Total',
  currency = true,
  loading = false,
  error = null,
  emptyMessage = 'No distribution data available yet',
}) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const totalValue = useMemo(() => {
    return data.reduce((acc, seg) => acc + (seg.value || 0), 0);
  }, [data]);

  const segments = useMemo(() => {
    if (totalValue === 0) return [];
    let accumulated = 0;
    return data.map((seg, idx) => {
      const share = seg.value / totalValue;
      const startAngle = accumulated * 2 * Math.PI;
      accumulated += share;
      const endAngle = accumulated * 2 * Math.PI;
      const color = seg.color || DEFAULT_PALETTE[idx % DEFAULT_PALETTE.length];
      return {
        ...seg,
        share,
        color,
        startAngle,
        endAngle,
      };
    });
  }, [data, totalValue]);

  if (loading) {
    return (
      <div className="bg-surface-card rounded-2xl border border-border p-5 sm:p-6 shadow-fintech animate-pulse space-y-4">
        <div className="h-4 w-32 bg-surface-muted rounded-md" />
        <div className="w-36 h-36 rounded-full bg-surface-muted mx-auto my-4" />
        <div className="space-y-2">
          <div className="h-3 w-full bg-surface-muted rounded-md" />
          <div className="h-3 w-3/4 bg-surface-muted rounded-md" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-surface-card rounded-2xl border border-danger/30 p-6 shadow-fintech text-center space-y-2">
        <AlertCircle className="w-7 h-7 text-danger mx-auto" />
        <h3 className="text-xs font-semibold text-text">Error loading breakdown</h3>
        <p className="text-[11px] text-text-muted">{error}</p>
      </div>
    );
  }

  const size = 180;
  const radius = 70;
  const strokeWidth = 24;
  const circumference = 2 * Math.PI * radius;

  // Active hover data
  const activeSeg = hoveredIdx !== null && segments[hoveredIdx] ? segments[hoveredIdx] : null;

  return (
    <div className="bg-surface-card rounded-2xl border border-border p-5 sm:p-6 shadow-fintech transition-all flex flex-col justify-between">
      <div>
        <h3 className="text-sm font-semibold text-text tracking-tight">{title}</h3>
        <p className="text-xs text-text-muted mt-0.5">{subtitle}</p>
      </div>

      {totalValue === 0 || segments.length === 0 ? (
        <div className="py-10 text-center flex flex-col items-center justify-center">
          <div className="w-10 h-10 rounded-xl bg-surface-muted text-text-muted flex items-center justify-center mb-2">
            <PieChart className="w-5 h-5 text-text-subtle" />
          </div>
          <p className="text-xs text-text-muted">{emptyMessage}</p>
        </div>
      ) : (
        <div className="my-4 flex flex-col sm:flex-row items-center justify-center gap-6">
          {/* SVG Donut */}
          <div className="relative shrink-0">
            <svg
              width={size}
              height={size}
              viewBox={`0 0 ${size} ${size}`}
              className="transform -rotate-90 select-none overflow-visible"
            >
              <circle
                cx={size / 2}
                cy={size / 2}
                r={radius}
                fill="transparent"
                stroke="rgb(var(--surface-muted))"
                strokeWidth={strokeWidth}
              />
              {(() => {
                let accumulatedOffset = 0;
                return segments.map((seg, idx) => {
                  const dashArray = seg.share * circumference;
                  const dashOffset = -accumulatedOffset;
                  accumulatedOffset += dashArray;
                  const isHovered = hoveredIdx === idx;

                  return (
                    <circle
                      key={seg.label}
                      cx={size / 2}
                      cy={size / 2}
                      r={radius}
                      fill="transparent"
                      stroke={seg.color}
                      strokeWidth={isHovered ? strokeWidth + 4 : strokeWidth}
                      strokeDasharray={`${dashArray} ${circumference}`}
                      strokeDashoffset={dashOffset}
                      className="cursor-pointer transition-all duration-150"
                      onMouseEnter={() => setHoveredIdx(idx)}
                      onMouseLeave={() => setHoveredIdx(null)}
                    />
                  );
                });
              })()}
            </svg>

            {/* Donut Center Display */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center">
              <span className="text-[10px] uppercase font-semibold text-text-muted tracking-wider">
                {activeSeg ? activeSeg.label : totalLabel}
              </span>
              <span className="text-base font-bold text-text tabular-nums leading-tight">
                {activeSeg
                  ? currency
                    ? formatCurrency(activeSeg.value, { compact: true })
                    : activeSeg.value
                  : currency
                  ? formatCurrency(totalValue, { compact: true })
                  : totalValue}
              </span>
              <span className="text-[10px] font-medium text-brand tabular-nums">
                {activeSeg ? formatPercent(activeSeg.share * 100) : '100%'}
              </span>
            </div>
          </div>

          {/* Legend Items */}
          <div className="w-full sm:w-auto flex-1 space-y-2 min-w-0">
            {segments.map((seg, idx) => {
              const isHovered = hoveredIdx === idx;
              return (
                <div
                  key={seg.label}
                  onMouseEnter={() => setHoveredIdx(idx)}
                  onMouseLeave={() => setHoveredIdx(null)}
                  className={`flex items-center justify-between gap-3 text-xs p-1.5 rounded-xl cursor-pointer transition-all ${
                    isHovered ? 'bg-surface-muted font-bold' : 'hover:bg-surface-muted/50'
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span
                      className="w-2.5 h-2.5 rounded-full shrink-0"
                      style={{ backgroundColor: seg.color }}
                    />
                    <span className="truncate text-text font-medium">{seg.label}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 tabular-nums text-right">
                    <span className="font-semibold text-text">
                      {currency ? formatCurrency(seg.value) : seg.value}
                    </span>
                    <span className="text-[11px] text-text-muted">
                      ({formatPercent(seg.share * 100)})
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
