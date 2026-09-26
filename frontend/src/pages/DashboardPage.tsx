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
                {t('soundbox_banner_title', 'Paytm Soundbox 4.0 Live')}
              </span>
              <span className="px-1.5 py-0.2 rounded-full text-[9px] font-bold bg-[#00B970] text-white">
                Audio Active
              </span>
            </div>
            <p className="text-sm font-bold text-white mt-0.5">
              {soundboxPlayed
                ? (language === 'hindi' ? '🔊 "पेटीएम पर ₹4,250 प्राप्त हुए!"' : '🔊 "Paytm par ₹4,250 prapt hue!"')
                : t('soundbox_banner_text')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
          <button
            onClick={handleTestSoundbox}
            className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold border border-white/20 transition-all flex items-center gap-1.5"
          >
            <Zap className="w-3.5 h-3.5 text-[#00BAF2]" />
            <span>{t('test_audio', 'Test Audio')}</span>
          </button>
          <span className="text-xs text-blue-200 font-medium hidden md:inline">
            {t('instant_settlement', '100% Instant Bank Settlement')}
          </span>
        </div>
      </div>

      {/* Welcome Banner */}
      <div className="bg-white dark:bg-[#0F1D38] rounded-2xl border border-[#CDE5F7] dark:border-[#1E3A6E] p-6 shadow-paytm flex flex-col md:flex-row md:items-center justify-between gap-4 transition-colors">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-xl lg:text-2xl font-black text-[#002970] dark:text-white tracking-tight">
              {t('greeting', 'Shubh Prabhat, Merchant Ji 👋')}
            </h2>
            <Badge variant="demo">{t('verified_merchant', 'Paytm Verified Store')}</Badge>
          </div>
          <p className="text-xs text-[#4F6A94] dark:text-blue-200 mt-1 max-w-xl font-medium">
            {t('welcome_subtext')}
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onQuickCopilot(language === 'hindi' ? 'मुझे आज का पूरा व्यापार सारांश बताओ' : 'Mujhe aaj ka poora business brief batao')}
            className="text-xs font-bold dark:border-[#00BAF2] dark:text-[#00BAF2] dark:hover:bg-[#132342]"
          >
            <Sparkles className="w-3.5 h-3.5 mr-1.5 text-[#00BAF2]" />
            {t('todays_brief', "Today's Brief")}
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => onNavigateTab('recommendations')}
            className="text-xs font-bold"
          >
            <span>{summary.total_actions_pending} {t('priority_actions_btn', 'Priority Actions')}</span>
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
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* Recent Sales History Chart */}
          <div className="bg-white dark:bg-[#0F1D38] rounded-2xl border border-[#CDE5F7] dark:border-[#1E3A6E] p-6 shadow-paytm transition-colors">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-extrabold text-[#002970] dark:text-white">{t('daily_sales_trend', 'Daily Sales Trend (Bikri)')}</h3>
                <p className="text-xs text-[#4F6A94] dark:text-blue-200 font-medium">{t('last_14_days', 'Last 14 recorded business days')}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-[#E8F8F0] dark:bg-[#00B970]/20 text-[#008A54] dark:text-[#00E68A] border border-[#B6E8D0] dark:border-[#00B970]/30">
                  {summary.sales_trend_direction === 'DECREASING'
                    ? t('trend_decreasing', 'Trend: DECREASING')
                    : summary.sales_trend_direction === 'INCREASING'
                    ? t('trend_increasing', 'Trend: INCREASING')
                    : t('trend_stable', 'Trend: STABLE')}
                </span>
              </div>
            </div>

            {/* Custom Bar Visualization */}
            <div className="h-56 flex items-end justify-between gap-1.5 pt-6 pb-2 border-b border-[#E8F4FD] dark:border-[#1E3A6E]">
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
                      className="w-full bg-gradient-to-t from-[#00BAF2] to-[#41C9F7] hover:from-[#002970] hover:to-[#001D4E] dark:hover:from-white dark:hover:to-[#00BAF2] rounded-t-lg transition-all duration-150 cursor-pointer shadow-2xs"
                      style={{ height: `${heightPct}%` }}
                    />
                    {/* Date label — Day name + date */}
                    <span className="text-[10px] text-[#4F6A94] dark:text-slate-400 font-semibold mt-2 truncate w-full text-center leading-tight">
                      {(() => {
                        const d = new Date(day.date);
                        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                        return (
                          <>
                            <span className="block text-[9px] font-bold text-[#002970] dark:text-blue-200">{dayNames[d.getDay()]}</span>
                            <span className="block">{d.getDate()}/{d.getMonth() + 1}</span>
                          </>
                        );
                      })()}
                    </span>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 flex items-center justify-between text-xs text-[#4F6A94] dark:text-blue-200">
              <span className="font-semibold">
                {t('peak_collection', 'Peak Day Collection:')}{' '}
                <strong className="text-[#002970] dark:text-white font-extrabold">₹{maxRev.toLocaleString()}</strong>
              </span>
              <button
                onClick={() => onNavigateTab('analytics')}
                className="text-[#00BAF2] hover:text-[#002970] dark:hover:text-white font-bold inline-flex items-center gap-1 transition-colors"
              >
                {t('deep_analytics', 'Deep Analytics')} <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* 7-Day Forward Forecast Banner with Paytm Royalty */}
          <div className="bg-gradient-to-r from-[#002970] via-[#00388F] to-[#001D4E] text-white rounded-2xl p-6 shadow-soundbox border border-[#00BAF2]/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-black text-[#00BAF2] uppercase tracking-wider">
                <TrendingUp className="w-4 h-4 text-[#00BAF2]" />
                <span>{t('forecast_7d_title', 'Predictive AI • 7-Day Forecast')}</span>
              </div>
              <p className="text-3xl font-black mt-1 text-white tracking-tight">
                ₹{summary.forecast_7d_total_revenue.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-blue-100 mt-1 max-w-md font-medium">
                {t('forecast_7d_subtext')}
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigateTab('forecasts')}
              className="border-white/40 text-white hover:bg-white/10 shrink-0 font-bold"
            >
              {t('view_sku_forecasts', 'View SKU Forecasts')}
            </Button>
          </div>
        </div>

        {/* Right 1 Col: Priority Action Center & Quick Ask */}
        <div className="flex flex-col gap-6">
          {/* Peer Benchmarking Summary Card */}
          {benchmark && (
            <div className="bg-white dark:bg-[#0F1D38] rounded-2xl border-2 border-[#CDE5F7] dark:border-[#1E3A6E] p-5 shadow-paytm relative overflow-hidden transition-colors">
              <div className="flex items-center justify-between pb-3 border-b border-[#E8F4FD] dark:border-[#1E3A6E]">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-gradient-to-br from-[#E0F4FD] to-[#C9EDFC] dark:from-[#0B254A] dark:to-[#0F356B] text-[#00BAF2] border border-[#B3E3FA] dark:border-[#1A4B8C]">
                    <Trophy className="w-4 h-4 text-[#00BAF2]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-extrabold text-[#002970] dark:text-white">{t('peers_comparison', 'Peers se tulna')}</h3>
                    <p className="text-[10px] text-[#4F6A94] dark:text-blue-200 font-semibold">{localizeDynamicText(benchmark.peer_group, language)}</p>
                  </div>
                </div>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-extrabold ${
                    benchmark.rank <= Math.ceil(benchmark.peer_count * 0.33)
                      ? 'bg-[#E8F8F0] dark:bg-[#00B970]/20 text-[#008A54] dark:text-[#00E68A] border border-[#B6E8D0] dark:border-[#00B970]/30'
                      : benchmark.rank <= Math.ceil(benchmark.peer_count * 0.66)
                      ? 'bg-[#FFF6E5] dark:bg-[#FFB800]/20 text-[#C27803] dark:text-[#FFCA33] border border-[#FFE1A8] dark:border-[#FFB800]/30'
                      : 'bg-[#FEECEB] dark:bg-[#FF4D4D]/20 text-[#D92D20] dark:text-[#FF8080] border border-[#FECDCA] dark:border-[#FF4D4D]/30'
                  }`}
                >
                  {language === 'hindi'
                    ? `रैंक: ${benchmark.peer_count} में से ${benchmark.rank}`
                    : language === 'hinglish'
                    ? `Rank: ${benchmark.peer_count} me se ${benchmark.rank}`
                    : `Rank ${benchmark.rank} of ${benchmark.peer_count}`}
                </span>
              </div>

              {/* Metrics Highlights Table */}
              <div className="py-3 space-y-2 text-xs">
                {benchmark.metrics.slice(0, 3).map((m) => (
                  <div
                    key={m.name}
                    className="flex items-center justify-between py-1.5 border-b border-slate-50 dark:border-[#172E58] last:border-none"
                  >
                    <span className="text-[#002970] dark:text-blue-100 font-semibold">{localizeDynamicText(m.label, language)}</span>
                    <div className="flex items-center gap-2">
                      <span className="font-black text-[#002970] dark:text-white">
                        {m.unit === '₹' ? `₹${Math.round(m.you)}` : `${m.you}${m.unit}`}
                      </span>
                      <span className="text-[10px] text-[#4F6A94] dark:text-slate-400">
                        vs {m.unit === '₹' ? `₹${Math.round(m.peer_median)}` : `${m.peer_median}${m.unit}`}
                      </span>
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-extrabold ${
                          m.status === 'green'
                            ? 'bg-[#E8F8F0] dark:bg-[#00B970]/20 text-[#008A54] dark:text-[#00E68A]'
                            : m.status === 'yellow'
                            ? 'bg-[#FFF6E5] dark:bg-[#FFB800]/20 text-[#C27803] dark:text-[#FFCA33]'
                            : 'bg-[#FEECEB] dark:bg-[#FF4D4D]/20 text-[#D92D20] dark:text-[#FF8080]'
                        }`}
                      >
                        {localizeDynamicText(m.status_text, language)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Top Action Recommendation */}
              <div className="mt-1 p-3 rounded-xl bg-[#F0F8FE] dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E] text-xs">
                <span className="font-extrabold text-[#002970] dark:text-white block text-[11px]">{t('recommended_action', 'Recommended Action:')}</span>
                <p className="text-[11px] text-[#4F6A94] dark:text-blue-200 mt-0.5 line-clamp-2 font-medium">
                  {localizeDynamicText(
                    benchmark.metrics.find((m) => m.status === 'red' || m.status === 'yellow')?.action ||
                    benchmark.metrics[0]?.action,
                    language
                  )}
                </p>
              </div>

              {/* Card Bottom CTA Buttons */}
              <div className="mt-3.5 flex items-center justify-between pt-2.5 border-t border-[#E8F4FD] dark:border-[#1E3A6E] text-xs">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onNavigateTab('recommendations')}
                  className="text-xs py-1.5 px-3 text-[#002970] dark:text-blue-100 dark:border-[#1E3A6E] font-bold"
                >
                  {t('send_offer', 'Offer bhejein')}
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => onNavigateTab('compare')}
                  className="text-xs py-1.5 px-3.5 flex items-center gap-1 font-bold"
                >
                  <span>{t('view_details', 'Details dekhein')}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
          )}

          {/* Priority Actions Card */}
          <div className="bg-white dark:bg-[#0F1D38] rounded-2xl border border-[#CDE5F7] dark:border-[#1E3A6E] p-5 shadow-paytm transition-colors">
            <div className="flex items-center justify-between pb-3 border-b border-[#E8F4FD] dark:border-[#1E3A6E]">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#00BAF2]" />
                <h3 className="text-sm font-extrabold text-[#002970] dark:text-white">{t('priority_actions_title', 'Priority Actions')}</h3>
              </div>
              <span className="px-2 py-0.5 rounded-full text-xs font-extrabold bg-[#FEECEB] dark:bg-[#FF4D4D]/20 text-[#D92D20] dark:text-[#FF8080] border border-[#FECDCA] dark:border-[#FF4D4D]/30">
                {summary.critical_actions_count} {t('critical_badge', 'Critical')}
              </span>
            </div>

            <div className="divide-y divide-[#E8F4FD] dark:divide-[#172E58] mt-2">
              {actions.map((act) => (
                <div
                  key={act.recommendation_id}
                  className="py-3 hover:bg-[#F0F8FE] dark:hover:bg-[#132342] rounded-xl p-2.5 transition-colors cursor-pointer"
                  onClick={() => onSelectAction(act.recommendation_id)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-bold text-[#002970] dark:text-white line-clamp-1">
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
                  <p className="text-[11px] text-[#4F6A94] dark:text-blue-200 mt-1 line-clamp-2 font-medium">
                    {act.action}
                  </p>
                  <div className="mt-2 flex items-center justify-between text-[11px]">
                    <span className="font-extrabold text-[#008A54] dark:text-[#00E68A]">
                      {t('expected_impact_label', 'Impact:')} ₹{act.expected_impact.toLocaleString()}
                    </span>
                    <span className="text-[#00BAF2] hover:text-[#002970] dark:hover:text-white font-bold">
                      {t('review_btn', 'Review →')}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-3 pt-3 border-t border-[#E8F4FD] dark:border-[#1E3A6E]">
              <Button
                variant="secondary"
                size="sm"
                className="w-full text-xs font-bold dark:bg-[#132342] dark:border-[#1E3A6E] dark:text-white dark:hover:bg-[#1A335F]"
                onClick={() => onNavigateTab('recommendations')}
              >
                {t('open_action_center_btn', 'Open Action Center')} ({summary.total_actions_pending})
              </Button>
            </div>
          </div>

          {/* Quick Copilot Interactive Card */}
          <div className="bg-[#F0F8FE] dark:bg-[#132342] rounded-2xl border-2 border-[#CDE5F7] dark:border-[#1E3A6E] p-5 shadow-xs transition-colors">
            <div>
              <div className="flex items-center gap-2 text-xs font-black text-[#002970] dark:text-white">
                <Bot className="w-4 h-4 text-[#00BAF2]" />
                <span>{t('ask_copilot_box_title', 'Ask VyaparMitra Copilot')}</span>
              </div>
              <p className="text-[11px] text-[#4F6A94] dark:text-blue-200 mt-1 font-medium">
                {t('ask_copilot_box_sub')}
              </p>

              <form onSubmit={handleQuickAsk} className="mt-3 space-y-2">
                <input
                  type="text"
                  value={quickQuery}
                  onChange={(e) => setQuickQuery(e.target.value)}
                  placeholder={t('quick_ask_placeholder', 'e.g. Kal kitni bikri hui thi?')}
                  className="w-full px-3.5 py-2.5 text-xs rounded-xl border border-[#CDE5F7] dark:border-[#1E3A6E] bg-white dark:bg-[#0B1528] text-[#002970] dark:text-white focus:outline-none focus:ring-2 focus:ring-[#00BAF2] font-medium"
                />
                <Button type="submit" variant="primary" size="sm" className="w-full text-xs font-bold">
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
                  className="text-[10px] bg-white dark:bg-[#0F1D38] border border-[#CDE5F7] dark:border-[#1E3A6E] text-[#4F6A94] dark:text-blue-200 hover:text-[#00BAF2] hover:border-[#00BAF2] rounded-lg px-2.5 py-1 transition-colors text-left font-semibold shadow-2xs"
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
