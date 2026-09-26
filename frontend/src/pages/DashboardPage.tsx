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
  Volume2,
  ShieldCheck,
  Zap,
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
  const [soundboxPlayed, setSoundboxPlayed] = useState<boolean>(false);

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

  const handleTestSoundbox = () => {
    setSoundboxPlayed(true);
    setTimeout(() => setSoundboxPlayed(false), 3000);
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
      {/* Paytm Soundbox 4.0 Live Notification Banner */}
      <div className="bg-gradient-to-r from-[#002970] via-[#00388F] to-[#001D4E] text-white rounded-2xl p-4 shadow-soundbox border border-[#00BAF2]/30 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-3.5 w-full sm:w-auto">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00BAF2] to-[#008CC4] flex items-center justify-center text-white shrink-0 shadow-md shadow-[#00BAF2]/30 ring-2 ring-white/20">
            <Volume2 className={`w-5 h-5 ${soundboxPlayed ? 'animate-bounce text-white' : 'text-white'}`} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black tracking-wider uppercase text-[#00BAF2]">
                Paytm Soundbox 4.0 Live
              </span>
              <span className="px-1.5 py-0.2 rounded-full text-[9px] font-bold bg-[#00B970] text-white">
                Audio Active
              </span>
            </div>
            <p className="text-sm font-bold text-white mt-0.5">
              {soundboxPlayed
                ? '🔊 "Paytm par ₹4,250 prapt hue!"'
                : '🔊 "Paytm par ₹4,250 prapt hue" • Aaj ka Total Collection: ₹45,280 (128 transactions)'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
          <button
            onClick={handleTestSoundbox}
            className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold border border-white/20 transition-all flex items-center gap-1.5"
          >
            <Zap className="w-3.5 h-3.5 text-[#00BAF2]" />
            <span>Test Audio</span>
          </button>
          <span className="text-xs text-blue-200 font-medium hidden md:inline">
            100% Instant Bank Settlement
          </span>
        </div>
      </div>

      {/* Welcome Banner */}
      <div className="bg-white rounded-2xl border border-[#CDE5F7] p-6 shadow-paytm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-xl lg:text-2xl font-black text-[#002970] tracking-tight">
              Shubh Prabhat, Merchant Ji 👋
            </h2>
            <Badge variant="demo">Paytm Verified Store</Badge>
          </div>
          <p className="text-xs text-[#4F6A94] mt-1 max-w-xl font-medium">
            Aapki dukaan ka poora commercial brief tayar hai. Sabhi metrics Phase 1-4 Feature Store aur ML models se verified hain.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onQuickCopilot('Mujhe aaj ka poora business brief batao')}
            className="text-xs font-bold"
          >
            <Sparkles className="w-3.5 h-3.5 mr-1.5 text-[#00BAF2]" />
            Today's Brief
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => onNavigateTab('recommendations')}
            className="text-xs font-bold"
          >
            <span>{summary.total_actions_pending} Priority Actions</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Button>
        </div>
      </div>

      {/* KPI Cards Grid with Paytm Accents */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          card={summary.kpis.revenue}
          icon={<DollarSign className="w-5 h-5" />}
          accentColor="cyan"
        />
        <MetricCard
          card={summary.kpis.orders}
          icon={<ShoppingBag className="w-5 h-5" />}
          accentColor="navy"
        />
        <MetricCard
          card={summary.kpis.aov}
          icon={<TrendingUp className="w-5 h-5" />}
          accentColor="green"
        />
        <MetricCard
          card={summary.kpis.units}
          icon={<Package className="w-5 h-5" />}
          accentColor="orange"
        />
      </div>

      {/* Main Grid: Left Charts + Right Action Center */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Sales Trends & Forecast */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Sales History Chart */}
          <div className="bg-white rounded-2xl border border-[#CDE5F7] p-6 shadow-paytm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-extrabold text-[#002970]">Daily Sales Trend (Bikri)</h3>
                <p className="text-xs text-[#4F6A94] font-medium">Last 14 recorded business days</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-[#E8F8F0] text-[#008A54] border border-[#B6E8D0]">
                  Trend: {summary.sales_trend_direction}
                </span>
              </div>
            </div>

            {/* Custom Bar Visualization */}
            <div className="h-56 flex items-end justify-between gap-1.5 pt-6 pb-2 border-b border-[#E8F4FD]">
              {recentDays.map((day, idx) => {
                const heightPct = Math.max(10, (day.revenue / maxRev) * 100);
                return (
                  <div
                    key={idx}
                    className="flex-1 flex flex-col items-center group relative h-full justify-end"
                  >
                    {/* Tooltip on hover */}
                    <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-[#002970] text-white text-[10px] font-bold rounded-lg px-2.5 py-1.5 pointer-events-none whitespace-nowrap z-20 shadow-lg border border-[#00BAF2]/40">
                      {day.date}: ₹{day.revenue.toLocaleString()} ({day.orders} orders)
                    </div>
                    {/* Bar */}
                    <div
                      className="w-full bg-gradient-to-t from-[#00BAF2] to-[#41C9F7] hover:from-[#002970] hover:to-[#001D4E] rounded-t-lg transition-all duration-150 cursor-pointer shadow-2xs"
                      style={{ height: `${heightPct}%` }}
                    />
                    {/* Date label */}
                    <span className="text-[10px] text-[#4F6A94] font-semibold mt-2 truncate w-full text-center">
                      {day.date.split('-').slice(1).join('/')}
                    </span>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 flex items-center justify-between text-xs text-[#4F6A94]">
              <span className="font-semibold">
                Peak Day Collection:{' '}
                <strong className="text-[#002970] font-extrabold">₹{maxRev.toLocaleString()}</strong>
              </span>
              <button
                onClick={() => onNavigateTab('analytics')}
                className="text-[#00BAF2] hover:text-[#002970] font-bold inline-flex items-center gap-1 transition-colors"
              >
                Deep Analytics <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* 7-Day Forward Forecast Banner with Paytm Royalty */}
          <div className="bg-gradient-to-r from-[#002970] via-[#00388F] to-[#001D4E] text-white rounded-2xl p-6 shadow-soundbox border border-[#00BAF2]/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-black text-[#00BAF2] uppercase tracking-wider">
                <TrendingUp className="w-4 h-4 text-[#00BAF2]" />
                <span>Phase 3 Predictive AI &bull; 7-Day Forecast</span>
              </div>
              <p className="text-3xl font-black mt-1 text-white tracking-tight">
                ₹{summary.forecast_7d_total_revenue.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-blue-100 mt-1 max-w-md font-medium">
                Autoregressive ML models ke anusaar agle 7 dino me anumanit store revenue.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigateTab('forecasts')}
              className="border-white/40 text-white hover:bg-white/10 shrink-0 font-bold"
            >
              View SKU Forecasts
            </Button>
          </div>
        </div>

        {/* Right 1 Col: Priority Action Center & Quick Ask */}
        <div className="space-y-6">
          {/* Peer Benchmarking Summary Card */}
          {benchmark && (
            <div className="bg-white rounded-2xl border-2 border-[#CDE5F7] p-5 shadow-paytm relative overflow-hidden">
              <div className="flex items-center justify-between pb-3 border-b border-[#E8F4FD]">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-gradient-to-br from-[#E0F4FD] to-[#C9EDFC] text-[#00BAF2] border border-[#B3E3FA]">
                    <Trophy className="w-4 h-4 text-[#00BAF2]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-extrabold text-[#002970]">Peers se tulna</h3>
                    <p className="text-[10px] text-[#4F6A94] font-semibold">{benchmark.peer_group}</p>
                  </div>
                </div>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-extrabold ${
                    benchmark.rank <= Math.ceil(benchmark.peer_count * 0.33)
                      ? 'bg-[#E8F8F0] text-[#008A54] border border-[#B6E8D0]'
                      : benchmark.rank <= Math.ceil(benchmark.peer_count * 0.66)
                      ? 'bg-[#FFF6E5] text-[#C27803] border-[#FFE1A8]'
                      : 'bg-[#FEECEB] text-[#D92D20] border-[#FECDCA]'
                  }`}
                >
                  Rank {benchmark.rank} of {benchmark.peer_count}
                </span>
              </div>

              {/* Metrics Highlights Table */}
              <div className="py-3 space-y-2 text-xs">
                {benchmark.metrics.slice(0, 3).map((m) => (
                  <div
                    key={m.name}
                    className="flex items-center justify-between py-1.5 border-b border-slate-50 last:border-none"
                  >
                    <span className="text-[#002970] font-semibold">{m.label}</span>
                    <div className="flex items-center gap-2">
                      <span className="font-black text-[#002970]">
                        {m.unit === '₹' ? `₹${Math.round(m.you)}` : `${m.you}${m.unit}`}
                      </span>
                      <span className="text-[10px] text-[#4F6A94]">
                        vs {m.unit === '₹' ? `₹${Math.round(m.peer_median)}` : `${m.peer_median}${m.unit}`}
                      </span>
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-extrabold ${
                          m.status === 'green'
                            ? 'bg-[#E8F8F0] text-[#008A54]'
                            : m.status === 'yellow'
                            ? 'bg-[#FFF6E5] text-[#C27803]'
                            : 'bg-[#FEECEB] text-[#D92D20]'
                        }`}
                      >
                        {m.status_text}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Top Action Recommendation */}
              <div className="mt-1 p-3 rounded-xl bg-[#F0F8FE] border border-[#CDE5F7] text-xs">
                <span className="font-extrabold text-[#002970] block text-[11px]">Recommended Action:</span>
                <p className="text-[11px] text-[#4F6A94] mt-0.5 line-clamp-2 font-medium">
                  {benchmark.metrics.find((m) => m.status === 'red' || m.status === 'yellow')?.action ||
                    benchmark.metrics[0]?.action}
                </p>
              </div>

              {/* Card Bottom CTA Buttons */}
              <div className="mt-3.5 flex items-center justify-between pt-2.5 border-t border-[#E8F4FD] text-xs">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onNavigateTab('recommendations')}
                  className="text-xs py-1.5 px-3 text-[#002970] font-bold"
                >
                  Offer bhejein
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => onNavigateTab('compare')}
                  className="text-xs py-1.5 px-3.5 flex items-center gap-1 font-bold"
                >
                  <span>Details dekhein</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
          )}

          {/* Priority Actions Card */}
          <div className="bg-white rounded-2xl border border-[#CDE5F7] p-5 shadow-paytm">
            <div className="flex items-center justify-between pb-3 border-b border-[#E8F4FD]">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#00BAF2]" />
                <h3 className="text-sm font-extrabold text-[#002970]">Priority Actions</h3>
              </div>
              <span className="px-2 py-0.5 rounded-full text-xs font-extrabold bg-[#FEECEB] text-[#D92D20] border border-[#FECDCA]">
                {summary.critical_actions_count} Critical
              </span>
            </div>

            <div className="divide-y divide-[#E8F4FD] mt-2">
              {actions.map((act) => (
                <div
                  key={act.recommendation_id}
                  className="py-3 hover:bg-[#F0F8FE] rounded-xl p-2.5 transition-colors cursor-pointer"
                  onClick={() => onSelectAction(act.recommendation_id)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-bold text-[#002970] line-clamp-1">
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
                  <p className="text-[11px] text-[#4F6A94] mt-1 line-clamp-2 font-medium">
                    {act.action}
                  </p>
                  <div className="mt-2 flex items-center justify-between text-[11px]">
                    <span className="font-extrabold text-[#008A54]">
                      Impact: ₹{act.expected_impact.toLocaleString()}
                    </span>
                    <span className="text-[#00BAF2] hover:text-[#002970] font-bold">
                      Review &rarr;
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-3 pt-3 border-t border-[#E8F4FD]">
              <Button
                variant="secondary"
                size="sm"
                className="w-full text-xs font-bold"
                onClick={() => onNavigateTab('recommendations')}
              >
                Open Action Center ({summary.total_actions_pending})
              </Button>
            </div>
          </div>

          {/* Quick Copilot Interactive Card */}
          <div className="bg-[#F0F8FE] rounded-2xl border-2 border-[#CDE5F7] p-5 shadow-xs">
            <div className="flex items-center gap-2 text-xs font-black text-[#002970]">
              <Bot className="w-4 h-4 text-[#00BAF2]" />
              <span>Ask VyaparMitra Copilot</span>
            </div>
            <p className="text-[11px] text-[#4F6A94] mt-1 font-medium">
              Sales, forecast, stockouts, ya Graahak ke baare mein Hindi/Hinglish me poochhein.
            </p>

            <form onSubmit={handleQuickAsk} className="mt-3 space-y-2">
              <input
                type="text"
                value={quickQuery}
                onChange={(e) => setQuickQuery(e.target.value)}
                placeholder="e.g. Kal kitni bikri hui thi?"
                className="w-full px-3.5 py-2.5 text-xs rounded-xl border border-[#CDE5F7] bg-white focus:outline-none focus:ring-2 focus:ring-[#00BAF2] font-medium"
              />
              <Button type="submit" variant="primary" size="sm" className="w-full text-xs font-bold">
                Ask Copilot
              </Button>
            </form>

            <div className="mt-3 flex flex-wrap gap-1.5">
              {[
                'Agle hafte sales kitni hogi?',
                'Kaunsa maal restock karein?',
                'Meri dukaan dusron se kaisi hai?',
              ].map((q, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => onQuickCopilot(q)}
                  className="text-[10px] bg-white border border-[#CDE5F7] text-[#4F6A94] hover:text-[#00BAF2] hover:border-[#00BAF2] rounded-lg px-2.5 py-1 transition-colors text-left font-semibold shadow-2xs"
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
