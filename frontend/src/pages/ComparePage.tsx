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
import { BenchmarkData, BenchmarkMetric, MerchantInfo, UserProfile } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { PageHeader } from '../components/PageHeader';
import { SectionHeader } from '../components/SectionHeader';
import { Modal } from '../components/Modal';
import { CardSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner } from '../components/EmptyState';
import { useLanguage } from '../i18n/LanguageContext';

interface ComparePageProps {
  onNavigateTab?: (tab: string) => void;
  onQuickCopilot?: (query: string) => void;
  currentUser?: UserProfile | null;
}

export const ComparePage: React.FC<ComparePageProps> = ({
  onNavigateTab,
  onQuickCopilot,
  currentUser,
}) => {
  const { t, language, language: currentLanguage } = useLanguage();
  const [merchants, setMerchants] = useState<MerchantInfo[]>([]);
  const [selectedMerchantId, setSelectedMerchantId] = useState<string>(() => {
    return currentUser?.merchant_id || currentUser?.business_id || 'M001';
  });
  const [benchmark, setBenchmark] = useState<BenchmarkData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Modals state
  const [isExplainModalOpen, setIsExplainModalOpen] = useState<boolean>(false);
  const [selectedExplainMetric, setSelectedExplainMetric] = useState<BenchmarkMetric | null>(null);
  const [isWhatsAppModalOpen, setIsWhatsAppModalOpen] = useState<boolean>(false);
  const [copiedWhatsApp, setCopiedWhatsApp] = useState<boolean>(false);

  // Twilio WhatsApp delivery state
  const [whatsAppPhone, setWhatsAppPhone] = useState<string>(() => {
    return currentUser?.phone || '';
  });
  const [sendingWhatsApp, setSendingWhatsApp] = useState<boolean>(false);
  const [whatsAppStatusMsg, setWhatsAppStatusMsg] = useState<string | null>(null);
  const [whatsAppStatusType, setWhatsAppStatusType] = useState<'success' | 'info' | 'error' | null>(null);

  // Load merchants list on mount
  useEffect(() => {
    const loadMerchantsList = async () => {
      try {
        const res = await api.getMerchants();
        const list = res.merchants || [];
        setMerchants(list);
        if (list.length > 0 && !currentUser?.merchant_id) {
          setSelectedMerchantId(list[0].merchant_id);
        }
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
      const res = await api.sendWhatsAppDigest(selectedMerchantId, whatsAppPhone.trim());
      if (res.status === 'sent') {
        setWhatsAppStatusType('success');
        setWhatsAppStatusMsg(
          currentLanguage === 'hindi'
            ? `व्हाट्सएप संदेश सफलतापूर्वक भेजा गया (SID: ${res.message_sid || 'OK'})`
            : `WhatsApp benchmark report sent! (SID: ${res.message_sid || 'OK'})`
        );
      } else if (res.status === 'simulated' || res.status === 'preview_only') {
        setWhatsAppStatusType('info');
        setWhatsAppStatusMsg(
          currentLanguage === 'hindi'
            ? 'डेमो मोड: संदेश तैयार है (लाइव Twilio API सक्रिय नहीं है)'
            : 'Demo mode: Digest generated (Live Twilio provider unconfigured)'
        );
      }
    } catch (err: any) {
      setWhatsAppStatusType('error');
      setWhatsAppStatusMsg(err?.message || 'Failed to send WhatsApp message');
    } finally {
      setSendingWhatsApp(false);
    }
  };

  const getStatusBadgeVariant = (status: string): 'success' | 'warning' | 'danger' => {
    if (status === 'green') return 'success';
    if (status === 'yellow') return 'warning';
    return 'danger';
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
    const levels = [0.25, 0.5, 0.75, 1.0];

    const youPoints = metrics
      .map((m, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const norm = Math.max(0.08, Math.min(1.0, m.percentile / 100));
        const x = center + radius * norm * Math.cos(angle);
        const y = center + radius * norm * Math.sin(angle);
        return `${x},${y}`;
      })
      .join(' ');

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
        {levels.map((lvl, idx) => (
          <circle
            key={idx}
            cx={center}
            cy={center}
            r={radius * lvl}
            fill="none"
            className="stroke-border"
            strokeWidth="1"
            strokeDasharray={lvl === 0.5 ? '3 3' : undefined}
          />
        ))}

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
              className="stroke-border"
              strokeWidth="1"
            />
          );
        })}

        <polygon
          points={peerPoints}
          fill="none"
          stroke="rgb(var(--brand))"
          strokeWidth="1.5"
          strokeDasharray="4 4"
        />

        <polygon
          points={youPoints}
          fill="rgba(var(--brand), 0.2)"
          stroke="rgb(var(--brand))"
          strokeWidth="2.5"
        />

        {metrics.map((m, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const norm = Math.max(0.08, Math.min(1.0, m.percentile / 100));
          const px = center + radius * norm * Math.cos(angle);
          const py = center + radius * norm * Math.sin(angle);

          const lx = center + (radius + 26) * Math.cos(angle);
          const ly = center + (radius + 20) * Math.sin(angle);

          return (
            <g key={i}>
              <circle
                cx={px}
                cy={py}
                r="4.5"
                fill={m.status === 'green' ? '#10B981' : m.status === 'yellow' ? '#F59E0B' : '#EF4444'}
                stroke="#FFFFFF"
                strokeWidth="2"
              />
              <text
                x={lx}
                y={ly}
                textAnchor="middle"
                dominantBaseline="central"
                className="text-[10px] font-bold fill-text pointer-events-none"
              >
                {m.name === 'repeat_rate'
                  ? 'Repeat'
                  : m.name === 'ticket_size'
                  ? 'Ticket'
                  : m.name === 'failure_rate'
                  ? 'Failures'
                  : m.name === 'refund_rate'
                  ? 'Refunds'
                  : m.name === 'upi_share'
                  ? 'UPI %'
                  : 'Growth'}
              </text>
            </g>
          );
        })}
      </svg>
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      <PageHeader
        title={t('compare_title', 'Peers se Tulna (Peer Benchmark)')}
        subtitle={t('compare_subtitle', 'Benchmark store metrics against category competitors in your retail geography.')}
        actions={
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5">
              <Store className="w-3.5 h-3.5 text-brand shrink-0" />
              <select
                value={selectedMerchantId}
                onChange={(e) => setSelectedMerchantId(e.target.value)}
                className="text-xs font-semibold bg-surface border border-border rounded-xl px-3 py-1.5 text-text focus:outline-none focus:ring-2 focus:ring-brand shadow-2xs"
              >
                {merchants.map((m) => (
                  <option key={m.merchant_id} value={m.merchant_id}>
                    {m.merchant_id} - {m.business_type} ({m.city})
                  </option>
                ))}
              </select>
            </div>

            <Button
              variant="secondary"
              size="sm"
              onClick={() => setIsWhatsAppModalOpen(true)}
              className="gap-1.5 text-xs font-semibold"
            >
              <Share2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">WhatsApp Digest</span>
            </Button>
          </div>
        }
      />

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
            <div className="flex items-start gap-2.5 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-700 dark:text-amber-300">
              <Info className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Group Expansion: </span>
                <span>{benchmark.fallback_reason}</span>
              </div>
            </div>
          )}

          {/* Primary Scorecard Hero Banner */}
          <div className="bg-gradient-to-r from-brand to-brand-hover rounded-2xl p-6 text-brand-contrast shadow-fintech border border-border/40 relative overflow-hidden">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
              <div className="space-y-3">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 text-xs backdrop-blur-xs border border-white/20">
                  <Store className="w-3.5 h-3.5" />
                  <span className="font-bold">{benchmark.peer_group}</span>
                  <span className="opacity-60">&bull;</span>
                  <span>{benchmark.peer_count} Verified Competitor Stores</span>
                </div>

                <div className="flex items-baseline gap-3">
                  <h1 className="text-3xl lg:text-4xl font-extrabold tracking-tight">
                    Rank #{benchmark.rank}
                    <span className="text-xl font-normal opacity-80"> of {benchmark.peer_count}</span>
                  </h1>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                      benchmark.rank <= Math.ceil(benchmark.peer_count * 0.33)
                        ? 'bg-emerald-500 text-white'
                        : benchmark.rank <= Math.ceil(benchmark.peer_count * 0.66)
                        ? 'bg-amber-400 text-slate-900'
                        : 'bg-rose-500 text-white'
                    }`}
                  >
                    {benchmark.rank <= Math.ceil(benchmark.peer_count * 0.33)
                      ? currentLanguage === 'hindi'
                        ? 'शीर्ष 33%'
                        : 'Top Performer'
                      : benchmark.rank <= Math.ceil(benchmark.peer_count * 0.66)
                      ? currentLanguage === 'hindi'
                        ? 'मध्यम'
                        : 'Average Performer'
                      : currentLanguage === 'hindi'
                      ? 'सुधार आवश्यक'
                      : 'Needs Push'}
                  </span>
                </div>

                <p className="text-sm opacity-90 max-w-xl font-medium">
                  {currentLanguage === 'hindi'
                    ? `आप ${benchmark.city} व आस-पास के ${benchmark.business_type.toLowerCase()} व्यवसायों में #${benchmark.rank} स्थान पर हैं।`
                    : `Aap ${benchmark.peer_group} ke merchants mein ${benchmark.rank}th/${benchmark.peer_count} position par hain.`}
                </p>
              </div>

              {/* Overall Score Box */}
              <div className="flex items-center gap-6 bg-white/10 rounded-2xl p-5 backdrop-blur-xs border border-white/20 self-start lg:self-auto shadow-sm">
                <div className="text-center">
                  <span className="text-[11px] font-bold tracking-wider opacity-80 uppercase block">
                    {t('overall_score', 'Overall Benchmark Score')}
                  </span>
                  <div className="flex items-baseline justify-center gap-1 mt-0.5">
                    <span className="text-4xl font-black tracking-tight">{benchmark.overall_score}</span>
                    <span className="opacity-75 font-semibold text-sm">/100</span>
                  </div>
                </div>

                <div className="h-10 w-px bg-white/20" />

                <div className="text-xs space-y-1">
                  <div className="flex items-center gap-1.5 font-bold">
                    <CheckCircle2 className="w-4 h-4 text-emerald-300" />
                    <span>{currentLanguage === 'hindi' ? '6 प्रमुख संकेतक मूल्यांकित' : '6 Core Metrics Scored'}</span>
                  </div>
                  <p className="text-[11px] opacity-80">Updated from verified store records</p>
                </div>
              </div>
            </div>
          </div>

          {/* Main Grid: 6 Metric Tiles + Radar Visualization */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 6 Metric Tiles */}
            <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
              {benchmark.metrics.map((metric) => {
                const badgeVariant = getStatusBadgeVariant(metric.status);
                const statusLabel = getStatusLabel(metric.status, metric.status_text, metric.status_text_hi);

                return (
                  <Card key={metric.name} className="p-5 flex flex-col justify-between">
                    <div>
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-xs font-bold text-text-muted uppercase tracking-wider">
                          {currentLanguage === 'hindi' && metric.label_hi ? metric.label_hi : metric.label}
                        </span>
                        <Badge variant={badgeVariant} className="text-[11px]">
                          {statusLabel}
                        </Badge>
                      </div>

                      <div className="mt-3 flex items-baseline justify-between">
                        <div>
                          <span className="text-xs text-text-muted block font-medium">Your Store</span>
                          <span className="text-2xl font-bold text-text tabular-nums">
                            {metric.unit === '₹'
                              ? `₹${Math.round(metric.you).toLocaleString('en-IN')}`
                              : `${metric.you}${metric.unit}`}
                          </span>
                        </div>

                        <div className="text-right">
                          <span className="text-xs text-text-muted block font-medium">Peer Median</span>
                          <span className="text-sm font-semibold text-text-muted tabular-nums">
                            {metric.unit === '₹'
                              ? `₹${Math.round(metric.peer_median).toLocaleString('en-IN')}`
                              : `${metric.peer_median}${metric.unit}`}
                          </span>
                        </div>
                      </div>

                      <div className="mt-4 space-y-1.5">
                        <div className="flex justify-between text-[10px] text-text-muted font-semibold">
                          <span>Min: {metric.peer_min}{metric.unit}</span>
                          <span className="text-text font-bold">50th %ile (Median)</span>
                          <span>Max: {metric.peer_max}{metric.unit}</span>
                        </div>
                        <div className="h-2 w-full bg-surface-muted rounded-full relative overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              metric.status === 'green'
                                ? 'bg-success'
                                : metric.status === 'yellow'
                                ? 'bg-amber-500'
                                : 'bg-danger'
                            }`}
                            style={{ width: `${metric.percentile}%` }}
                          />
                        </div>
                        <div className="text-right text-[10px] font-bold text-brand tabular-nums">
                          {metric.percentile}th Percentile Rank
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-xs">
                      <p className="text-xs text-text font-medium line-clamp-1 flex-1 pr-2" title={metric.action}>
                        💡 {currentLanguage === 'hindi' && metric.action_hi ? metric.action_hi : metric.action}
                      </p>
                      <button
                        onClick={() => {
                          setSelectedExplainMetric(metric);
                          setIsExplainModalOpen(true);
                        }}
                        className="text-xs font-semibold text-brand hover:underline whitespace-nowrap flex items-center gap-0.5"
                      >
                        <span>Kaise?</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </Card>
                );
              })}
            </div>

            {/* Radar / Spider Chart Panel */}
            <Card className="p-5 flex flex-col justify-between">
              <div>
                <SectionHeader
                  title="Benchmark Radar"
                  subtitle="Multivariate percentile comparison"
                />

                <div className="py-2 flex justify-center">{renderRadarChart(benchmark.metrics)}</div>

                <div className="mt-3 flex items-center justify-center gap-4 text-xs text-text-muted font-medium">
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-2 rounded-xs bg-brand" />
                    <span>Your Store</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 border-t-2 border-dashed border-brand" />
                    <span>Peer Median (50%)</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-3.5 rounded-xl bg-surface-muted/60 border border-border text-xs space-y-2">
                <p className="font-semibold text-text">Want an explanation in Hindi or Hinglish?</p>
                <Button
                  variant="primary"
                  size="sm"
                  className="w-full text-xs font-semibold"
                  onClick={() => onQuickCopilot && onQuickCopilot('Meri dukaan dusron se kaisi hai?')}
                >
                  Ask Copilot: "Meri dukaan dusron se kaisi hai?"
                </Button>
              </div>
            </Card>
          </div>

          {/* What Top Performers Do Panel */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-xl bg-success/10 text-success border border-success/20">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-text">
                  What Top 10% {benchmark.business_type} Performers Do
                </h3>
                <p className="text-xs text-text-muted font-medium">
                  Category leaders' validated operational patterns and growth tactics
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {benchmark.top_performer_practices.map((practice, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 p-3.5 rounded-xl bg-surface-muted/50 border border-border text-xs text-text font-medium"
                >
                  <div className="w-6 h-6 rounded-full bg-brand text-brand-contrast flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                    {idx + 1}
                  </div>
                  <span className="leading-relaxed">{practice}</span>
                </div>
              ))}
            </div>
          </Card>
        </>
      ) : null}

      {/* "Kaise Pata Chala?" Explanation Modal */}
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
          <div className="space-y-4 text-xs text-text">
            <p className="text-text-muted leading-relaxed">
              VyaparMitra peer benchmarking compares your store against{' '}
              <strong className="text-text font-bold">{benchmark.peer_count} verified stores</strong> in{' '}
              <strong className="text-text font-bold">{benchmark.peer_group}</strong>.
            </p>

            <div className="rounded-xl bg-surface-muted/60 p-4 border border-border space-y-2 text-xs">
              <span className="font-bold text-text uppercase tracking-wider block">Calculation Breakdown</span>
              <div className="grid grid-cols-2 gap-2 text-text-muted font-medium">
                <div>Your Store Value:</div>
                <div className="font-bold text-text text-right tabular-nums">
                  {selectedExplainMetric.unit === '₹'
                    ? `₹${selectedExplainMetric.you.toLocaleString('en-IN')}`
                    : `${selectedExplainMetric.you}${selectedExplainMetric.unit}`}
                </div>

                <div>Peer Median (50%):</div>
                <div className="font-bold text-text text-right tabular-nums">
                  {selectedExplainMetric.unit === '₹'
                    ? `₹${selectedExplainMetric.peer_median.toLocaleString('en-IN')}`
                    : `${selectedExplainMetric.peer_median}${selectedExplainMetric.unit}`}
                </div>

                <div>Percentile Rank:</div>
                <div className="font-bold text-brand text-right tabular-nums">
                  {selectedExplainMetric.percentile}th %ile
                </div>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-brand/10 border border-brand/20 text-text">
              <span className="font-bold block mb-1">Recommended Growth Action:</span>
              <p className="text-xs text-text-muted">{selectedExplainMetric.action}</p>
            </div>

            <div className="flex justify-end pt-2">
              <Button variant="secondary" onClick={() => setIsExplainModalOpen(false)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* WhatsApp Digest Modal */}
      <Modal
        isOpen={isWhatsAppModalOpen}
        onClose={() => setIsWhatsAppModalOpen(false)}
        title="Weekly WhatsApp Benchmark Digest"
        subtitle="Share an automated scorecard summary directly with store staff or business partner."
      >
        {benchmark && (
          <div className="space-y-4 text-xs text-text">
            <div className="relative">
              <pre className="p-4 rounded-xl bg-surface-muted/70 border border-border text-[11px] font-mono whitespace-pre-wrap text-text max-h-56 overflow-y-auto leading-relaxed">
                {benchmark.whatsapp_digest}
              </pre>
              <button
                onClick={handleCopyWhatsApp}
                className="absolute top-3 right-3 p-1.5 rounded-lg bg-surface border border-border text-text hover:bg-surface-muted shadow-xs transition-all flex items-center gap-1 text-[11px] font-semibold"
              >
                {copiedWhatsApp ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-success" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy Text</span>
                  </>
                )}
              </button>
            </div>

            <div className="space-y-2 pt-2 border-t border-border">
              <label className="font-semibold text-text block">Recipient Mobile Number (WhatsApp)</label>
              <div className="flex gap-2">
                <input
                  type="tel"
                  value={whatsAppPhone}
                  onChange={(e) => setWhatsAppPhone(e.target.value)}
                  placeholder="+91 98765 43210"
                  className="flex-1 px-3 py-2 rounded-xl border border-border bg-surface text-text font-mono text-xs focus:outline-none focus:ring-2 focus:ring-brand font-medium"
                />
                <Button
                  variant="primary"
                  onClick={handleSendWhatsApp}
                  disabled={sendingWhatsApp || !whatsAppPhone.trim()}
                  className="gap-1.5 shrink-0"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{sendingWhatsApp ? 'Sending...' : 'Send'}</span>
                </Button>
              </div>

              {whatsAppStatusMsg && (
                <div
                  className={`p-3 rounded-xl text-xs font-semibold mt-2 flex items-center gap-2 ${
                    whatsAppStatusType === 'success'
                      ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                      : whatsAppStatusType === 'info'
                      ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20'
                      : 'bg-danger/10 text-danger border border-danger/20'
                  }`}
                >
                  <Info className="w-4 h-4 shrink-0" />
                  <span>{whatsAppStatusMsg}</span>
                </div>
              )}
            </div>

            <div className="flex justify-end pt-2 border-t border-border">
              <Button variant="secondary" onClick={() => setIsWhatsAppModalOpen(false)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
