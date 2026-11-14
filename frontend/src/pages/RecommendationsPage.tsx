import React, { useEffect, useState } from 'react';
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
        title={language === 'hindi' ? 'व्यापारी एक्शन सेंटर' : 'Merchant Action Center'}
        subtitle={
          language === 'hindi'
            ? 'इन्वेंट्री, चर्न शमन और बंडलिंग के आधार पर व्यापारिक निर्णय।'
            : 'Evidence-backed business interventions synthesized across restock alerts, churn risk, and cross-sell combos.'
        }
        actions={
          <Badge variant="info">
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              <span>{recommendations.length} Actions Available</span>
            </span>
          </Badge>
        }
      />

      {/* Governance & Safeguard Notice */}
      <Card className="bg-brand/5 border-brand/20 p-4">
        <div className="flex items-start gap-3">
          <Info className="w-4 h-4 text-brand shrink-0 mt-0.5" />
          <p className="text-xs text-text leading-relaxed">
            <span className="font-bold text-text">Commercial Safety Boundary: </span>
            VyaparMitra surfaces evidence-backed recommendations for your consideration. The system will never execute purchases, adjust prices, or dispatch customer messages without your explicit approval.
          </p>
        </div>
      </Card>

      {/* Filter Row */}
      <Card className="p-4">
        <div className="flex flex-wrap items-center gap-3">
          <Filter className="w-4 h-4 text-brand shrink-0" />

          {/* Type Filter */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
          >
            <option value="ALL">All Subsystems</option>
            <option value="INVENTORY">Inventory Restock</option>
            <option value="RETENTION">Customer Retention</option>
            <option value="CROSS_SELL">Cross-Sell &amp; Bundling</option>
            <option value="PRICING">Pricing &amp; Margin</option>
          </select>

          {/* Priority Filter */}
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
          >
            <option value="ALL">All Priorities</option>
            <option value="CRITICAL">🔴 Critical Priority</option>
            <option value="HIGH">🟠 High Priority</option>
            <option value="MEDIUM">🟡 Medium Priority</option>
            <option value="LOW">🟢 Low Priority</option>
          </select>

          {/* Status Filter */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
          >
            <option value="ALL">All Statuses</option>
            <option value="GENERATED">Generated</option>
            <option value="VIEWED">Viewed</option>
            <option value="ACCEPTED">Accepted</option>
            <option value="REJECTED">Rejected</option>
            <option value="EXECUTED">Executed</option>
          </select>

          <Button variant="secondary" size="sm" onClick={loadRecommendations}>
            Apply Filter
          </Button>
        </div>
      </Card>

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
            const isRejected = rec.status === 'REJECTED';
            const isExecuted = rec.status === 'EXECUTED';

            return (
              <Card
                key={rec.recommendation_id}
                className="p-5 hover:border-brand/40 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge
                      variant={
                        rec.priority_band === 'CRITICAL'
                          ? 'danger'
                          : rec.priority_band === 'HIGH'
                          ? 'warning'
                          : rec.priority_band === 'MEDIUM'
                          ? 'neutral'
                          : 'success'
                      }
                    >
                      {rec.priority_band}
                    </Badge>
                    <span className="text-[11px] font-mono uppercase text-text-muted">
                      [{rec.type}]
                    </span>
                    <span className="text-[11px] font-mono text-text-muted">
                      ID: {rec.recommendation_id}
                    </span>
                    <Badge
                      variant={
                        isAccepted
                          ? 'info'
                          : isExecuted
                          ? 'success'
                          : isRejected
                          ? 'danger'
                          : 'neutral'
                      }
                    >
                      Status: {localizeDynamicText(rec.status, language)}
                    </Badge>
                  </div>

                  <h3 className="text-sm font-bold text-text">{localizeDynamicText(rec.title, language)}</h3>
                  <p className="text-xs text-text font-medium">{localizeDynamicText(rec.action, language)}</p>
                  <p className="text-xs text-text-muted">{localizeDynamicText(rec.reason, language)}</p>

                  <div className="flex items-center gap-4 text-xs pt-1">
                    <span className="font-bold text-success tabular-nums">
                      Expected Impact: {formatCurrency(rec.expected_impact)}
                    </span>
                    {rec.entity_id && (
                      <span className="text-text-muted font-mono text-[11px]">
                        Target: {rec.entity_id}
                      </span>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-border">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setSelectedRec(rec)}
                  >
                    View Rationale
                  </Button>

                  {!isAccepted && !isExecuted && (
                    <Button
                      variant="primary"
                      size="sm"
                      isLoading={updatingId === rec.recommendation_id}
                      onClick={() => handleStatusChange(rec.recommendation_id, 'ACCEPTED')}
                    >
                      Accept
                    </Button>
                  )}

                  {isAccepted && !isExecuted && (
                    <Button
                      variant="primary"
                      size="sm"
                      className="bg-emerald-600 hover:bg-emerald-700 text-white"
                      isLoading={updatingId === rec.recommendation_id}
                      onClick={() => handleStatusChange(rec.recommendation_id, 'EXECUTED')}
                    >
                      Mark Executed
                    </Button>
                  )}

                  {!isRejected && (
                    <Button
                      variant="secondary"
                      size="sm"
                      isLoading={updatingId === rec.recommendation_id}
                      onClick={() => handleStatusChange(rec.recommendation_id, 'REJECTED')}
                    >
                      Dismiss
                    </Button>
                  )}
                </div>
              </Card>
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
