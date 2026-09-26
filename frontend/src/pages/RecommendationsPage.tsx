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
import { Modal } from '../components/Modal';
import { TableSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner, EmptyState } from '../components/EmptyState';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';

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
        const found = res.recommendations.find((r) => r.recommendation_id === initialActionId);
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
      // Update locally
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
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-paytm-blue" />
            <h2 className="text-xl font-bold text-paytm-dark">{language === 'hindi' ? 'व्यापारी एक्शन सेंटर' : language === 'hinglish' ? 'Merchant Action Center' : 'Merchant Action Center'}</h2>
          </div>
          <p className="text-xs text-paytm-muted mt-0.5">
            {language === 'hindi' ? 'इन्वेंट्री, चर्न शमन और बंडलिंग के आधार पर व्यापारिक निर्णय।' : 'Prioritized business decisions synthesized across inventory restock, churn mitigation, and bundling.'}
          </p>
        </div>
        <Badge variant="info">{language === 'hindi' ? 'कुल कार्य:' : 'Total Actions:'} {recommendations.length}</Badge>
      </div>

      {/* Governance & Safeguard Notice */}
      <div className="bg-paytm-light rounded-xl border border-paytm-border p-4 text-xs text-paytm-dark flex items-start gap-3">
        <Info className="w-4 h-4 text-paytm-blue shrink-0 mt-0.5" />
        <p>
          <span className="font-semibold text-paytm-dark">{language === 'hindi' ? 'व्यापार सुरक्षा सीमा:' : 'Commercial Safety Boundary:'}</span> {language === 'hindi' ? 'व्यापारमित्र साक्ष्य-समर्थित सुझाव देता है। सिस्टम आपकी स्पष्ट सहमति के बिना कोई भी कार्य निष्पादित नहीं करेगा।' : 'VyaparMitra surfaces evidence-backed recommendations for your consideration. The system will never execute purchases, adjust prices, or dispatch customer messages without your explicit confirmation.'}
        </p>
      </div>

      {/* Filter Row */}
      <div className="bg-white rounded-xl border border-paytm-border p-4 flex flex-wrap items-center gap-3 shadow-xs">
        <Filter className="w-4 h-4 text-slate-400" />
        
        {/* Type Filter */}
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-3 py-2 text-xs rounded-lg border border-paytm-border bg-white text-paytm-text focus:outline-none focus:ring-2 focus:ring-paytm-blue"
        >
          <option value="ALL">{language === 'hindi' ? 'सभी उपप्रणालियाँ' : 'All Subsystems'}</option>
          <option value="INVENTORY">{language === 'hindi' ? 'इन्वेंट्री रेस्टॉक' : 'Inventory Restock'}</option>
          <option value="RETENTION">{language === 'hindi' ? 'ग्राहक प्रतिधारण' : 'Customer Retention'}</option>
          <option value="CROSS_SELL">{language === 'hindi' ? 'क्रॉस-सेल और बंडलिंग' : 'Cross-Sell & Bundling'}</option>
          <option value="PRICING">{language === 'hindi' ? 'मूल्य और मार्जिन' : 'Pricing & Margin'}</option>
        </select>

        {/* Priority Filter */}
        <select
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value)}
          className="px-3 py-2 text-xs rounded-lg border border-paytm-border bg-white text-paytm-text focus:outline-none focus:ring-2 focus:ring-paytm-blue"
        >
          <option value="ALL">{language === 'hindi' ? 'सभी प्राथमिकताएं' : 'All Priorities'}</option>
          <option value="CRITICAL">🔴 {language === 'hindi' ? 'अति-महत्वपूर्ण' : 'Critical Priority'}</option>
          <option value="HIGH">🟠 {language === 'hindi' ? 'उच्च प्राथमिकता' : 'High Priority'}</option>
          <option value="MEDIUM">🟡 {language === 'hindi' ? 'मध्यम प्राथमिकता' : 'Medium Priority'}</option>
          <option value="LOW">🟢 {language === 'hindi' ? 'कम प्राथमिकता' : 'Low Priority'}</option>
        </select>

        {/* Status Filter */}
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-2 text-xs rounded-lg border border-paytm-border bg-white text-paytm-text focus:outline-none focus:ring-2 focus:ring-paytm-blue"
        >
          <option value="ALL">{language === 'hindi' ? 'सभी स्थितियाँ' : 'All Statuses'}</option>
          <option value="GENERATED">{language === 'hindi' ? 'उत्पन्न' : 'Generated'}</option>
          <option value="VIEWED">{language === 'hindi' ? 'देखा गया' : 'Viewed'}</option>
          <option value="ACCEPTED">{language === 'hindi' ? 'स्वीकृत' : 'Accepted'}</option>
          <option value="REJECTED">{language === 'hindi' ? 'अस्वीकृत' : 'Rejected'}</option>
          <option value="EXECUTED">{language === 'hindi' ? 'निष्पादित' : 'Executed'}</option>
        </select>

        <Button variant="secondary" size="sm" onClick={loadRecommendations}>
          {language === 'hindi' ? 'फ़िल्टर' : 'Filter'}
        </Button>
      </div>

      {/* Recommendations List */}
      {loading ? (
        <TableSkeleton rows={6} />
      ) : error ? (
        <ErrorBanner message={error} onRetry={loadRecommendations} />
      ) : recommendations.length === 0 ? (
        <EmptyState
          title={language === 'hindi' ? "कोई कार्य मेल नहीं खाता" : "No Actions Matching Criteria"}
          message={language === 'hindi' ? "सभी स्पष्ट! कोई लंबित सुझाव आपके चयनित फ़िल्टर से मेल नहीं खाता।" : "All clear! No pending recommendations match your selected filters."}
          actionText={language === 'hindi' ? "फ़िल्टर रीसेट करें" : "Reset Filters"}
          onAction={() => {
            setFilterType('ALL');
            setFilterPriority('ALL');
            setFilterStatus('ALL');
          }}
        />
      ) : (
        <div className="space-y-3">
          {recommendations.map((rec) => {
            const isAccepted = rec.status === 'ACCEPTED';
            const isRejected = rec.status === 'REJECTED';
            const isExecuted = rec.status === 'EXECUTED';

            return (
              <div
                key={rec.recommendation_id}
                className="bg-white rounded-xl border border-paytm-border p-5 shadow-xs hover:border-paytm-blue/60 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge
                      variant={
                        rec.priority_band === 'CRITICAL'
                          ? 'critical'
                          : rec.priority_band === 'HIGH'
                          ? 'high'
                          : rec.priority_band === 'MEDIUM'
                          ? 'medium'
                          : 'low'
                      }
                    >
                      {rec.priority_band}
                    </Badge>
                    <span className="text-[11px] font-mono uppercase text-slate-400">
                      [{rec.type}]
                    </span>
                    <span className="text-[11px] font-mono text-slate-400">
                      ID: {rec.recommendation_id}
                    </span>
                    <Badge
                      variant={
                        isAccepted
                          ? 'info'
                          : isExecuted
                          ? 'success'
                          : isRejected
                          ? 'critical'
                          : 'neutral'
                      }
                    >
                      {language === 'hindi' ? 'स्थिति:' : 'Status:'} {localizeDynamicText(rec.status, language)}
                    </Badge>
                  </div>

                  <h3 className="text-sm font-bold text-paytm-dark">{localizeDynamicText(rec.title, language)}</h3>
                  <p className="text-xs text-paytm-text font-medium">{localizeDynamicText(rec.action, language)}</p>
                  <p className="text-xs text-paytm-muted">{localizeDynamicText(rec.reason, language)}</p>

                  <div className="flex items-center gap-4 text-xs pt-1">
                    <span className="font-semibold text-emerald-700">
                      {language === 'hindi' ? 'अपेक्षित प्रभाव:' : 'Expected Impact:'} ₹{rec.expected_impact.toLocaleString()}
                    </span>
                    {rec.entity_id && (
                      <span className="text-paytm-muted font-mono">
                        {language === 'hindi' ? 'लक्ष्य:' : 'Target:'} {rec.entity_id}
                      </span>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-100">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedRec(rec)}
                  >
                    {language === 'hindi' ? 'कारण व साक्ष्य देखें' : 'View Why & Evidence'}
                  </Button>

                  {!isAccepted && !isExecuted && (
                    <Button
                      variant="primary"
                      size="sm"
                      isLoading={updatingId === rec.recommendation_id}
                      onClick={() => handleStatusChange(rec.recommendation_id, 'ACCEPTED')}
                    >
                      {language === 'hindi' ? 'स्वीकार करें' : 'Accept'}
                    </Button>
                  )}

                  {isAccepted && !isExecuted && (
                    <Button
                      variant="success"
                      size="sm"
                      isLoading={updatingId === rec.recommendation_id}
                      onClick={() => handleStatusChange(rec.recommendation_id, 'EXECUTED')}
                    >
                      {language === 'hindi' ? 'निष्पादित करें' : 'Mark Executed'}
                    </Button>
                  )}

                  {!isRejected && (
                    <Button
                      variant="secondary"
                      size="sm"
                      isLoading={updatingId === rec.recommendation_id}
                      onClick={() => handleStatusChange(rec.recommendation_id, 'REJECTED')}
                    >
                      {language === 'hindi' ? 'रद्द करें' : 'Dismiss'}
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
          title={`${language === 'hindi' ? 'सुझाव का कारण:' : 'Recommendation Rationale:'} ${localizeDynamicText(selectedRec.title, language)}`}
          subtitle={`${language === 'hindi' ? 'प्राथमिकता बैंड:' : 'Priority Band:'} ${localizeDynamicText(selectedRec.priority_band, language)} • ${language === 'hindi' ? 'प्राथमिकता स्कोर:' : 'Priority Score:'} ${selectedRec.priority_score.toFixed(4)}`}
          footer={
            <div className="flex items-center gap-2">
              {selectedRec.status !== 'ACCEPTED' && selectedRec.status !== 'EXECUTED' && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleStatusChange(selectedRec.recommendation_id, 'ACCEPTED')}
                >
                  {language === 'hindi' ? 'कार्य स्वीकार करें' : 'Accept Action'}
                </Button>
              )}
              {selectedRec.status === 'ACCEPTED' && (
                <Button
                  variant="success"
                  size="sm"
                  onClick={() => handleStatusChange(selectedRec.recommendation_id, 'EXECUTED')}
                >
                  {language === 'hindi' ? 'निष्पादन की पुष्टि करें' : 'Confirm Execution'}
                </Button>
              )}
              <Button variant="secondary" size="sm" onClick={() => setSelectedRec(null)}>
                {language === 'hindi' ? 'बंद करें' : 'Close'}
              </Button>
            </div>
          }
        >
          <div className="space-y-4">
            <div className="p-3.5 rounded-xl bg-paytm-light border border-paytm-border">
              <span className="text-[10px] uppercase font-bold text-paytm-blue">{language === 'hindi' ? 'सुझाए गए व्यापारिक कार्य' : 'Recommended Business Action'}</span>
              <p className="text-sm font-semibold text-paytm-dark mt-1">{localizeDynamicText(selectedRec.action, language)}</p>
            </div>

            <div>
              <h4 className="text-xs font-bold text-paytm-dark mb-1">{language === 'hindi' ? 'अंतर्निहित कारण' : 'Underlying Rationale'}</h4>
              <p className="text-xs text-paytm-text leading-relaxed">{localizeDynamicText(selectedRec.reason, language)}</p>
            </div>

            {/* 6-Part Auditable Evidence */}
            <div className="pt-2 border-t border-slate-100">
              <h4 className="text-xs font-bold text-paytm-dark mb-2">{language === 'hindi' ? 'ऑडिट योग्य डेटा साक्ष्य' : 'Auditable Data Evidence'} ({selectedRec.evidence.length} {language === 'hindi' ? 'संकेतक' : 'Indicators'})</h4>
              {selectedRec.evidence.length === 0 ? (
                <p className="text-xs text-paytm-muted">{language === 'hindi' ? 'साक्ष्य रिकॉर्ड दुकान की वास्तविक बिक्री से संकलित है।' : 'Evidence record compiled from verified store sales.'}</p>
              ) : (
                <div className="space-y-2">
                  {selectedRec.evidence.map((ev, i) => (
                    <div key={i} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-paytm-dark">{localizeDynamicText(ev.metric, language)}</span>
                        <span className="font-bold text-emerald-700">{String(ev.value)}</span>
                      </div>
                      {ev.description && <p className="text-[11px] text-paytm-muted mt-0.5">{localizeDynamicText(ev.description, language)}</p>}
                      <div className="mt-1 text-[10px] text-slate-400 font-mono">{language === 'hindi' ? 'स्रोत:' : 'Source:'} {localizeDynamicText(ev.source, language)}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
