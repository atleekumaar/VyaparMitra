import React, { useEffect, useState, useMemo } from 'react';
import {
  Sparkles,
  Filter,
  CheckCircle,
  XCircle,
  Clock,
  ShieldAlert,
  ArrowRight,
  TrendingUp,
  Info,
  Package,
  Tag,
  Users,
  Zap,
} from 'lucide-react';
import { api } from '../api/client';
import { RecommendationDetail } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { PageHeader } from '../components/PageHeader';
import { SectionHeader } from '../components/SectionHeader';
import { Modal } from '../components/Modal';
import { TableSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner, EmptyState } from '../components/EmptyState';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';
import { formatCurrency } from '../utils/formatters';

interface RecommendationsPageProps {
  initialActionId?: string | null;
}

export const RecommendationsPage: React.FC<RecommendationsPageProps> = ({
  initialActionId,
}) => {
  const { t, language } = useLanguage();
  const [recommendations, setRecommendations] = useState<RecommendationDetail[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [filterType, setFilterType] = useState<string>('ALL');
  const [filterPriority, setFilterPriority] = useState<string>('ALL');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const [selectedRec, setSelectedRec] = useState<RecommendationDetail | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const inventoryCount = useMemo(
    () => recommendations.filter((r) => r.type === 'INVENTORY').length,
    [recommendations]
  );
  const pricingCount = useMemo(
    () => recommendations.filter((r) => r.type === 'PRICING' || r.type === 'MARGIN').length,
    [recommendations]
  );
  const customersCount = useMemo(
    () => recommendations.filter((r) => r.type === 'RETENTION' || r.type === 'CROSS_SELL').length,
    [recommendations]
  );

  const loadRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getRecommendations({
        type: filterType !== 'ALL' ? filterType : undefined,
        priority: filterPriority !== 'ALL' ? filterPriority : undefined,
        status: filterStatus !== 'ALL' ? filterStatus : undefined,
        limit: 100,
      });
      setRecommendations(res.recommendations || []);

      if (initialActionId) {
        const found = (res.recommendations || []).find((r: any) => r.recommendation_id === initialActionId);
        if (found) setSelectedRec(found);
      }
    } catch (err: any) {
      console.error('[loadRecommendations] Failed to fetch data:', err);
      setError(err?.message || 'Failed to load recommendations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, [filterType, filterPriority, filterStatus]);

  const handleStatusChange = async (recId: string, newStatus: string) => {
    setUpdatingId(recId);
    try {
      await api.updateActionStatus(recId, newStatus);
      setRecommendations((prev) =>
        prev.map((r) =>
          r.recommendation_id === recId ? { ...r, status: newStatus } : r
        )
      );
      if (selectedRec && selectedRec.recommendation_id === recId) {
        setSelectedRec({ ...selectedRec, status: newStatus });
      }
    } catch (err: any) {
      alert(`Could not update action status: ${err?.message}`);
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      <PageHeader
        title="⚡ Action Center"
        subtitle="AI-powered, high-impact recommendations for your business."
        actions={
          <div className="flex items-center gap-2">
            <span className="px-3 py-1.5 rounded-xl bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 font-bold text-xs border border-purple-200/50 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-purple-600" />
              <span>{recommendations.length} Actions Available</span>
            </span>
          </div>
        }
      />

      {/* Category Segmented Tabs Inspired by Mockup */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs font-semibold">
        {[
          { id: 'ALL', label: `All (${recommendations.length})` },
          { id: 'INVENTORY', label: `Inventory (${inventoryCount})` },
          { id: 'PRICING', label: `Pricing (${pricingCount})` },
          { id: 'RETENTION', label: `Customers (${customersCount})` },
        ].map((tab) => {
          const isActive = filterType === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setFilterType(tab.id)}
              className={`px-4 py-2 rounded-xl transition-all whitespace-nowrap ${
                isActive
                  ? 'bg-blue-600 text-white font-bold shadow-xs'
                  : 'bg-surface-card hover:bg-surface-muted text-text-muted hover:text-text border border-border'
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Governance & Safeguard Notice */}
      <div className="rounded-2xl bg-blue-500/5 border border-blue-500/20 p-4">
        <div className="flex items-start gap-3">
          <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
          <p className="text-xs text-text leading-relaxed">
            <span className="font-bold text-text">Commercial Safety Boundary: </span>
            VyaparMitra surfaces evidence-backed recommendations for your consideration. The system will never execute purchases, adjust prices, or dispatch customer messages without your explicit approval.
          </p>
        </div>
      </div>

      {/* Recommendations List */}
      {loading ? (
        <TableSkeleton rows={6} />
      ) : error ? (
        <ErrorBanner message={error} onRetry={loadRecommendations} />
      ) : recommendations.length === 0 ? (
        <Card className="p-8">
          <EmptyState
            title="All Clear — No Pending Interventions"
            message="Your business metrics are operating within normal baseline boundaries. As new patterns emerge, actionable prompts will appear here."
            actionText="Reset Filters"
            onAction={() => {
              setFilterType('ALL');
              setFilterPriority('ALL');
              setFilterStatus('ALL');
            }}
          />
        </Card>
      ) : (
        <div className="space-y-3">
          {recommendations.map((rec) => {
            const isAccepted = rec.status === 'ACCEPTED';
            const isExecuted = rec.status === 'EXECUTED';
            const isInventory = rec.type === 'INVENTORY';
            const isPricing = rec.type === 'PRICING' || rec.type === 'MARGIN';
            const isCustomer = rec.type === 'RETENTION' || rec.type === 'CROSS_SELL';

            const impactLabel =
              rec.priority_band === 'CRITICAL' || rec.priority_band === 'HIGH'
                ? 'High Impact'
                : rec.priority_band === 'MEDIUM'
                ? 'Medium'
                : 'Low Impact';

            return (
              <div
                key={rec.recommendation_id}
                className="bg-surface-card rounded-2xl border border-border p-5 hover:border-blue-300 dark:hover:border-blue-700 shadow-fintech transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                {/* Left: Icon and Details */}
                <div className="flex items-start gap-3.5 flex-1 min-w-0">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-2xs mt-0.5 ${
                      isInventory
                        ? 'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-400 border border-amber-200/50'
                        : isPricing
                        ? 'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-400 border border-blue-200/50'
                        : isCustomer
                        ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400 border border-emerald-200/50'
                        : 'bg-purple-50 text-purple-600 dark:bg-purple-950/40 dark:text-purple-400 border border-purple-200/50'
                    }`}
                  >
                    {isInventory ? (
                      <Package className="w-5 h-5" />
                    ) : isPricing ? (
                      <Tag className="w-5 h-5" />
                    ) : isCustomer ? (
                      <Users className="w-5 h-5" />
                    ) : (
                      <Zap className="w-5 h-5" />
                    )}
                  </div>

                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-bold text-text truncate">
                        {localizeDynamicText(rec.title, language)}
                      </h3>
                      {rec.entity_id && (
                        <span className="text-[10px] text-text-muted font-mono bg-surface-muted px-1.5 py-0.5 rounded border border-border">
                          {rec.entity_id}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-text-muted leading-relaxed line-clamp-2">
                      {localizeDynamicText(rec.reason || rec.action, language)}
                    </p>
                    {rec.expected_impact > 0 && (
                      <div className="pt-0.5">
                        <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400">
                          Expected Impact: +{formatCurrency(rec.expected_impact)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Right: Impact Pill & Action Button */}
                <div className="flex items-center gap-3 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-border justify-between md:justify-end">
                  {/* Impact badge */}
                  <span
                    className={`inline-flex px-3 py-1 rounded-full text-xs font-bold border ${
                      impactLabel === 'High Impact'
                        ? 'bg-rose-50 text-rose-600 dark:bg-rose-950/40 dark:text-rose-400 border-rose-200/50'
                        : impactLabel === 'Medium'
                        ? 'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-400 border-amber-200/50'
                        : 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400 border-emerald-200/50'
                    }`}
                  >
                    {impactLabel}
                  </span>

                  {/* Primary Action Button matching mockup */}
                  {isInventory ? (
                    <Button
                      variant="primary"
                      size="sm"
                      isLoading={updatingId === rec.recommendation_id}
                      onClick={() => handleStatusChange(rec.recommendation_id, 'ACCEPTED')}
                      className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-4 py-2 rounded-xl shadow-xs"
                    >
                      Take Action
                    </Button>
                  ) : isPricing ? (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setSelectedRec(rec)}
                      className="font-bold text-xs px-4 py-2 rounded-xl shadow-2xs"
                    >
                      Review
                    </Button>
                  ) : isCustomer ? (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setSelectedRec(rec)}
                      className="font-bold text-xs px-4 py-2 rounded-xl shadow-2xs"
                    >
                      Start Campaign
                    </Button>
                  ) : (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setSelectedRec(rec)}
                      className="font-bold text-xs px-4 py-2 rounded-xl shadow-2xs"
                    >
                      Details
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Evidence & Rationale Modal */}
      {selectedRec && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedRec(null)}
          title={`Recommendation: ${localizeDynamicText(selectedRec.title, language)}`}
          subtitle={`Priority Band: ${localizeDynamicText(selectedRec.priority_band, language)} • Score: ${selectedRec.priority_score.toFixed(4)}`}
        >
          <div className="space-y-4 text-xs text-text">
            <div className="p-3.5 rounded-xl bg-surface-muted/60 border border-border">
              <span className="text-[10px] uppercase font-bold text-brand">Recommended Intervention</span>
              <p className="text-sm font-semibold text-text mt-1">{localizeDynamicText(selectedRec.action, language)}</p>
            </div>

            <div>
              <h4 className="font-bold text-text mb-1">Underlying Rationale</h4>
              <p className="text-text-muted leading-relaxed">{localizeDynamicText(selectedRec.reason, language)}</p>
            </div>

            {/* Evidence List */}
            <div className="pt-2 border-t border-border">
              <h4 className="font-bold text-text mb-2">Auditable Data Evidence ({selectedRec.evidence.length} Indicators)</h4>
              {selectedRec.evidence.length === 0 ? (
                <p className="text-text-muted">Evidence record compiled from verified store sales.</p>
              ) : (
                <div className="space-y-2">
                  {selectedRec.evidence.map((ev, i) => (
                    <div key={i} className="p-2.5 rounded-xl bg-surface-muted/50 border border-border text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-text">{localizeDynamicText(ev.metric, language)}</span>
                        <span className="font-bold text-success">{String(ev.value)}</span>
                      </div>
                      {ev.description && <p className="text-[11px] text-text-muted mt-0.5">{localizeDynamicText(ev.description, language)}</p>}
                      <div className="mt-1 text-[10px] text-text-muted font-mono">Source: {localizeDynamicText(ev.source, language)}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-border">
              {selectedRec.status !== 'ACCEPTED' && selectedRec.status !== 'EXECUTED' && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleStatusChange(selectedRec.recommendation_id, 'ACCEPTED')}
                >
                  Accept Action
                </Button>
              )}
              {selectedRec.status === 'ACCEPTED' && (
                <Button
                  variant="primary"
                  size="sm"
                  className="bg-emerald-600 hover:bg-emerald-700 text-white"
                  onClick={() => handleStatusChange(selectedRec.recommendation_id, 'EXECUTED')}
                >
                  Confirm Execution
                </Button>
              )}
              <Button variant="secondary" size="sm" onClick={() => setSelectedRec(null)}>
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
