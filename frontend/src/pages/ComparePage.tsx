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
} from 'lucide-react';
import { api } from '../api/client';
import { BenchmarkData, BenchmarkMetric, MerchantInfo } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Modal } from '../components/Modal';
import { CardSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner } from '../components/EmptyState';

interface ComparePageProps {
  currentLanguage?: string;
  onNavigateTab?: (tab: string) => void;
  onQuickCopilot?: (query: string) => void;
}

export const ComparePage: React.FC<ComparePageProps> = ({
  currentLanguage = 'hinglish',
  onNavigateTab,
  onQuickCopilot,
}) => {
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

  const getStatusBadgeVariant = (status: string): 'success' | 'high' | 'critical' => {
    if (status === 'green') return 'success';
    if (status === 'yellow') return 'high';
    return 'critical';
  };

  const getStatusLabel = (status: string, statusText: string, statusTextHi?: string | null) => {
    if (currentLanguage === 'hindi' && statusTextHi) return statusTextHi;
    if (currentLanguage === 'english') {
      if (status === 'green') return 'Top Performer';
      if (status === 'yellow') return 'Average';
      return 'Needs Attention';
    }
    return statusText; // Hinglish: Achha, Ausat, Sudhar sakte hain
  };

  // Helper for Radar Chart SVG vertices
  const renderRadarChart = (metrics: BenchmarkMetric[]) => {
    const size = 260;
    const center = size / 2;
    const radius = 90;
    const count = metrics.length;
    if (count === 0) return null;

    // Angle per point
    const angleStep = (Math.PI * 2) / count;

    // Background concentric rings (25%, 50%, 75%, 100%)
    const rings = [0.25, 0.5, 0.75, 1.0];

    // Compute vertices for 50% baseline (peer median)
    const peerPoints = metrics
      .map((_, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const r = radius * 0.5;
        return `${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`;
      })
      .join(' ');

    // Compute vertices for merchant percentiles
    const youPoints = metrics
      .map((m, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const norm = Math.max(0.1, Math.min(1.0, m.percentile / 100));
        const r = radius * norm;
        return `${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`;
      })
      .join(' ');

    return (
      <svg width={size} height={size} className="mx-auto overflow-visible select-none">
        {/* Concentric grid polygons */}
        {rings.map((ring, idx) => {
          const ringPoints = metrics
            .map((_, i) => {
              const angle = i * angleStep - Math.PI / 2;
              const r = radius * ring;
              return `${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`;
            })
            .join(' ');
          return (
            <polygon
              key={idx}
              points={ringPoints}
              fill="none"
              stroke="#E2E8F0"
              strokeWidth="1"
              strokeDasharray={idx === 1 ? '3 3' : undefined}
            />
          );
        })}

        {/* Axis Spokes */}
        {metrics.map((_, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const x2 = center + radius * Math.cos(angle);
          const y2 = center + radius * Math.sin(angle);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x2}
              y2={y2}
              stroke="#CBD5E1"
              strokeWidth="1"
            />
          );
        })}

        {/* Peer Median Baseline (50th percentile) */}
        <polygon
          points={peerPoints}
          fill="none"
          stroke="#94A3B8"
          strokeWidth="1.5"
          strokeDasharray="4 4"
        />

        {/* Merchant Polygon */}
        <polygon
          points={youPoints}
          fill="rgba(0, 186, 242, 0.25)"
          stroke="#00BAF2"
          strokeWidth="2.5"
        />

        {/* Data points & labels */}
        {metrics.map((m, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const norm = Math.max(0.1, Math.min(1.0, m.percentile / 100));
          const px = center + radius * norm * Math.cos(angle);
          const py = center + radius * norm * Math.sin(angle);

          // Label coordinates slightly beyond radius
          const lx = center + (radius + 24) * Math.cos(angle);
          const ly = center + (radius + 18) * Math.sin(angle);

          return (
            <g key={i}>
              <circle
                cx={px}
                cy={py}
                r="4"
                fill={m.status === 'green' ? '#00A859' : m.status === 'yellow' ? '#F59E0B' : '#EF4444'}
                stroke="#FFFFFF"
                strokeWidth="1.5"
              />
              <text
                x={lx}
                y={ly}
                textAnchor="middle"
                dominantBaseline="central"
                className="text-[10px] font-semibold fill-slate-700 pointer-events-none"
              >
                {m.name === 'repeat_rate' ? 'Repeat' :
                 m.name === 'ticket_size' ? 'Bill Size' :
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-paytm-border shadow-xs">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-paytm-light text-paytm-blue border border-paytm-border">
              <Trophy className="w-5 h-5 text-paytm-blue" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-paytm-dark tracking-tight">
                {currentLanguage === 'hindi' ? 'दुकान की प्रतिस्पर्धा से तुलना (Benchmark)' : 'Peers se Tulna (Benchmark)'}
              </h2>
              <p className="text-xs text-paytm-muted mt-0.5">
                {currentLanguage === 'hindi'
                  ? 'समान शहर व श्रेणी की अन्य दुकानों से 6 मुख्य संकेतकों पर तुलना'
                  : 'Compare your store against 6 core performance metrics of category peers'}
              </p>
            </div>
          </div>
        </div>

        {/* Demo Merchant Selector Dropdown */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <label className="text-xs font-semibold text-paytm-dark flex items-center gap-1.5 whitespace-nowrap">
            <Store className="w-3.5 h-3.5 text-paytm-blue" />
            <span>Select Shop:</span>
          </label>
          <select
            value={selectedMerchantId}
            onChange={(e) => setSelectedMerchantId(e.target.value)}
            className="text-xs font-medium bg-slate-50 border border-paytm-border rounded-lg px-3 py-2 text-paytm-dark focus:outline-hidden focus:ring-2 focus:ring-paytm-blue/20 focus:border-paytm-blue transition-all"
          >
            {merchants.map((m) => (
              <option key={m.merchant_id} value={m.merchant_id}>
                {m.merchant_id} - {m.business_type} ({m.city})
              </option>
            ))}
          </select>

          {/* WhatsApp Digest Modal Trigger */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsWhatsAppModalOpen(true)}
            className="flex items-center gap-1.5 text-xs text-emerald-700 border-emerald-300 hover:bg-emerald-50"
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
            <div className="flex items-start gap-2.5 p-3.5 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-900 animate-in fade-in-50">
              <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Group Expansion: </span>
                <span>{benchmark.fallback_reason}</span>
              </div>
            </div>
          )}

          {/* Primary Scorecard Hero Banner */}
          <div className="bg-gradient-to-br from-paytm-dark via-slate-900 to-paytm-dark rounded-2xl p-6 text-white shadow-md relative overflow-hidden">
            <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-radial from-paytm-blue/20 to-transparent pointer-events-none" />

            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
              {/* Left Rank Callout */}
              <div className="space-y-3">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-white/90 text-xs backdrop-blur-xs">
                  <Store className="w-3.5 h-3.5 text-paytm-blue" />
                  <span className="font-semibold">{benchmark.peer_group}</span>
                  <span className="opacity-60">&bull;</span>
                  <span>{benchmark.peer_count} Verified Peers</span>
                </div>

                <div className="flex items-baseline gap-3">
                  <h1 className="text-3xl lg:text-4xl font-extrabold tracking-tight">
                    Rank #{benchmark.rank}
                    <span className="text-xl font-normal text-white/70"> of {benchmark.peer_count}</span>
                  </h1>
                  <Badge
                    variant={
                      benchmark.rank <= Math.ceil(benchmark.peer_count * 0.33)
                        ? 'success'
                        : benchmark.rank <= Math.ceil(benchmark.peer_count * 0.66)
                        ? 'high'
                        : 'critical'
                    }
                    className="text-xs px-2.5 py-1"
                  >
                    {benchmark.rank <= Math.ceil(benchmark.peer_count * 0.33)
                      ? currentLanguage === 'hindi' ? 'शीर्ष 33%' : 'Top Performer'
                      : benchmark.rank <= Math.ceil(benchmark.peer_count * 0.66)
                      ? currentLanguage === 'hindi' ? 'मध्यम' : 'Average Performer'
                      : currentLanguage === 'hindi' ? 'सुधार आवश्यक' : 'Needs Push'}
                  </Badge>
                </div>

                <p className="text-sm text-slate-300 max-w-xl">
                  {currentLanguage === 'hindi'
                    ? `आप ${benchmark.city} व आस-पास के ${benchmark.business_type.toLowerCase()} व्यवसायों में #${benchmark.rank} स्थान पर हैं।`
                    : `Aap ${benchmark.peer_group} ke merchants mein ${benchmark.rank}th/${benchmark.peer_count} position par hain.`}
                </p>
              </div>

              {/* Right Overall Score Meter */}
              <div className="flex items-center gap-6 bg-white/10 rounded-xl p-4 lg:p-5 backdrop-blur-xs border border-white/10 self-start lg:self-auto">
                <div className="text-center">
                  <span className="text-[11px] font-medium tracking-wider text-slate-300 uppercase block">
                    Overall Benchmark
                  </span>
                  <div className="flex items-baseline justify-center gap-1 mt-0.5">
                    <span className="text-4xl font-extrabold text-paytm-blue tracking-tight">
                      {benchmark.overall_score}
                    </span>
                    <span className="text-slate-400 font-bold text-sm">/100</span>
                  </div>
                </div>

                <div className="h-10 w-px bg-white/20" />

                <div className="text-xs text-slate-200 space-y-1">
                  <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>6 Metrics Scored</span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Updated with live feature store
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
                    className="bg-white rounded-xl p-5 border border-paytm-border hover:shadow-sm transition-all flex flex-col justify-between"
                  >
                    <div>
                      {/* Title & Status Badge */}
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-xs font-semibold text-paytm-muted uppercase tracking-wide">
                          {currentLanguage === 'hindi' && metric.label_hi ? metric.label_hi : metric.label}
                        </span>
                        <Badge variant={badgeVariant} className="text-[11px]">
                          {statusLabel}
                        </Badge>
                      </div>

                      {/* Metric Comparison Numbers */}
                      <div className="mt-3 flex items-baseline justify-between">
                        <div>
                          <span className="text-xs text-slate-400 block">You</span>
                          <span className="text-2xl font-extrabold text-paytm-dark">
                            {metric.unit === '₹' ? `₹${Math.round(metric.you).toLocaleString('en-IN')}` : `${metric.you}${metric.unit}`}
                          </span>
                        </div>

                        <div className="text-right">
                          <span className="text-xs text-slate-400 block">Peer Median</span>
                          <span className="text-sm font-bold text-slate-700">
                            {metric.unit === '₹' ? `₹${Math.round(metric.peer_median).toLocaleString('en-IN')}` : `${metric.peer_median}${metric.unit}`}
                          </span>
                        </div>
                      </div>

                      {/* Visual Range Bar Component */}
                      <div className="mt-4 space-y-1">
                        <div className="flex justify-between text-[10px] text-slate-400">
                          <span>Min: {metric.peer_min}{metric.unit}</span>
                          <span className="font-semibold text-slate-600">50th %ile (Median)</span>
                          <span>Max: {metric.peer_max}{metric.unit}</span>
                        </div>
                        <div className="h-2 w-full bg-slate-100 rounded-full relative overflow-hidden">
                          {/* Percentile fill */}
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              metric.status === 'green' ? 'bg-emerald-500' :
                              metric.status === 'yellow' ? 'bg-amber-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${metric.percentile}%` }}
                          />
                        </div>
                        <div className="text-right text-[10px] font-semibold text-paytm-muted">
                          {metric.percentile}th Percentile
                        </div>
                      </div>
                    </div>

                    {/* Actionable Tip & Explain Button */}
                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                      <p className="text-[11px] text-slate-600 font-medium line-clamp-1 flex-1 pr-2" title={metric.action}>
                        💡 {currentLanguage === 'hindi' && metric.action_hi ? metric.action_hi : metric.action}
                      </p>
                      <button
                        onClick={() => {
                          setSelectedExplainMetric(metric);
                          setIsExplainModalOpen(true);
                        }}
                        className="text-[11px] font-semibold text-paytm-blue hover:underline whitespace-nowrap flex items-center gap-0.5"
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
            <div className="bg-white rounded-xl p-5 border border-paytm-border flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-paytm-dark flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-paytm-blue" />
                    <span>Benchmark Spider Chart</span>
                  </h3>
                  <Badge variant="neutral" className="text-[10px]">
                    Relative Score
                  </Badge>
                </div>

                {/* SVG Radar Chart */}
                <div className="py-2 flex justify-center">
                  {renderRadarChart(benchmark.metrics)}
                </div>

                <div className="mt-3 flex items-center justify-center gap-4 text-xs text-paytm-muted">
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-1.5 rounded-sm bg-paytm-blue" />
                    <span>Your Store</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 border-t border-dashed border-slate-400" />
                    <span>Peer Median (50%)</span>
                  </div>
                </div>
              </div>

              {/* Quick AI Ask CTA */}
              <div className="mt-6 p-3 rounded-lg bg-paytm-light border border-paytm-border text-xs space-y-2">
                <p className="font-semibold text-paytm-dark">
                  💬 Want an audio or Hindi explanation?
                </p>
                <Button
                  variant="primary"
                  size="sm"
                  className="w-full text-xs"
                  onClick={() => onQuickCopilot && onQuickCopilot('Meri dukaan dusron se kaisi hai?')}
                >
                  Ask Copilot: "Meri dukaan dusron se kaisi hai?"
                </Button>
              </div>
            </div>
          </div>

          {/* What Top Performers Do Panel */}
          <div className="bg-white rounded-xl p-6 border border-paytm-border shadow-xs">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-1.5 rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-200">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
              </div>
              <div>
                <h3 className="text-base font-bold text-paytm-dark">
                  {currentLanguage === 'hindi'
                    ? `शीर्ष 10% ${benchmark.business_type} विक्रेता क्या करते हैं?`
                    : `What Top 10% ${benchmark.business_type} Performers Do`}
                </h3>
                <p className="text-xs text-paytm-muted">
                  Data-backed operational strategies observed among category leaders
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {benchmark.top_performer_practices.map((practice, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 p-3.5 rounded-lg bg-slate-50 border border-slate-200/80 text-xs text-slate-700"
                >
                  <div className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
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
          <div className="space-y-4 text-sm text-paytm-dark">
            <p className="text-xs text-paytm-muted leading-relaxed">
              VyaparMitra peer benchmarking transparently computes percentiles by comparing your store against{' '}
              <strong className="text-paytm-dark">{benchmark.peer_count} verified stores</strong> in{' '}
              <strong className="text-paytm-dark">{benchmark.peer_group}</strong>.
            </p>

            {/* Formula & Calculation Box */}
            <div className="rounded-lg bg-slate-50 p-4 border border-slate-200 space-y-2 text-xs">
              <span className="font-bold text-slate-700 uppercase tracking-wide block">
                Calculation Breakdown
              </span>
              <div className="grid grid-cols-2 gap-2 text-slate-600">
                <div>Your Store Value:</div>
                <div className="font-bold text-paytm-dark">
                  {selectedExplainMetric.you} {selectedExplainMetric.unit}
                </div>
                <div>Peer Group Median:</div>
                <div className="font-bold text-slate-700">
                  {selectedExplainMetric.peer_median} {selectedExplainMetric.unit}
                </div>
                <div>Peer Minimum:</div>
                <div>{selectedExplainMetric.peer_min} {selectedExplainMetric.unit}</div>
                <div>Peer Maximum:</div>
                <div>{selectedExplainMetric.peer_max} {selectedExplainMetric.unit}</div>
                <div>Percentile Standing:</div>
                <div className="font-bold text-paytm-blue">
                  {selectedExplainMetric.percentile}th percentile
                </div>
              </div>
            </div>

            <div className="rounded-lg bg-paytm-light p-3.5 border border-paytm-border text-xs text-slate-700 space-y-1">
              <span className="font-semibold text-paytm-blue block">Actionable Guidance:</span>
              <p>{selectedExplainMetric.action}</p>
            </div>

            <div className="flex justify-end pt-2">
              <Button variant="secondary" onClick={() => setIsExplainModalOpen(false)}>
                Samajh gaya (Close)
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* WhatsApp Digest Preview Modal */}
      <Modal
        isOpen={isWhatsAppModalOpen}
        onClose={() => setIsWhatsAppModalOpen(false)}
        title="WhatsApp Weekly Digest Preview"
      >
        {benchmark && (
          <div className="space-y-4 text-sm text-paytm-dark">
            <p className="text-xs text-paytm-muted">
              Copy and share this digest with your shop team or partners:
            </p>

            <pre className="p-4 rounded-xl bg-slate-900 text-emerald-400 text-xs font-mono whitespace-pre-wrap leading-relaxed overflow-x-auto max-h-72 border border-slate-800">
              {benchmark.whatsapp_digest}
            </pre>

            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-slate-500">
                {copiedWhatsApp ? '✅ Copied to clipboard!' : 'Ready to paste into WhatsApp'}
              </span>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setIsWhatsAppModalOpen(false)}>
                  Cancel
                </Button>
                <Button variant="primary" onClick={handleCopyWhatsApp} className="flex items-center gap-1.5">
                  {copiedWhatsApp ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  <span>{copiedWhatsApp ? 'Copied!' : 'Copy Digest'}</span>
                </Button>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
