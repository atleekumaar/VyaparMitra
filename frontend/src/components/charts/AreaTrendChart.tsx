import React, { useState, useId, useMemo } from 'react';
import { formatCompactINR, formatCurrency, formatDate } from '../../utils/formatters';
import { TrendingUp, AlertCircle, PlusCircle } from 'lucide-react';
import { Button } from '../Button';

export interface TrendDataPoint {
  date: string;
  revenue: number;
  orders?: number;
  label?: string;
}

interface AreaTrendChartProps {
  data: TrendDataPoint[];
  title?: string;
  subtitle?: string;
  range?: '7D' | '30D' | '90D';
  onRangeChange?: (range: '7D' | '30D' | '90D') => void;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  onEmptyAction?: () => void;
  emptyActionLabel?: string;
  height?: number;
}

export const AreaTrendChart: React.FC<AreaTrendChartProps> = ({
  data = [],
  title = 'Revenue Trend',
  subtitle = 'Daily sales movement & volume',
  range = '7D',
  onRangeChange,
  loading = false,
  error = null,
  onRetry,
  onEmptyAction,
  emptyActionLabel = 'Record First Sale',
  height = 240,
}) => {
  const gradientId = useId();
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  // Compute domain & filtered points
  const points = useMemo(() => {
    if (!data || data.length === 0) return [];
    const sliceCount = range === '7D' ? 7 : range === '30D' ? 30 : 90;
    return data.slice(-sliceCount);
  }, [data, range]);

  const hasData = points.length > 0 && points.some((p) => p.revenue > 0);

  const { maxVal, minVal, svgPoints, areaPath, linePath } = useMemo(() => {
    if (!hasData) {
      return { maxVal: 0, minVal: 0, svgPoints: [], areaPath: '', linePath: '' };
    }

    const revenues = points.map((p) => p.revenue);
    const max = Math.max(...revenues, 100);
    const min = 0; // Baseline at 0 for financial revenue charts
    const rangeVal = max - min || 1;

    const width = 600;
    const chartHeight = height - 40; // reserve space for bottom labels
    const paddingTop = 20;

    const pts = points.map((p, idx) => {
      const x = (idx / Math.max(points.length - 1, 1)) * (width - 40) + 20;
      const y = paddingTop + chartHeight - ((p.revenue - min) / rangeVal) * chartHeight;
      return { x, y, point: p };
    });

    const linePointsStr = pts.map((pt) => `${pt.x.toFixed(1)},${pt.y.toFixed(1)}`).join(' L ');
    const line = `M ${linePointsStr}`;
    const area = `${line} L ${pts[pts.length - 1].x.toFixed(1)},${paddingTop + chartHeight} L ${pts[0].x.toFixed(1)},${paddingTop + chartHeight} Z`;

    return {
      maxVal: max,
      minVal: min,
      svgPoints: pts,
      areaPath: area,
      linePath: line,
    };
  }, [points, hasData, height]);

  // Loading skeleton state
  if (loading) {
    return (
      <div className="bg-surface-card rounded-2xl border border-border p-5 sm:p-6 shadow-fintech animate-pulse space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-4 w-32 bg-surface-muted rounded-md" />
            <div className="h-3 w-48 bg-surface-muted rounded-md" />
          </div>
          <div className="h-7 w-28 bg-surface-muted rounded-lg" />
        </div>
        <div className="h-48 w-full bg-surface-muted rounded-xl mt-4" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-surface-card rounded-2xl border border-danger/30 p-6 shadow-fintech text-center space-y-3">
        <AlertCircle className="w-8 h-8 text-danger mx-auto" />
        <h3 className="text-sm font-semibold text-text">Failed to load revenue trend</h3>
        <p className="text-xs text-text-muted max-w-sm mx-auto">{error}</p>
        {onRetry && (
          <Button variant="secondary" size="sm" onClick={onRetry} className="mt-2">
            Retry
          </Button>
        )}
      </div>
    );
  }

  // Active hovered point
  const activePt = hoveredIndex !== null && svgPoints[hoveredIndex] ? svgPoints[hoveredIndex] : null;

  return (
    <div className="bg-surface-card rounded-2xl border border-border p-5 sm:p-6 shadow-fintech transition-all">
      {/* Chart Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border/60">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-text tracking-tight">{title}</h3>
            {hasData && (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-success bg-success-soft px-2 py-0.5 rounded-full">
                <TrendingUp className="w-3 h-3" />
                Live Revenue
              </span>
            )}
          </div>
          <p className="text-xs text-text-muted mt-0.5">{subtitle}</p>
        </div>

        {/* Range Selector */}
        {onRangeChange && (
          <div className="flex items-center bg-surface-muted p-1 rounded-xl border border-border text-xs font-semibold self-start sm:self-auto">
            {(['7D', '30D', '90D'] as const).map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => onRangeChange(r)}
                className={`px-3 py-1 rounded-lg transition-all ${
                  range === r
                    ? 'bg-surface-card text-brand shadow-xs font-bold'
                    : 'text-text-muted hover:text-text'
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Chart Body */}
      {!hasData ? (
        // Empty State: Friendly fintech prompt
        <div className="py-12 px-4 text-center flex flex-col items-center justify-center">
          <div className="w-12 h-12 rounded-2xl bg-brand-soft text-brand flex items-center justify-center mb-3">
            <TrendingUp className="w-6 h-6" />
          </div>
          <h4 className="text-sm font-semibold text-text">Abhi koi sale nahi hui hai</h4>
          <p className="text-xs text-text-muted mt-1 max-w-xs leading-relaxed">
            Pehli transaction add karte hi yahan daily revenue trend aur automated forecasts live dikhenge.
          </p>
          {onEmptyAction && (
            <Button
              variant="primary"
              size="sm"
              onClick={onEmptyAction}
              className="mt-4 gap-1.5"
            >
              <PlusCircle className="w-4 h-4" />
              {emptyActionLabel}
            </Button>
          )}
        </div>
      ) : (
        <div className="relative mt-4">
          {/* Active tooltip badge */}
          {activePt && (
            <div
              className="absolute -top-1 bg-surface-elevated text-text border border-border-strong px-2.5 py-1.5 rounded-xl shadow-fintech-md text-xs pointer-events-none z-10 transition-all transform -translate-x-1/2"
              style={{ left: `${(activePt.x / 600) * 100}%` }}
            >
              <div className="font-bold text-text tabular-nums">
                {formatCurrency(activePt.point.revenue)}
              </div>
              <div className="text-[10px] text-text-muted flex items-center gap-1.5">
                <span>{formatDate(activePt.point.date)}</span>
                {typeof activePt.point.orders === 'number' && (
                  <span>&bull; {activePt.point.orders} orders</span>
                )}
              </div>
            </div>
          )}

          {/* SVG Area & Crosshair */}
          <div className="w-full overflow-hidden">
            <svg
              viewBox="0 0 600 240"
              className="w-full h-auto overflow-visible select-none"
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <defs>
                <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="rgb(var(--brand))" stopOpacity="0.28" />
                  <stop offset="90%" stopColor="rgb(var(--brand))" stopOpacity="0.02" />
                  <stop offset="100%" stopColor="rgb(var(--brand))" stopOpacity="0" />
                </linearGradient>
              </defs>

              {/* Grid Lines */}
              <line x1="20" y1="20" x2="580" y2="20" stroke="rgb(var(--border-subtle))" strokeDasharray="3 3" />
              <line x1="20" y1="110" x2="580" y2="110" stroke="rgb(var(--border-subtle))" strokeDasharray="3 3" />
              <line x1="20" y1="200" x2="580" y2="200" stroke="rgb(var(--border))" />

              {/* Y Axis Reference Labels */}
              <text x="18" y="24" textAnchor="end" className="text-[9px] fill-text-subtle font-mono">
                {formatCompactINR(maxVal)}
              </text>
              <text x="18" y="114" textAnchor="end" className="text-[9px] fill-text-subtle font-mono">
                {formatCompactINR(maxVal / 2)}
              </text>
              <text x="18" y="204" textAnchor="end" className="text-[9px] fill-text-subtle font-mono">
                ₹0
              </text>

              {/* Filled Area */}
              <path d={areaPath} fill={`url(#${gradientId})`} />

              {/* Stroke Line */}
              <path
                d={linePath}
                fill="none"
                stroke="rgb(var(--brand))"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {/* Interactive Crosshair & Points */}
              {svgPoints.map((pt, idx) => (
                <g key={pt.point.date || idx}>
                  {/* Invisible hit target for smooth hover on mobile & desktop */}
                  <rect
                    x={pt.x - 18}
                    y="0"
                    width="36"
                    height="210"
                    fill="transparent"
                    className="cursor-pointer"
                    onMouseEnter={() => setHoveredIndex(idx)}
                    onClick={() => setHoveredIndex(idx)}
                  />

                  {hoveredIndex === idx && (
                    <>
                      {/* Vertical Crosshair */}
                      <line
                        x1={pt.x}
                        y1="15"
                        x2={pt.x}
                        y2="200"
                        stroke="rgb(var(--brand))"
                        strokeWidth="1.25"
                        strokeDasharray="3 3"
                      />
                      {/* Outer pulse circle */}
                      <circle
                        cx={pt.x}
                        cy={pt.y}
                        r="6"
                        fill="rgb(var(--brand))"
                        fillOpacity="0.25"
                      />
                      {/* Center dot */}
                      <circle
                        cx={pt.x}
                        cy={pt.y}
                        r="3.5"
                        fill="rgb(var(--brand))"
                        stroke="rgb(var(--surface-card))"
                        strokeWidth="2"
                      />
                    </>
                  )}
                </g>
              ))}

              {/* Bottom Date Labels */}
              {svgPoints.map((pt, idx) => {
                // Show a clean sample of dates so labels don't collide
                const step = points.length > 10 ? Math.ceil(points.length / 5) : 1;
                if (idx % step !== 0 && idx !== points.length - 1) return null;
                const label = formatDate(pt.point.date);
                return (
                  <text
                    key={`lbl-${idx}`}
                    x={pt.x}
                    y="222"
                    textAnchor="middle"
                    className="text-[10px] fill-text-muted font-medium tabular-nums"
                  >
                    {label}
                  </text>
                );
              })}
            </svg>
          </div>
        </div>
      )}
    </div>
  );
};
