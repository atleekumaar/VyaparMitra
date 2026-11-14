import React from 'react';
import { formatCurrency, formatNumber } from '../../utils/formatters';
import { BarChart3, AlertCircle } from 'lucide-react';

export interface BarItem {
  id: string;
  label: string;
  value: number;
  subtext?: string;
  category?: string;
  rank?: number;
}

interface HorizontalBarChartProps {
  data: BarItem[];
  title?: string;
  subtitle?: string;
  currency?: boolean;
  loading?: boolean;
  error?: string | null;
  emptyMessage?: string;
  maxItems?: number;
}

export const HorizontalBarChart: React.FC<HorizontalBarChartProps> = ({
  data = [],
  title = 'Top Performing SKUs',
  subtitle = 'Ranked by revenue generation',
  currency = true,
  loading = false,
  error = null,
  emptyMessage = 'No sales recorded for any products yet',
  maxItems = 5,
}) => {
  if (loading) {
    return (
      <div className="bg-surface-card rounded-2xl border border-border p-5 sm:p-6 shadow-fintech animate-pulse space-y-4">
        <div className="h-4 w-32 bg-surface-muted rounded-md" />
        <div className="space-y-3 pt-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="space-y-1.5">
              <div className="flex justify-between">
                <div className="h-3 w-28 bg-surface-muted rounded" />
                <div className="h-3 w-16 bg-surface-muted rounded" />
              </div>
              <div className="h-2 w-full bg-surface-muted rounded-full" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-surface-card rounded-2xl border border-danger/30 p-6 shadow-fintech text-center space-y-2">
        <AlertCircle className="w-7 h-7 text-danger mx-auto" />
        <h3 className="text-xs font-semibold text-text">Error loading rankings</h3>
        <p className="text-[11px] text-text-muted">{error}</p>
      </div>
    );
  }

  const items = data.slice(0, maxItems);
  const maxValue = Math.max(...items.map((i) => i.value), 1);
  const hasData = items.length > 0 && items.some((i) => i.value > 0);

  return (
    <div className="bg-surface-card rounded-2xl border border-border p-5 sm:p-6 shadow-fintech transition-all flex flex-col justify-between">
      <div>
        <h3 className="text-sm font-semibold text-text tracking-tight">{title}</h3>
        <p className="text-xs text-text-muted mt-0.5">{subtitle}</p>
      </div>

      {!hasData ? (
        <div className="py-10 text-center flex flex-col items-center justify-center">
          <div className="w-10 h-10 rounded-xl bg-surface-muted text-text-muted flex items-center justify-center mb-2">
            <BarChart3 className="w-5 h-5 text-text-subtle" />
          </div>
          <p className="text-xs text-text-muted">{emptyMessage}</p>
        </div>
      ) : (
        <div className="space-y-3.5 my-3 pt-1">
          {items.map((item, idx) => {
            const pct = Math.min(Math.round((item.value / maxValue) * 100), 100);
            return (
              <div key={item.id || idx} className="space-y-1.5 group">
                <div className="flex items-center justify-between text-xs gap-3">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="w-4 text-[11px] font-bold text-text-subtle text-right shrink-0">
                      #{idx + 1}
                    </span>
                    <span className="font-semibold text-text truncate group-hover:text-brand transition-colors">
                      {item.label}
                    </span>
                    {item.category && (
                      <span className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] rounded-md bg-surface-muted text-text-muted border border-border/60 shrink-0">
                        {item.category}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 shrink-0 tabular-nums">
                    {item.subtext && (
                      <span className="text-[11px] text-text-muted font-normal">
                        {item.subtext}
                      </span>
                    )}
                    <span className="font-bold text-text">
                      {currency ? formatCurrency(item.value) : formatNumber(item.value)}
                    </span>
                  </div>
                </div>

                {/* Progress track & bar */}
                <div className="h-2 w-full bg-surface-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-brand rounded-full transition-all duration-300 group-hover:bg-brand-hover"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
