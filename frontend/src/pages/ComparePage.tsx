import React, { useEffect, useState } from 'react';
import {
  Trophy,
  TrendingUp,
  HelpCircle,
  Share2,
  Copy,
  Check,
  AlertCircle,
  Info,
  ChevronRight,
  Store,
  ArrowUpRight,
  Sparkles,
  ShieldCheck,
  Percent,
  CheckCircle2,
  Send,
  Phone,
} from 'lucide-react';
import { api } from '../api/client';
import { BenchmarkData, BenchmarkMetric, MerchantInfo } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Modal } from '../components/Modal';
import { CardSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner } from '../components/EmptyState';
import { useLanguage } from '../i18n/LanguageContext';

interface ComparePageProps {
  onNavigateTab?: (tab: string) => void;
  onQuickCopilot?: (query: string) => void;
}

export const ComparePage: React.FC<ComparePageProps> = ({
  onNavigateTab,
  onQuickCopilot,
}) => {
  const { t, language, language: currentLanguage } = useLanguage();
  const [merchants, setMerchants] = useState<MerchantInfo[]>([]);
  const [selectedMerchantId, setSelectedMerchantId] = useState<string>('M015');
  const [benchmark, setBenchmark] = useState<BenchmarkData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Modals state
  const [isExplainModalOpen, setIsExplainModalOpen] = useState<boolean>(false);
  const [selectedExplainMetric, setSelectedExplainMetric] = useState<BenchmarkMetric | null>(null);
  const [isWhatsAppModalOpen, setIsWhatsAppModalOpen] = useState<boolean>(false);
  const [copiedWhatsApp, setCopiedWhatsApp] = useState<boolean>(false);

  // Twilio WhatsApp delivery state
  const [whatsAppPhone, setWhatsAppPhone] = useState<string>('+919876543210');
  const [sendingWhatsApp, setSendingWhatsApp] = useState<boolean>(false);
  const [whatsAppStatusMsg, setWhatsAppStatusMsg] = useState<string | null>(null);
  const [whatsAppStatusType, setWhatsAppStatusType] = useState<'success' | 'info' | 'error' | null>(null);

  // Load merchants list on mount
  useEffect(() => {
    const loadMerchantsList = async () => {
      try {
        const res = await api.getMerchants();
        setMerchants(res.merchants || []);
      } catch (err: any) {
        console.error('Failed to load merchants list:', err);
      }
    };
    loadMerchantsList();
  }, []);

  // Load benchmark data when selected merchant changes
  const loadBenchmark = async (mId: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getMerchantBenchmark(mId);
      setBenchmark(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load peer benchmark data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBenchmark(selectedMerchantId);
  }, [selectedMerchantId]);

  const handleCopyWhatsApp = () => {
    if (benchmark?.whatsapp_digest) {
      navigator.clipboard.writeText(benchmark.whatsapp_digest);
      setCopiedWhatsApp(true);
      setTimeout(() => setCopiedWhatsApp(false), 2500);
    }
  };

  const handleSendWhatsApp = async () => {
    if (!benchmark?.whatsapp_digest || !whatsAppPhone.trim()) return;
    setSendingWhatsApp(true);
    setWhatsAppStatusMsg(null);
    try {
      const res = await api.sendWhatsAppDigest(
        whatsAppPhone.trim(),
        benchmark.whatsapp_digest,
        benchmark.merchant_id
      );
      setWhatsAppStatusMsg(res.message);
      setWhatsAppStatusType(res.success ? (res.status === 'simulated' ? 'info' : 'success') : 'error');
    } catch (err: any) {
      setWhatsAppStatusMsg(err?.message || 'Failed to send WhatsApp message via Twilio');
      setWhatsAppStatusType('error');
    } finally {
      setSendingWhatsApp(false);
    }
  };

  const getStatusBadgeVariant = (status: string): 'success' | 'high' | 'critical' => {
    if (status === 'green') return 'success';
    if (status === 'yellow') return 'high';
    return 'critical';
  };

  const getStatusLabel = (status: string, statusText: string, statusTextHi?: string | null) => {
    if (language === 'hindi' && statusTextHi) return statusTextHi;
    if (language === 'english') {
      if (status === 'green') return 'Top Performer';
      if (status === 'yellow') return 'Average';
      return 'Needs Attention';
    }
    return statusText;
  };

  // Helper for SVG radar chart calculation
  const renderRadarChart = (metrics: BenchmarkMetric[]) => {
    const size = 260;
    const center = size / 2;
    const radius = 95;
    const count = metrics.length;
    const angleStep = (Math.PI * 2) / count;

    // Outer polygon points for radar grid levels
    const levels = [0.25, 0.5, 0.75, 1.0];

    // Calculate merchant points
    const youPoints = metrics
      .map((m, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const norm = Math.max(0.08, Math.min(1.0, m.percentile / 100));
        const x = center + radius * norm * Math.cos(angle);
        const y = center + radius * norm * Math.sin(angle);
        return `${x},${y}`;
      })
      .join(' ');

    // Baseline median (50th percentile) points
    const peerPoints = metrics
      .map((_, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const norm = 0.5;
        const x = center + radius * norm * Math.cos(angle);
        const y = center + radius * norm * Math.sin(angle);
        return `${x},${y}`;
      })
      .join(' ');

    return (
      <svg width={size} height={size} className="overflow-visible select-none">
        {/* Background Concentric Grid Rings */}
        {levels.map((lvl, idx) => (
          <circle
            key={idx}
            cx={center}
            cy={center}
            r={radius * lvl}
            fill="none"
            className="stroke-[#D0E5F7] dark:stroke-[#1E3A6E]"
            strokeWidth="1"
            strokeDasharray={lvl === 0.5 ? '3 3' : undefined}
          />
        ))}

        {/* Radial Axis Spokes */}
        {metrics.map((_, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const x = center + radius * Math.cos(angle);
          const y = center + radius * Math.sin(angle);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x}
              y2={y}
              className="stroke-[#D0E5F7] dark:stroke-[#1E3A6E]"
              strokeWidth="1"
            />
          );
        })}

        {/* Peer 50th Percentile Baseline */}
        <polygon
          points={peerPoints}
          fill="none"
          stroke="#00BAF2"
          strokeWidth="1.5"
          strokeDasharray="4 4"
        />

        {/* Merchant Polygon */}
        <polygon
          points={youPoints}
          fill="rgba(0, 186, 242, 0.28)"
          stroke="#00BAF2"
          strokeWidth="3"
        />

        {/* Data points & labels */}
        {metrics.map((m, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const norm = Math.max(0.08, Math.min(1.0, m.percentile / 100));
          const px = center + radius * norm * Math.cos(angle);
          const py = center + radius * norm * Math.sin(angle);

          // Label coordinates slightly beyond radius
          const lx = center + (radius + 26) * Math.cos(angle);
          const ly = center + (radius + 20) * Math.sin(angle);

          return (
            <g key={i}>
              <circle
                cx={px}
                cy={py}
                r="5"
                fill={m.status === 'green' ? '#00B970' : m.status === 'yellow' ? '#FFB800' : '#FF4D4D'}
                stroke="#FFFFFF"
                strokeWidth="2"
              />
              <text
                x={lx}
                y={ly}
                textAnchor="middle"
                dominantBaseline="central"
                className="text-[10px] font-bold fill-[#002970] dark:fill-white pointer-events-none"
              >
                {m.name === 'repeat_rate' ? 'Repeat' :
                 m.name === 'ticket_size' ? 'Ticket' :
                 m.name === 'failure_rate' ? 'Failures' :
                 m.name === 'refund_rate' ? 'Refunds' :
                 m.name === 'upi_share' ? 'UPI %' : 'Growth'}
              </text>
            </g>
          );
        })}
      </svg>
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      {/* Top Header & Merchant Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-[#0F1D38] p-5 rounded-2xl border border-[#CDE5F7] dark:border-[#1E3A6E] shadow-paytm transition-colors">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-[#E0F4FD] to-[#C9EDFC] dark:from-[#0B254A] dark:to-[#0F356B] text-[#00BAF2] border border-[#B3E3FA] dark:border-[#1A4B8C]">
              <Trophy className="w-6 h-6 text-[#00BAF2]" />
            </div>
            <div>
              <h2 className="text-xl lg:text-2xl font-black text-[#002970] dark:text-white tracking-tight">
                {t('compare_title', 'Peers se Tulna (Benchmark)')}
              </h2>
              <p className="text-xs text-[#4F6A94] dark:text-blue-200 mt-0.5 font-medium">
                {t('compare_subtitle', 'Compare your store against 6 core performance metrics of category peers')}
              </p>
            </div>
          </div>
        </div>

        {/* Demo Merchant Selector Dropdown */}
        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          <label className="text-xs font-bold text-[#002970] dark:text-blue-100 flex items-center gap-1.5 whitespace-nowrap">
            <Store className="w-3.5 h-3.5 text-[#00BAF2]" />
            <span>{t('select_shop', 'Select Shop:')}</span>
          </label>
          <select
            value={selectedMerchantId}
            onChange={(e) => setSelectedMerchantId(e.target.value)}
            className="text-xs font-bold bg-[#F0F8FE] dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E] rounded-xl px-3.5 py-2 text-[#002970] dark:text-white focus:outline-none focus:ring-2 focus:ring-[#00BAF2] transition-all shadow-2xs"
          >
            {merchants.map((m) => (
              <option key={m.merchant_id} value={m.merchant_id}>
                {m.merchant_id} - {m.business_type} ({m.city})
              </option>
            ))}
          </select>

          {/* WhatsApp Digest Modal Trigger */}
          <Button
            variant="success"
            size="sm"
            onClick={() => setIsWhatsAppModalOpen(true)}
            className="flex items-center gap-1.5 text-xs font-bold shadow-md"
            title="Preview WhatsApp Digest"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span className="hidden md:inline">WhatsApp Digest</span>
          </Button>
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={() => loadBenchmark(selectedMerchantId)} />}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : benchmark ? (
        <>
          {/* Small Peer Group Fallback Alert Notice */}
          {benchmark.is_fallback_group && benchmark.fallback_reason && (
            <div className="flex items-start gap-2.5 p-3.5 rounded-xl bg-[#FFF6E5] dark:bg-[#FFB800]/15 border border-[#FFE1A8] dark:border-[#FFB800]/30 text-xs text-[#C27803] dark:text-[#FFCA33] animate-in fade-in-50">
              <Info className="w-4 h-4 text-[#C27803] dark:text-[#FFCA33] shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Group Expansion: </span>
                <span>{benchmark.fallback_reason}</span>
              </div>
            </div>
          )}

          {/* Primary Scorecard Hero Banner with Paytm Navy Gradient */}
          <div className="bg-gradient-to-r from-[#002970] via-[#00388F] to-[#001D4E] rounded-2xl p-6 text-white shadow-soundbox border border-[#00BAF2]/30 relative overflow-hidden">
            <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-radial from-[#00BAF2]/25 to-transparent pointer-events-none" />

            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
              {/* Left Rank Callout */}
              <div className="space-y-3">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-white text-xs backdrop-blur-xs border border-white/15">
                  <Store className="w-3.5 h-3.5 text-[#00BAF2]" />
                  <span className="font-bold">{benchmark.peer_group}</span>
                  <span className="opacity-60">&bull;</span>
                  <span>{benchmark.peer_count} Verified Competitor Stores</span>
                </div>

                <div className="flex items-baseline gap-3">
                  <h1 className="text-3xl lg:text-4xl font-black tracking-tight text-white">
                    Rank #{benchmark.rank}
                    <span className="text-xl font-normal text-blue-200"> of {benchmark.peer_count}</span>
                  </h1>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider ${
                      benchmark.rank <= Math.ceil(benchmark.peer_count * 0.33)
                        ? 'bg-[#00B970] text-white shadow-xs'
                        : benchmark.rank <= Math.ceil(benchmark.peer_count * 0.66)
                        ? 'bg-[#FFB800] text-[#002970] shadow-xs'
                        : 'bg-[#FF4D4D] text-white shadow-xs'
                    }`}
                  >
                    {benchmark.rank <= Math.ceil(benchmark.peer_count * 0.33)
                      ? currentLanguage === 'hindi' ? 'शीर्ष 33%' : 'Top Performer'
                      : benchmark.rank <= Math.ceil(benchmark.peer_count * 0.66)
                      ? currentLanguage === 'hindi' ? 'मध्यम' : 'Average Performer'
                      : currentLanguage === 'hindi' ? 'सुधार आवश्यक' : 'Needs Push'}
                  </span>
                </div>

                <p className="text-sm text-blue-100 max-w-xl font-medium">
                  {currentLanguage === 'hindi'
                    ? `आप ${benchmark.city} व आस-पास के ${benchmark.business_type.toLowerCase()} व्यवसायों में #${benchmark.rank} स्थान पर हैं।`
                    : `Aap ${benchmark.peer_group} ke merchants mein ${benchmark.rank}th/${benchmark.peer_count} position par hain.`}
                </p>
              </div>

              {/* Right Overall Score Meter with Electric Cyan & Gold */}
              <div className="flex items-center gap-6 bg-white/10 rounded-2xl p-5 backdrop-blur-xs border border-white/20 self-start lg:self-auto shadow-md">
                <div className="text-center">
                  <span className="text-[11px] font-bold tracking-wider text-blue-200 uppercase block">
                    Overall Benchmark Score
                  </span>
                  <div className="flex items-baseline justify-center gap-1 mt-0.5">
                    <span className="text-4xl font-black text-[#00BAF2] tracking-tight">
                      {benchmark.overall_score}
                    </span>
                    <span className="text-blue-300 font-bold text-sm">/100</span>
                  </div>
                </div>

                <div className="h-10 w-px bg-white/20" />

                <div className="text-xs text-blue-100 space-y-1">
                  <div className="flex items-center gap-1.5 text-[#00B970] font-bold">
                    <CheckCircle2 className="w-4 h-4 text-[#00B970]" />
                    <span>6 Metrics Scored</span>
                  </div>
                  <p className="text-[11px] text-blue-200">
                    Updated live from Feature Store
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Main Grid: 6 Metric Tiles + Radar Visualization */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 6 Metric Tiles (2 Columns on Large Screens) */}
            <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
              {benchmark.metrics.map((metric) => {
                const badgeVariant = getStatusBadgeVariant(metric.status);
                const statusLabel = getStatusLabel(metric.status, metric.status_text, metric.status_text_hi);

                return (
                  <div
                    key={metric.name}
                    className="bg-white dark:bg-[#0F1D38] rounded-2xl p-5 border-2 border-[#CDE5F7] dark:border-[#1E3A6E] hover:shadow-paytm transition-all duration-200 flex flex-col justify-between"
                  >
                    <div>
                      {/* Title & Status Badge */}
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-xs font-bold text-[#4F6A94] dark:text-blue-200 uppercase tracking-wide">
                          {currentLanguage === 'hindi' && metric.label_hi ? metric.label_hi : metric.label}
                        </span>
                        <Badge variant={badgeVariant} className="text-[11px]">
                          {statusLabel}
                        </Badge>
                      </div>

                      {/* Metric Comparison Numbers */}
                      <div className="mt-3 flex items-baseline justify-between">
                        <div>
                          <span className="text-xs text-[#4F6A94] dark:text-blue-200 block font-semibold">Your Store</span>
                          <span className="text-2xl font-black text-[#002970] dark:text-white">
                            {metric.unit === '₹' ? `₹${Math.round(metric.you).toLocaleString('en-IN')}` : `${metric.you}${metric.unit}`}
                          </span>
                        </div>

                        <div className="text-right">
                          <span className="text-xs text-[#4F6A94] dark:text-blue-200 block font-semibold">Peer Median</span>
                          <span className="text-sm font-bold text-[#002970] dark:text-blue-100">
                            {metric.unit === '₹' ? `₹${Math.round(metric.peer_median).toLocaleString('en-IN')}` : `${metric.peer_median}${metric.unit}`}
                          </span>
                        </div>
                      </div>

                      {/* Visual Range Bar Component */}
                      <div className="mt-4 space-y-1.5">
                        <div className="flex justify-between text-[10px] text-[#4F6A94] dark:text-slate-400 font-semibold">
                          <span>Min: {metric.peer_min}{metric.unit}</span>
                          <span className="text-[#002970] dark:text-white font-bold">50th %ile (Median)</span>
                          <span>Max: {metric.peer_max}{metric.unit}</span>
                        </div>
                        <div className="h-2.5 w-full bg-[#E8F4FD] dark:bg-[#132342] rounded-full relative overflow-hidden">
                          {/* Percentile fill */}
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              metric.status === 'green' ? 'bg-[#00B970]' :
                              metric.status === 'yellow' ? 'bg-[#FFB800]' : 'bg-[#FF4D4D]'
                            }`}
                            style={{ width: `${metric.percentile}%` }}
                          />
                        </div>
                        <div className="text-right text-[10px] font-bold text-[#00BAF2]">
                          {metric.percentile}th Percentile Rank
                        </div>
                      </div>
                    </div>

                    {/* Actionable Tip & Explain Button */}
                    <div className="mt-4 pt-3 border-t border-[#E8F4FD] dark:border-[#1E3A6E] flex items-center justify-between text-xs">
                      <p className="text-[11px] text-[#0F2042] dark:text-blue-100 font-semibold line-clamp-1 flex-1 pr-2" title={metric.action}>
                        💡 {currentLanguage === 'hindi' && metric.action_hi ? metric.action_hi : metric.action}
                      </p>
                      <button
                        onClick={() => {
                          setSelectedExplainMetric(metric);
                          setIsExplainModalOpen(true);
                        }}
                        className="text-[11px] font-bold text-[#00BAF2] hover:text-[#002970] dark:hover:text-white whitespace-nowrap flex items-center gap-0.5 transition-colors"
                      >
                        <span>Kaise?</span>
                        <ChevronRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Radar / Spider Chart Panel */}
            <div className="bg-white dark:bg-[#0F1D38] rounded-2xl p-5 border-2 border-[#CDE5F7] dark:border-[#1E3A6E] shadow-paytm flex flex-col justify-between transition-colors">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-extrabold text-[#002970] dark:text-white flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-[#00BAF2]" />
                    <span>Benchmark Spider Chart</span>
                  </h3>
                  <Badge variant="demo" className="text-[10px]">
                    Relative Score
                  </Badge>
                </div>

                {/* SVG Radar Chart */}
                <div className="py-2 flex justify-center">
                  {renderRadarChart(benchmark.metrics)}
                </div>

                <div className="mt-3 flex items-center justify-center gap-4 text-xs text-[#4F6A94] dark:text-blue-200 font-semibold">
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-2 rounded-sm bg-[#00BAF2]" />
                    <span>Your Store</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 border-t-2 border-dashed border-[#00BAF2]" />
                    <span>Peer Median (50%)</span>
                  </div>
                </div>
              </div>

              {/* Quick AI Ask CTA */}
              <div className="mt-6 p-3.5 rounded-xl bg-[#F0F8FE] dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E] text-xs space-y-2">
                <p className="font-bold text-[#002970] dark:text-white">
                  💬 Want an audio or Hindi explanation?
                </p>
                <Button
                  variant="primary"
                  size="sm"
                  className="w-full text-xs font-bold"
                  onClick={() => onQuickCopilot && onQuickCopilot('Meri dukaan dusron se kaisi hai?')}
                >
                  Ask Copilot: "Meri dukaan dusron se kaisi hai?"
                </Button>
              </div>
            </div>
          </div>

          {/* What Top Performers Do Panel */}
          <div className="bg-white dark:bg-[#0F1D38] rounded-2xl p-6 border-2 border-[#CDE5F7] dark:border-[#1E3A6E] shadow-paytm transition-colors">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-xl bg-[#E8F8F0] dark:bg-[#00B970]/20 text-[#008A54] dark:text-[#00E68A] border border-[#B6E8D0] dark:border-[#00B970]/30">
                <ShieldCheck className="w-5 h-5 text-[#00B970]" />
              </div>
              <div>
                <h3 className="text-base font-extrabold text-[#002970] dark:text-white">
                  {currentLanguage === 'hindi'
                    ? `शीर्ष 10% ${benchmark.business_type} विक्रेता क्या करते हैं?`
                    : `What Top 10% ${benchmark.business_type} Performers Do`}
                </h3>
                <p className="text-xs text-[#4F6A94] dark:text-blue-200 font-medium">
                  Category leaders ke high-impact business practices aur strategies
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {benchmark.top_performer_practices.map((practice, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 p-3.5 rounded-xl bg-[#F0F8FE] dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E] text-xs text-[#0F2042] dark:text-blue-100 font-semibold"
                >
                  <div className="w-6 h-6 rounded-full bg-[#00B970] text-white flex items-center justify-center font-black text-xs shrink-0 mt-0.5 shadow-2xs">
                    {idx + 1}
                  </div>
                  <span className="leading-relaxed">{practice}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : null}

      {/* "Kaise Pata Chala?" (Calculation Explanation Modal) */}
      <Modal
        isOpen={isExplainModalOpen}
        onClose={() => setIsExplainModalOpen(false)}
        title={
          selectedExplainMetric
            ? `Kaise Pata Chala: ${selectedExplainMetric.label}`
            : 'Calculation Explanation'
        }
      >
        {selectedExplainMetric && benchmark && (
          <div className="space-y-4 text-sm text-[#002970] dark:text-white">
            <p className="text-xs text-[#4F6A94] dark:text-blue-200 leading-relaxed">
              VyaparMitra peer benchmarking transparently computes percentiles by comparing your store against{' '}
              <strong className="text-[#002970] dark:text-white font-bold">{benchmark.peer_count} verified stores</strong> in{' '}
              <strong className="text-[#002970] dark:text-white font-bold">{benchmark.peer_group}</strong>.
            </p>

            {/* Formula & Calculation Box */}
            <div className="rounded-xl bg-[#F0F8FE] dark:bg-[#132342] p-4 border border-[#CDE5F7] dark:border-[#1E3A6E] space-y-2 text-xs">
              <span className="font-extrabold text-[#002970] dark:text-white uppercase tracking-wide block">
                Calculation Breakdown
              </span>
              <div className="grid grid-cols-2 gap-2 text-[#4F6A94] dark:text-blue-200 font-medium">
                <div>Your Store Value:</div>
                <div className="font-extrabold text-[#002970] dark:text-white">
                  {selectedExplainMetric.you} {selectedExplainMetric.unit}
                </div>
                <div>Peer Group Median:</div>
                <div className="font-bold text-[#002970] dark:text-white">
                  {selectedExplainMetric.peer_median} {selectedExplainMetric.unit}
                </div>
                <div>Peer Minimum:</div>
                <div>{selectedExplainMetric.peer_min} {selectedExplainMetric.unit}</div>
                <div>Peer Maximum:</div>
                <div>{selectedExplainMetric.peer_max} {selectedExplainMetric.unit}</div>
                <div>Percentile Standing:</div>
                <div className="font-extrabold text-[#00BAF2]">
                  {selectedExplainMetric.percentile}th percentile
                </div>
              </div>
            </div>

            <div className="rounded-xl bg-[#E8F8F0] dark:bg-[#00B970]/15 p-3.5 border border-[#B6E8D0] dark:border-[#00B970]/30 text-xs text-[#008A54] dark:text-[#00E68A] space-y-1">
              <span className="font-bold block">Actionable Guidance:</span>
              <p className="font-medium">{selectedExplainMetric.action}</p>
            </div>

            <div className="flex justify-end pt-2">
              <Button variant="navy" onClick={() => setIsExplainModalOpen(false)}>
                Samajh gaya (Close)
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* WhatsApp Digest Preview & Twilio Send Modal */}
      <Modal
        isOpen={isWhatsAppModalOpen}
        onClose={() => {
          setIsWhatsAppModalOpen(false);
          setWhatsAppStatusMsg(null);
        }}
        title="WhatsApp Weekly Digest & Twilio Sender"
        maxWidth="xl"
      >
        {benchmark && (
          <div className="space-y-4 text-sm text-[#002970] dark:text-white">
            {/* Twilio Quick Sender Card */}
            <div className="p-4 rounded-xl bg-[#F0F8FE] dark:bg-[#132342] border-2 border-[#CDE5F7] dark:border-[#1E3A6E] space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold text-[#002970] dark:text-white flex items-center gap-1.5">
                  <Phone className="w-4 h-4 text-[#00BAF2]" />
                  <span>Send Directly via Twilio WhatsApp</span>
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-[#00B970] text-white">
                  Twilio Configured
                </span>
              </div>

              <div className="flex flex-col sm:flex-row gap-2">
                <input
                  type="text"
                  value={whatsAppPhone}
                  onChange={(e) => setWhatsAppPhone(e.target.value)}
                  placeholder="+919876543210"
                  className="flex-1 px-3.5 py-2 text-xs rounded-xl border border-[#CDE5F7] dark:border-[#1E3A6E] bg-white dark:bg-[#0B1528] text-[#002970] dark:text-white focus:outline-none focus:ring-2 focus:ring-[#00BAF2] font-semibold"
                />
                <Button
                  variant="success"
                  size="sm"
                  onClick={handleSendWhatsApp}
                  disabled={sendingWhatsApp || !whatsAppPhone.trim()}
                  className="flex items-center gap-1.5 font-bold shrink-0"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{sendingWhatsApp ? 'Sending...' : 'Send WhatsApp'}</span>
                </Button>
              </div>

              {whatsAppStatusMsg && (
                <div
                  className={`p-3 rounded-xl text-xs font-semibold leading-relaxed border ${
                    whatsAppStatusType === 'success'
                      ? 'bg-[#E8F8F0] text-[#008A54] border-[#B6E8D0]'
                      : whatsAppStatusType === 'info'
                      ? 'bg-[#E8F4FD] text-[#002970] dark:text-blue-200 border-[#B3DCF8] dark:border-[#1E3A6E]'
                      : 'bg-[#FEECEB] text-[#D92D20] border-[#FECDCA]'
                  }`}
                >
                  {whatsAppStatusMsg}
                </div>
              )}
            </div>

            <p className="text-xs text-[#4F6A94] dark:text-blue-200 font-medium">
              Aapka weekly benchmark digest preview:
            </p>

            <pre className="p-4 rounded-xl bg-slate-900 text-[#00B970] text-xs font-mono whitespace-pre-wrap leading-relaxed overflow-x-auto max-h-60 border border-slate-800">
              {benchmark.whatsapp_digest}
            </pre>

            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-[#4F6A94] dark:text-blue-200 font-semibold">
                {copiedWhatsApp ? '✅ Copied to clipboard!' : 'Or copy raw text for manual sharing'}
              </span>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  onClick={() => {
                    setIsWhatsAppModalOpen(false);
                    setWhatsAppStatusMsg(null);
                  }}
                  className="dark:bg-[#132342] dark:border-[#1E3A6E] dark:text-white"
                >
                  Close
                </Button>
                <Button variant="outline" onClick={handleCopyWhatsApp} className="flex items-center gap-1.5 font-bold dark:border-[#00BAF2] dark:text-[#00BAF2]">
                  {copiedWhatsApp ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  <span>{copiedWhatsApp ? 'Copied!' : 'Copy Text'}</span>
                </Button>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
