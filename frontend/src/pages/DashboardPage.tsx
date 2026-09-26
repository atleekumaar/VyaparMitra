import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  Sparkles,
  Bot,
  AlertTriangle,
  ArrowRight,
  ShoppingBag,
  DollarSign,
  Users,
  Package,
  Calendar,
  CheckCircle2,
  Trophy,
} from 'lucide-react';
import { api } from '../api/client';
import { ActionItem, BenchmarkData, DashboardSummary, SalesAnalytics } from '../types';
import { MetricCard } from '../components/MetricCard';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { CardSkeleton, ChartSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner } from '../components/EmptyState';

interface DashboardPageProps {
  onNavigateTab: (tab: any) => void;
  onSelectAction: (actionId: string) => void;
  onQuickCopilot: (query: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigateTab,
  onSelectAction,
  onQuickCopilot,
}) => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [actions, setActions] = useState<ActionItem[]>([]);
  const [salesAnalytics, setSalesAnalytics] = useState<SalesAnalytics | null>(null);
  const [benchmark, setBenchmark] = useState<BenchmarkData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [quickQuery, setQuickQuery] = useState<string>('');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, actRes, salesRes] = await Promise.all([
        api.getDashboardSummary(),
        api.getDashboardActions(5),
        api.getSalesAnalytics(),
      ]);
      setSummary(sumRes);
      setActions(actRes.actions || []);
      setSalesAnalytics(salesRes);

      try {
        const benchRes = await api.getMerchantBenchmark(sumRes.merchant_id || 'M015');
        setBenchmark(benchRes);
      } catch {
        // Fallback silently if benchmark not yet computed
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleQuickAsk = (e: React.FormEvent) => {
    e.preventDefault();
    if (quickQuery.trim()) {
      onQuickCopilot(quickQuery.trim());
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ChartSkeleton />
          </div>
          <div>
            <CardSkeleton />
          </div>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="space-y-4">
        <ErrorBanner message={error || 'Could not load dashboard.'} onRetry={loadData} />
      </div>
    );
  }

  // Slice last 14 days of sales for chart
  const recentDays = salesAnalytics?.daily_series?.slice(-14) || [];
  const maxRev = Math.max(...recentDays.map((d) => d.revenue), 1000);

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      {/* Welcome Banner */}
      <div className="bg-white rounded-2xl border border-paytm-border p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-paytm-dark">
              Good Morning, Merchant 👋
            </h2>
            <Badge variant="demo">Synthetic Store Data</Badge>
          </div>
          <p className="text-xs text-paytm-muted mt-1 max-w-xl">
            Here is your daily commercial overview. All metrics are verified against Phase 1-4
            artifacts and ML models.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onQuickCopilot('Mujhe aaj ka poora business brief batao')}
            className="text-xs"
          >
            <Sparkles className="w-3.5 h-3.5 mr-1.5 text-paytm-blue" />
            Today's Brief
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => onNavigateTab('recommendations')}
            className="text-xs"
          >
            <span>{summary.total_actions_pending} Priority Actions</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          card={summary.kpis.revenue}
          icon={<DollarSign className="w-4 h-4" />}
        />
        <MetricCard
          card={summary.kpis.orders}
          icon={<ShoppingBag className="w-4 h-4" />}
        />
        <MetricCard
          card={summary.kpis.aov}
          icon={<TrendingUp className="w-4 h-4" />}
        />
        <MetricCard
          card={summary.kpis.units}
          icon={<Package className="w-4 h-4" />}
        />
      </div>

      {/* Main Grid: Left Charts + Right Action Center */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Sales Trends & Forecast */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Sales History Chart */}
          <div className="bg-white rounded-2xl border border-paytm-border p-6 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-paytm-dark">Daily Sales Trend</h3>
                <p className="text-xs text-paytm-muted">Last 14 recorded business days</p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="info">
                  Trend: {summary.sales_trend_direction}
                </Badge>
              </div>
            </div>

            {/* Custom Bar Visualization */}
            <div className="h-52 flex items-end justify-between gap-1.5 pt-6 pb-2 border-b border-slate-100">
              {recentDays.map((day, idx) => {
                const heightPct = Math.max(10, (day.revenue / maxRev) * 100);
                return (
                  <div
                    key={idx}
                    className="flex-1 flex flex-col items-center group relative h-full justify-end"
                  >
                    {/* Tooltip on hover */}
                    <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 text-white text-[10px] rounded px-2 py-1 pointer-events-none whitespace-nowrap z-20 shadow-md">
                      {day.date}: ₹{day.revenue.toLocaleString()} ({day.orders} orders)
                    </div>
                    {/* Bar */}
                    <div
                      className="w-full bg-paytm-light border border-paytm-border hover:bg-paytm-blue hover:border-paytm-blue rounded-t transition-all duration-150 cursor-pointer"
                      style={{ height: `${heightPct}%` }}
                    />
                    {/* Date label */}
                    <span className="text-[9px] text-slate-400 mt-2 truncate w-full text-center">
                      {day.date.split('-').slice(1).join('/')}
                    </span>
                  </div>
                );
              })}
            </div>
            <div className="mt-3 flex items-center justify-between text-xs text-paytm-muted">
              <span>Peak Day: ₹{maxRev.toLocaleString()}</span>
              <button
                onClick={() => onNavigateTab('analytics')}
                className="text-paytm-blue hover:underline font-medium inline-flex items-center gap-1"
              >
                Deep Analytics <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          </div>

          {/* 7-Day Forward Forecast Banner */}
          <div className="bg-gradient-to-r from-paytm-dark to-slate-900 text-white rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-semibold text-paytm-blue uppercase tracking-wider">
                <TrendingUp className="w-4 h-4" />
                <span>Phase 3 Predictive AI &bull; 7-Day Forecast</span>
              </div>
              <p className="text-2xl font-bold mt-1 text-white">
                ₹{summary.forecast_7d_total_revenue.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-slate-300 mt-1 max-w-md">
                Expected store revenue over the upcoming 7 days based on autoregressive demand patterns.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigateTab('forecasts')}
              className="border-paytm-blue text-white hover:bg-paytm-blue/20 shrink-0"
            >
              View SKU Forecasts
            </Button>
          </div>
        </div>

        {/* Right 1 Col: Priority Action Center & Quick Ask */}
        <div className="space-y-6">
          {/* Peer Benchmarking Summary Card */}
          {benchmark && (
            <div className="bg-white rounded-2xl border border-paytm-border p-5 shadow-xs relative overflow-hidden">
              <div className="flex items-center justify-between pb-3 border-b border-paytm-border">
                <div className="flex items-center gap-2">
                  <div className="p-1 rounded-md bg-paytm-light text-paytm-blue border border-paytm-border">
                    <Trophy className="w-4 h-4 text-paytm-blue" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-paytm-dark">Peers se tulna</h3>
                    <p className="text-[10px] text-paytm-muted font-medium">{benchmark.peer_group}</p>
                  </div>
                </div>
                <Badge
                  variant={
                    benchmark.rank <= Math.ceil(benchmark.peer_count * 0.33)
                      ? 'success'
                      : benchmark.rank <= Math.ceil(benchmark.peer_count * 0.66)
                      ? 'high'
                      : 'critical'
                  }
                  className="text-xs"
                >
                  Rank {benchmark.rank} of {benchmark.peer_count}
                </Badge>
              </div>

              {/* Metrics Highlights Table */}
              <div className="py-3 space-y-2 text-xs">
                {benchmark.metrics.slice(0, 3).map((m) => (
                  <div
                    key={m.name}
                    className="flex items-center justify-between py-1 border-b border-slate-50 last:border-none"
                  >
                    <span className="text-slate-600 font-medium">{m.label}</span>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-paytm-dark">
                        {m.unit === '₹' ? `₹${Math.round(m.you)}` : `${m.you}${m.unit}`}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        vs {m.unit === '₹' ? `₹${Math.round(m.peer_median)}` : `${m.peer_median}${m.unit}`}
                      </span>
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                          m.status === 'green'
                            ? 'bg-emerald-100 text-emerald-800'
                            : m.status === 'yellow'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {m.status_text}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Top Action Recommendation */}
              <div className="mt-1 p-2.5 rounded-lg bg-paytm-light/70 border border-paytm-border text-xs">
                <span className="font-semibold text-paytm-dark block text-[11px]">Recommended Action:</span>
                <p className="text-[11px] text-slate-600 mt-0.5 line-clamp-2">
                  {benchmark.metrics.find((m) => m.status === 'red' || m.status === 'yellow')?.action ||
                    benchmark.metrics[0]?.action}
                </p>
              </div>

              {/* Card Bottom CTA Buttons */}
              <div className="mt-3 flex items-center justify-between pt-2 border-t border-paytm-border text-xs">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onNavigateTab('recommendations')}
                  className="text-xs py-1 px-2.5 text-paytm-dark"
                >
                  Offer bhejein
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => onNavigateTab('compare')}
                  className="text-xs py-1 px-3 flex items-center gap-1"
                >
                  <span>Details dekhein</span>
                  <ArrowRight className="w-3 h-3" />
                </Button>
              </div>
            </div>
          )}

          {/* Priority Actions Card */}
          <div className="bg-white rounded-2xl border border-paytm-border p-5 shadow-xs">
            <div className="flex items-center justify-between pb-3 border-b border-paytm-border">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-paytm-blue" />
                <h3 className="text-sm font-bold text-paytm-dark">Priority Actions</h3>
              </div>
              <Badge variant="critical">
                {summary.critical_actions_count} Critical
              </Badge>
            </div>

            <div className="divide-y divide-slate-100 mt-2">
              {actions.map((act) => (
                <div
                  key={act.recommendation_id}
                  className="py-3 hover:bg-slate-50/80 rounded-lg p-2 transition-colors cursor-pointer"
                  onClick={() => onSelectAction(act.recommendation_id)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-bold text-paytm-dark line-clamp-1">
                      {act.title}
                    </span>
                    <Badge
                      variant={
                        act.priority_band === 'CRITICAL'
                          ? 'critical'
                          : act.priority_band === 'HIGH'
                          ? 'high'
                          : 'medium'
                      }
                    >
                      {act.priority_band}
                    </Badge>
                  </div>
                  <p className="text-[11px] text-paytm-muted mt-1 line-clamp-2">
                    {act.action}
                  </p>
                  <div className="mt-2 flex items-center justify-between text-[11px]">
                    <span className="font-semibold text-emerald-700">
                      Impact: ₹{act.expected_impact.toLocaleString()}
                    </span>
                    <span className="text-paytm-blue hover:underline font-medium">
                      Review &rarr;
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-3 pt-3 border-t border-slate-100">
              <Button
                variant="secondary"
                size="sm"
                className="w-full text-xs"
                onClick={() => onNavigateTab('recommendations')}
              >
                Open Action Center ({summary.total_actions_pending})
              </Button>
            </div>
          </div>

          {/* Quick Copilot Interactive Card */}
          <div className="bg-paytm-light rounded-2xl border border-paytm-border p-5 shadow-xs">
            <div className="flex items-center gap-2 text-xs font-bold text-paytm-dark">
              <Bot className="w-4 h-4 text-paytm-blue" />
              <span>Ask VyaparMitra Copilot</span>
            </div>
            <p className="text-[11px] text-paytm-muted mt-1">
              Ask questions about sales, forecast, stockouts, or Graahak in Hindi, Hinglish, or English.
            </p>

            <form onSubmit={handleQuickAsk} className="mt-3 space-y-2">
              <input
                type="text"
                value={quickQuery}
                onChange={(e) => setQuickQuery(e.target.value)}
                placeholder="e.g. Kal kitni bikri hui thi?"
                className="w-full px-3 py-2 text-xs rounded-lg border border-paytm-border bg-white focus:outline-none focus:ring-2 focus:ring-paytm-blue"
              />
              <Button type="submit" variant="primary" size="sm" className="w-full text-xs">
                Ask Copilot
              </Button>
            </form>

            <div className="mt-3 flex flex-wrap gap-1">
              {[
                'Agle hafte sales kitni hogi?',
                'Kaunsa maal restock karein?',
                'High-risk customers kaun hain?',
              ].map((q, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => onQuickCopilot(q)}
                  className="text-[10px] bg-white border border-paytm-border text-paytm-muted hover:text-paytm-blue hover:border-paytm-blue rounded-md px-2 py-1 transition-colors text-left"
                >
                  &ldquo;{q}&rdquo;
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
