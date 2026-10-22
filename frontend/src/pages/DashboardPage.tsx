import React, { useEffect, useState, useMemo } from 'react';
import {
  TrendingUp,
  Sparkles,
  Bot,
  ArrowRight,
  ShoppingBag,
  DollarSign,
  Package,
  Trophy,
  Volume2,
  ShieldCheck,
  Zap,
  Activity,
  Calendar,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../api/client';
import { ActionItem, BenchmarkData, DashboardSummary, SalesAnalytics, DailySalesPoint } from '../types';
import { MetricCard } from '../components/MetricCard';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { CardSkeleton, ChartSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner } from '../components/EmptyState';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';

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
  const { t, language } = useLanguage();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [actions, setActions] = useState<ActionItem[]>([]);
  const [salesAnalytics, setSalesAnalytics] = useState<SalesAnalytics | null>(null);
  const [benchmark, setBenchmark] = useState<BenchmarkData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [quickQuery, setQuickQuery] = useState<string>('');
  const [soundboxPlayed, setSoundboxPlayed] = useState<boolean>(false);
  const [timeRange, setTimeRange] = useState<'7D' | '14D'>('7D');
  const [activeDayIndex, setActiveDayIndex] = useState<number | null>(null);

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
    try {
      const utterance = new SpeechSynthesisUtterance();
      if (language === 'hindi') {
        utterance.text = '४२५० रुपये प्राप्त हुए!';
        utterance.lang = 'hi-IN';
      } else {
        utterance.text = '4250 rupees prapt hue!';
        utterance.lang = 'hi-IN';
      }
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.error('Audio playback failed', e);
    }
    setTimeout(() => setSoundboxPlayed(false), 4000);
  };

  // Slice historical days based on selected time range (7D / 14D)
  const daysToDisplay = useMemo<DailySalesPoint[]>(() => {
    const series = salesAnalytics?.daily_series || [];
    const count = timeRange === '7D' ? 7 : 14;
    return series.slice(-count);
  }, [salesAnalytics, timeRange]);

  // Derived statistics for the chart
  const { periodTotal, periodOrders, periodAvg, maxRev } = useMemo(() => {
    const total = daysToDisplay.reduce((sum, d) => sum + (d.revenue || 0), 0);
    const orders = daysToDisplay.reduce((sum, d) => sum + (d.orders || 0), 0);
    const avg = daysToDisplay.length > 0 ? total / daysToDisplay.length : 0;
    const max = Math.max(...daysToDisplay.map((d) => d.revenue || 0), 1000);
    return { periodTotal: total, periodOrders: orders, periodAvg: avg, maxRev: max };
  }, [daysToDisplay]);

  // Daily Run-Rate Calculations
  const { projectedDailyRunRate, recentDailyRunRate, runRateDiffPct } = useMemo(() => {
    const proj = summary?.forecast_7d_total_revenue ? summary.forecast_7d_total_revenue / 7 : 0;
    const recent7 = (salesAnalytics?.daily_series || []).slice(-7);
    const recentTotal = recent7.reduce((sum, d) => sum + (d.revenue || 0), 0);
    const actual = recent7.length > 0 ? recentTotal / recent7.length : 0;
    const diff = actual > 0 ? ((proj - actual) / actual) * 100 : 0;
    return {
      projectedDailyRunRate: proj,
      recentDailyRunRate: actual,
      runRateDiffPct: diff,
    };
  }, [summary, salesAnalytics]);

  if (loading) {
    return (
      <div className="space-y-6">
        {/* Header Skeleton */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 p-6 animate-pulse">
          <div className="h-5 bg-slate-200 dark:bg-slate-800 rounded w-1/4 mb-2.5" />
          <div className="h-3.5 bg-slate-200 dark:bg-slate-800 rounded w-1/3" />
        </div>

        {/* KPI Grid Skeletons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>

        {/* Main Content Skeletons */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <ChartSkeleton />
            <CardSkeleton />
          </div>
          <div className="space-y-6">
            <CardSkeleton />
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

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      {/* Unified Executive Header */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 p-5 sm:p-6 shadow-xs transition-colors">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          {/* Left: Merchant Greeting & Store Meta */}
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                {t('greeting', 'Shubh Prabhat, Merchant Ji 👋')}
              </h1>
              <Badge variant="success">
                <ShieldCheck className="w-3.5 h-3.5 mr-1 text-emerald-600 dark:text-emerald-400" />
                {t('verified_merchant', 'Verified Store')}
              </Badge>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1 font-normal flex items-center gap-2 flex-wrap">
              <span>{t('store_name', 'Vyapar Store')} &bull; ID: M001</span>
              <span>&bull;</span>
              <span>Lucknow FMCG & Retail</span>
              <span>&bull;</span>
              <span className="text-slate-400 dark:text-slate-500">
                {t('last_14_days', 'Last 14 recorded business days')}
              </span>
            </p>
          </div>

          {/* Right: Soundbox Status Widget & Action CTAs */}
          <div className="flex flex-wrap items-center gap-2.5 sm:gap-3 shrink-0">
            {/* Integrated Smart Soundbox Mini Widget */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-850 border border-slate-200/80 dark:border-slate-800 text-xs">
              <div className="w-6 h-6 rounded-md bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
                <Volume2 className={`w-3.5 h-3.5 ${soundboxPlayed ? 'animate-bounce text-blue-600 dark:text-blue-400' : ''}`} />
              </div>
              <div className="text-[11px] leading-tight">
                <div className="flex items-center gap-1 font-bold text-slate-800 dark:text-slate-200">
                  <span>Smart Soundbox</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                </div>
                <div className="text-[10px] text-slate-500 dark:text-slate-400">
                  {soundboxPlayed
                    ? (language === 'hindi' ? '🔊 "₹4,250 प्राप्त हुए!"' : '🔊 "₹4,250 prapt hue!"')
                    : '100% Instant Audio'}
                </div>
              </div>
              <button
                onClick={handleTestSoundbox}
                className="ml-1 p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-blue-600 dark:text-blue-400 transition-colors"
                title="Test Audio Announcement"
                aria-label="Test Audio Announcement"
              >
                <Zap className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Quick Brief Button */}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onQuickCopilot(language === 'hindi' ? 'मुझे आज का पूरा व्यापार सारांश बताओ' : 'Mujhe aaj ka poora business brief batao')}
              className="text-xs"
            >
              <Sparkles className="w-3.5 h-3.5 mr-1.5 text-purple-600 dark:text-purple-400" />
              {t('todays_brief', "Today's Brief")}
            </Button>

            {/* Priority Actions Button */}
            <Button
              variant="primary"
              size="sm"
              onClick={() => onNavigateTab('recommendations')}
              className="text-xs"
            >
              <span>{summary.total_actions_pending} {t('priority_actions_btn', 'Priority Actions')}</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </div>
        </div>
      </div>

      {/* Primary KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
        <MetricCard
          card={summary.kpis.revenue}
          icon={<DollarSign className="w-4 h-4" />}
          accentColor="blue"
        />
        <MetricCard
          card={summary.kpis.orders}
          icon={<ShoppingBag className="w-4 h-4" />}
          accentColor="navy"
        />
        <MetricCard
          card={summary.kpis.aov}
          icon={<TrendingUp className="w-4 h-4" />}
          accentColor="green"
        />
        <MetricCard
          card={summary.kpis.units}
          icon={<Package className="w-4 h-4" />}
          accentColor="orange"
        />
      </div>

      {/* Main Grid: Left Charts & Forecast + Right Benchmarking & Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Revenue Trend & Daily Run-rate */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* Revenue Trend Chart Card */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 p-5 sm:p-6 shadow-xs transition-colors">
            {/* Header: Title, Range Toggle, Trend Status */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Activity className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <span>
                    {timeRange === '7D'
                      ? t('trend_7d', '7-Day Revenue Trend')
                      : t('trend_14d', '14-Day Revenue Trend')}
                  </span>
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
                  {timeRange === '7D'
                    ? 'Recent 7 recorded store business days'
                    : t('last_14_days', 'Last 14 recorded business days')}
                </p>
              </div>

              <div className="flex items-center gap-2 self-start sm:self-auto">
                {/* 7D / 14D Segmented Toggle */}
                <div className="flex items-center bg-slate-100 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700 rounded-lg p-0.5 text-xs">
                  <button
                    onClick={() => setTimeRange('7D')}
                    className={`px-2.5 py-1 rounded-md font-bold transition-colors ${
                      timeRange === '7D'
                        ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-300 shadow-2xs'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                    }`}
                  >
                    7D
                  </button>
                  <button
                    onClick={() => setTimeRange('14D')}
                    className={`px-2.5 py-1 rounded-md font-bold transition-colors ${
                      timeRange === '14D'
                        ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-300 shadow-2xs'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                    }`}
                  >
                    14D
                  </button>
                </div>

                {/* Trend Badge */}
                <span
                  className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${
                    summary.sales_trend_direction === 'DECREASING'
                      ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800/60'
                      : summary.sales_trend_direction === 'INCREASING'
                      ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/60'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700'
                  }`}
                >
                  {summary.sales_trend_direction === 'DECREASING'
                    ? t('trend_decreasing', 'Trend: DECREASING')
                    : summary.sales_trend_direction === 'INCREASING'
                    ? t('trend_increasing', 'Trend: INCREASING')
                    : t('trend_stable', 'Trend: STABLE')}
                </span>
              </div>
            </div>

            {/* Metric Summary Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 mb-5 bg-slate-50 dark:bg-slate-850 rounded-xl border border-slate-200/80 dark:border-slate-800 text-xs">
              <div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium block">
                  {t('period_total_label', 'Period Total:')}
                </span>
                <span className="text-sm font-bold text-slate-900 dark:text-white tabular-nums">
                  ₹{periodTotal.toLocaleString('en-IN')}
                </span>
              </div>
              <div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium block">
                  {t('daily_avg_label', 'Daily Average:')}
                </span>
                <span className="text-sm font-bold text-blue-600 dark:text-blue-400 tabular-nums">
                  ₹{Math.round(periodAvg).toLocaleString('en-IN')}/day
                </span>
              </div>
              <div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium block">
                  Total Orders:
                </span>
                <span className="text-sm font-bold text-slate-900 dark:text-white tabular-nums">
                  {periodOrders.toLocaleString('en-IN')}
                </span>
              </div>
              <div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium block">
                  Peak Collection:
                </span>
                <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
                  ₹{maxRev.toLocaleString('en-IN')}
                </span>
              </div>
            </div>

            {/* Custom Bar Visualization with Gridlines and Tooltip */}
            <div className="relative pt-6 pb-2">
              {/* Subtle Horizontal Gridlines */}
              <div className="absolute inset-x-0 top-6 bottom-10 flex flex-col justify-between pointer-events-none opacity-40">
                <div className="border-b border-dashed border-slate-200 dark:border-slate-800 w-full" />
                <div className="border-b border-dashed border-slate-200 dark:border-slate-800 w-full" />
                <div className="border-b border-dashed border-slate-200 dark:border-slate-800 w-full" />
                <div className="border-b border-slate-200 dark:border-slate-800 w-full" />
              </div>

              {/* Bars Container */}
              <div className="h-56 flex items-end justify-between gap-1.5 sm:gap-2.5 relative z-10">
                {daysToDisplay.map((day, idx) => {
                  const heightPct = Math.max(8, (day.revenue / maxRev) * 100);
                  const isHovered = activeDayIndex === idx;

                  const dateObj = new Date(day.date);
                  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                  const dayOfWeek = dayNames[dateObj.getDay()] || '';
                  const formattedDate = `${dateObj.getDate()}/${dateObj.getMonth() + 1}`;

                  return (
                    <div
                      key={day.date || idx}
                      className="flex-1 flex flex-col items-center group relative h-full justify-end cursor-pointer"
                      onMouseEnter={() => setActiveDayIndex(idx)}
                      onMouseLeave={() => setActiveDayIndex(null)}
                      onClick={() => setActiveDayIndex(activeDayIndex === idx ? null : idx)}
                    >
                      {/* Floating Theme-Aware Tooltip */}
                      {isHovered && (
                        <div className="absolute -top-14 z-30 pointer-events-none whitespace-nowrap bg-slate-900 dark:bg-slate-800 text-white border border-slate-700/80 rounded-lg px-3 py-1.5 shadow-xl text-center text-xs animate-in fade-in-50 duration-150">
                          <div className="font-semibold text-[11px] text-slate-300">
                            {dayOfWeek}, {day.date}
                          </div>
                          <div className="font-bold text-white text-xs mt-0.5 tabular-nums">
                            ₹{day.revenue.toLocaleString('en-IN')} &bull; {day.orders} orders
                          </div>
                          {day.orders > 0 && (
                            <div className="text-[10px] text-blue-300 tabular-nums">
                              AOV: ₹{Math.round(day.revenue / day.orders).toLocaleString('en-IN')}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Bar Pillar */}
                      <div
                        className={`w-full rounded-t-md transition-all duration-150 ${
                          isHovered
                            ? 'bg-blue-600 dark:bg-blue-400 shadow-md ring-2 ring-blue-500/20'
                            : 'bg-blue-500 hover:bg-blue-600 dark:bg-blue-600/80 dark:hover:bg-blue-500'
                        }`}
                        style={{ height: `${heightPct}%` }}
                      />

                      {/* X-Axis Date Labels */}
                      <div className="mt-2 text-center w-full truncate leading-tight">
                        <span className="block text-[10px] font-bold text-slate-700 dark:text-slate-300">
                          {dayOfWeek}
                        </span>
                        <span className="block text-[9px] text-slate-400 dark:text-slate-500">
                          {formattedDate}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Chart Footer Link */}
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
              <span className="font-medium">
                {t('peak_collection', 'Peak Day Collection:')}{' '}
                <strong className="text-slate-900 dark:text-white font-bold tabular-nums">
                  ₹{maxRev.toLocaleString('en-IN')}
                </strong>
              </span>
              <button
                onClick={() => onNavigateTab('analytics')}
                className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-bold inline-flex items-center gap-1 transition-colors"
              >
                <span>{t('deep_analytics', 'Deep Analytics')}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Daily Sales Run-Rate & AI Forecast Module */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 p-5 sm:p-6 shadow-xs transition-colors">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 border border-blue-200/60 dark:border-blue-800/60 flex items-center justify-center font-bold">
                  <TrendingUp className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                    {t('forecast_7d_title', 'Sales Forecast • 7-Day Revenue Projection')}
                  </h2>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                    {t('forecast_7d_subtext')}
                  </p>
                </div>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => onNavigateTab('forecasts')}
                className="text-xs shrink-0 hidden sm:inline-flex"
              >
                {t('view_sku_forecasts', 'View SKU Forecasts')}
                <ArrowRight className="w-3 h-3 ml-1" />
              </Button>
            </div>

            {/* Split Metric Cards: 7-Day Cumulative Total & Daily Sales Run-Rate */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
              {/* 7-Day Total Projection */}
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200/80 dark:border-slate-800 flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                    7-Day Projected Total
                  </span>
                  <p className="text-2xl font-extrabold text-slate-900 dark:text-white mt-1 tabular-nums">
                    ₹{summary.forecast_7d_total_revenue.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </p>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2 flex items-center gap-1.5 font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0" />
                  <span>Cumulative forward ML revenue prediction</span>
                </p>
              </div>

              {/* Daily Sales Run-Rate */}
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200/80 dark:border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block truncate">
                      {t('daily_run_rate_label', 'Daily Sales Run-Rate')}
                    </span>
                    <span
                      className={`inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-bold border shrink-0 ${
                        runRateDiffPct >= 0
                          ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/60'
                          : 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800/60'
                      }`}
                    >
                      {runRateDiffPct >= 0 ? '+' : ''}{runRateDiffPct.toFixed(1)}% vs recent pace
                    </span>
                  </div>
                  <p className="text-2xl font-extrabold text-blue-600 dark:text-blue-400 mt-1 tabular-nums">
                    ₹{projectedDailyRunRate.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 ml-1">/ day</span>
                  </p>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2 flex items-center gap-1.5 font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                  <span className="truncate">{t('daily_run_rate_sub', 'Required daily pace to meet projected 7-day total')}</span>
                </p>
              </div>
            </div>

            {/* Mobile SKU Forecasts Button */}
            <div className="mt-4 sm:hidden">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => onNavigateTab('forecasts')}
                className="w-full text-xs"
              >
                {t('view_sku_forecasts', 'View SKU Forecasts')}
                <ArrowRight className="w-3 h-3 ml-1" />
              </Button>
            </div>
          </div>
        </div>

        {/* Right 1 Col: Peer Benchmarking, Actions & Quick Copilot */}
        <div className="flex flex-col gap-6">
          {/* Peer Benchmarking Summary Card */}
          {benchmark && (
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 p-5 shadow-xs transition-colors">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 border border-amber-200/60 dark:border-amber-800/60">
                    <Trophy className="w-4 h-4" />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                      {t('peers_comparison', 'Peers se tulna')}
                    </h2>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                      {localizeDynamicText(benchmark.peer_group, language)}
                    </p>
                  </div>
                </div>

                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                    benchmark.rank <= Math.ceil(benchmark.peer_count * 0.33)
                      ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/60'
                      : benchmark.rank <= Math.ceil(benchmark.peer_count * 0.66)
                      ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800/60'
                      : 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border-red-200 dark:border-red-900/60'
                  }`}
                >
                  {language === 'hindi'
                    ? `रैंक: ${benchmark.peer_count} में से ${benchmark.rank}`
                    : language === 'hinglish'
                    ? `Rank: ${benchmark.peer_count} me se ${benchmark.rank}`
                    : `Rank ${benchmark.rank} of ${benchmark.peer_count}`}
                </span>
              </div>

              {/* Metrics Highlights */}
              <div className="py-2.5 space-y-2 text-xs">
                {benchmark.metrics.slice(0, 3).map((m) => (
                  <div
                    key={m.name}
                    className="flex items-center justify-between py-1.5 border-b border-slate-50 dark:border-slate-800/60 last:border-none"
                  >
                    <span className="text-slate-700 dark:text-slate-300 font-medium">
                      {localizeDynamicText(m.label, language)}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-900 dark:text-white tabular-nums">
                        {m.unit === '₹' ? `₹${Math.round(m.you)}` : `${m.you}${m.unit}`}
                      </span>
                      <span className="text-[10px] text-slate-400 tabular-nums">
                        vs {m.unit === '₹' ? `₹${Math.round(m.peer_median)}` : `${m.peer_median}${m.unit}`}
                      </span>
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                          m.status === 'green'
                            ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300'
                            : m.status === 'yellow'
                            ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300'
                            : 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300'
                        }`}
                      >
                        {localizeDynamicText(m.status_text, language)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Top Action Recommendation */}
              <div className="mt-1 p-3 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200/80 dark:border-slate-800 text-xs">
                <span className="font-bold text-slate-900 dark:text-white block text-[11px]">
                  {t('recommended_action', 'Recommended Action:')}
                </span>
                <p className="text-[11px] text-slate-600 dark:text-slate-300 mt-0.5 line-clamp-2 font-normal">
                  {localizeDynamicText(
                    benchmark.metrics.find((m) => m.status === 'red' || m.status === 'yellow')?.action ||
                    benchmark.metrics[0]?.action,
                    language
                  )}
                </p>
              </div>

              {/* Bottom CTAs */}
              <div className="mt-3.5 flex items-center justify-between pt-2.5 border-t border-slate-100 dark:border-slate-800 text-xs gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => onNavigateTab('recommendations')}
                  className="text-xs"
                >
                  {t('send_offer', 'Offer bhejein')}
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => onNavigateTab('compare')}
                  className="text-xs"
                >
                  <span>{t('view_details', 'Details dekhein')}</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </Button>
              </div>
            </div>
          )}

          {/* Priority Actions Card */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 p-5 shadow-xs transition-colors">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                  {t('priority_actions_title', 'Priority Actions')}
                </h2>
              </div>
              <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-900/60">
                {summary.critical_actions_count} {t('critical_badge', 'Critical')}
              </span>
            </div>

            <div className="divide-y divide-slate-100 dark:divide-slate-800 mt-1">
              {actions.map((act) => (
                <div
                  key={act.recommendation_id}
                  className="py-2.5 hover:bg-slate-50 dark:hover:bg-slate-850 rounded-lg p-2 transition-colors cursor-pointer"
                  onClick={() => onSelectAction(act.recommendation_id)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-bold text-slate-900 dark:text-white line-clamp-1">
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
                      {localizeDynamicText(act.priority_band, language)}
                    </Badge>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2 font-normal">
                    {act.action}
                  </p>
                  <div className="mt-1.5 flex items-center justify-between text-[11px]">
                    <span className="font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
                      {t('expected_impact_label', 'Impact:')} ₹{act.expected_impact.toLocaleString()}
                    </span>
                    <span className="text-blue-600 hover:text-blue-700 dark:text-blue-400 font-bold">
                      {t('review_btn', 'Review →')}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800">
              <Button
                variant="secondary"
                size="sm"
                className="w-full text-xs font-bold"
                onClick={() => onNavigateTab('recommendations')}
              >
                {t('open_action_center_btn', 'Open Action Center')} ({summary.total_actions_pending})
              </Button>
            </div>
          </div>

          {/* Quick Copilot Interactive Card (Purple AI Accent) */}
          <div className="bg-purple-50/40 dark:bg-purple-950/20 rounded-xl border border-purple-200 dark:border-purple-900/40 p-5 shadow-xs transition-colors">
            <div>
              <div className="flex items-center gap-2 text-xs font-bold text-purple-900 dark:text-purple-200">
                <Bot className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <span>{t('ask_copilot_box_title', 'Ask VyaparMitra Copilot')}</span>
              </div>
              <p className="text-[11px] text-purple-700/80 dark:text-purple-300/80 mt-1 font-normal">
                {t('ask_copilot_box_sub')}
              </p>

              <form onSubmit={handleQuickAsk} className="mt-3 space-y-2">
                <input
                  type="text"
                  value={quickQuery}
                  onChange={(e) => setQuickQuery(e.target.value)}
                  placeholder={t('quick_ask_placeholder', 'e.g. Kal kitni bikri hui thi?')}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-purple-200 dark:border-purple-800/60 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-600 font-medium transition-colors"
                />
                <Button type="submit" variant="ai" size="sm" className="w-full text-xs font-bold">
                  {t('ask_btn', 'Ask Copilot')}
                </Button>
              </form>
            </div>

            <div className="mt-3 flex flex-wrap gap-1.5">
              {(language === 'hindi'
                ? [
                    'अगले हफ्ते बिक्री कितनी होगी?',
                    'कौन सा सामान रीस्टॉक करें?',
                    'मेरी दुकान दूसरों से कैसी है?',
                  ]
                : [
                    'Agle hafte sales kitni hogi?',
                    'Kaunsa maal restock karein?',
                    'Meri dukaan dusron se kaisi hai?',
                  ]
              ).map((q, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => onQuickCopilot(q)}
                  className="text-[10px] bg-white dark:bg-slate-900 border border-purple-200 dark:border-purple-800/50 text-purple-800 dark:text-purple-300 hover:border-purple-400 rounded-md px-2 py-1 transition-colors text-left font-medium shadow-2xs"
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
