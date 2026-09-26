import React, { useEffect, useState } from 'react';
import { Users, Filter, AlertTriangle, ShieldCheck, HeartHandshake, PhoneCall } from 'lucide-react';
import { api } from '../api/client';
import { CustomerDetail, CustomerListItem } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Modal } from '../components/Modal';
import { TableSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner, EmptyState } from '../components/EmptyState';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';

export const CustomersPage: React.FC = () => {
  const { t, language } = useLanguage();
  const [customers, setCustomers] = useState<CustomerListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedSegment, setSelectedSegment] = useState<string>('');
  const [selectedRisk, setSelectedRisk] = useState<string>('');
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerDetail | null>(null);

  const loadCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getCustomers({
        segment: selectedSegment || undefined,
        risk_tier: selectedRisk || undefined,
        limit: 100,
      });
      setCustomers(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load customers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCustomers();
  }, [selectedSegment, selectedRisk]);

  const handleOpenDetail = async (customerId: string) => {
    try {
      const detail = await api.getCustomerDetail(customerId);
      setSelectedCustomer(detail);
    } catch (err: any) {
      alert(`Could not load customer detail: ${err?.message}`);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-paytm-dark">{language === 'hindi' ? 'ग्राहक बुद्धिमत्ता और प्रतिधारण' : 'Customer Intelligence & Retention'}</h2>
          <p className="text-xs text-paytm-muted mt-0.5">
            {language === 'hindi' ? 'एआई चर्न जोखिम स्कोरिंग, खरीद नवीनता, और प्राथमिकता प्रतिधारण आउटरीच।' : 'AI churn risk scoring, purchase recency, and prioritized retention outreach.'}
          </p>
        </div>
        <Badge variant="info">{language === 'hindi' ? 'निगरानी वाले ग्राहक:' : 'Monitored Customers:'} {customers.length}</Badge>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-paytm-border p-4 flex flex-wrap items-center gap-3 shadow-xs">
        <Filter className="w-4 h-4 text-slate-400" />
        <select
          value={selectedRisk}
          onChange={(e) => setSelectedRisk(e.target.value)}
          className="px-3 py-2 text-xs rounded-lg border border-paytm-border bg-white text-paytm-text focus:outline-none focus:ring-2 focus:ring-paytm-blue"
        >
          <option value="">{language === 'hindi' ? 'सभी चर्न स्तर' : 'All Churn Tiers'}</option>
          <option value="high">{language === 'hindi' ? 'उच्च चर्न जोखिम' : 'High Churn Risk'}</option>
          <option value="medium">{language === 'hindi' ? 'मध्यम चर्न जोखिम' : 'Medium Churn Risk'}</option>
          <option value="low">{language === 'hindi' ? 'कम चर्न जोखिम' : 'Low Churn Risk'}</option>
        </select>

        <select
          value={selectedSegment}
          onChange={(e) => setSelectedSegment(e.target.value)}
          className="px-3 py-2 text-xs rounded-lg border border-paytm-border bg-white text-paytm-text focus:outline-none focus:ring-2 focus:ring-paytm-blue"
        >
          <option value="">{language === 'hindi' ? 'सभी सेगमेंट' : 'All Segments'}</option>
          <option value="Champions">{language === 'hindi' ? 'चैंपियंस' : 'Champions'}</option>
          <option value="Loyal">{language === 'hindi' ? 'वफादार ग्राहक' : 'Loyal Customers'}</option>
          <option value="At Risk">{language === 'hindi' ? 'जोखिम में' : 'At Risk'}</option>
          <option value="Low Engagement">{language === 'hindi' ? 'कम जुड़ाव' : 'Low Engagement'}</option>
        </select>

        <Button variant="secondary" size="sm" onClick={loadCustomers}>
          {language === 'hindi' ? 'फ़िल्टर' : 'Filter'}
        </Button>
      </div>

      {/* Customers Table */}
      {loading ? (
        <TableSkeleton rows={8} />
      ) : error ? (
        <ErrorBanner message={error} onRetry={loadCustomers} />
      ) : customers.length === 0 ? (
        <EmptyState
          title={language === 'hindi' ? 'कोई ग्राहक फ़िल्टर से मेल नहीं खाता' : "No Customers Match Filters"}
          message={language === 'hindi' ? 'चयनित सेगमेंट या जोखिम स्तर से मेल खाने वाला कोई रिकॉर्ड नहीं मिला।' : "No records found matching the selected segment or risk tier."}
          actionText={language === 'hindi' ? 'फ़िल्टर हटाएं' : "Clear Filters"}
          onAction={() => {
            setSelectedSegment('');
            setSelectedRisk('');
          }}
        />
      ) : (
        <div className="bg-white rounded-xl border border-paytm-border overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
                <tr>
                  <th className="py-3 px-4">{language === 'hindi' ? 'ग्राहक ID' : 'Customer ID'}</th>
                  <th className="py-3 px-4">{language === 'hindi' ? 'सेगमेंट' : 'Segment'}</th>
                  <th className="py-3 px-4">{language === 'hindi' ? 'कुल खर्च' : 'Lifetime Spend'}</th>
                  <th className="py-3 px-4">{language === 'hindi' ? 'ऑर्डर्स' : 'Orders'}</th>
                  <th className="py-3 px-4">{language === 'hindi' ? 'नवीनता (दिन)' : 'Recency (Days)'}</th>
                  <th className="py-3 px-4">{language === 'hindi' ? 'चर्न जोखिम' : 'Churn Risk Tier'}</th>
                  <th className="py-3 px-4">{language === 'hindi' ? 'निष्क्रियता संभ.' : 'Inactivity Prob.'}</th>
                  <th className="py-3 px-4 text-right">{language === 'hindi' ? 'कार्रवाई' : 'Action'}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {customers.map((c) => (
                  <tr key={c.customer_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono font-semibold text-paytm-dark">{c.customer_id}</td>
                    <td className="py-3 px-4 font-medium text-paytm-text">{localizeDynamicText(c.segment, language)}</td>
                    <td className="py-3 px-4 font-semibold text-emerald-700">₹{c.lifetime_spend.toLocaleString()}</td>
                    <td className="py-3 px-4">{c.total_orders}</td>
                    <td className="py-3 px-4 text-paytm-muted">{c.recency_days} {language === 'hindi' ? 'दिन पहले' : 'days ago'}</td>
                    <td className="py-3 px-4">
                      <Badge
                        variant={
                          c.churn_risk_tier.toLowerCase() === 'high'
                            ? 'critical'
                            : c.churn_risk_tier.toLowerCase() === 'medium'
                            ? 'high'
                            : 'success'
                        }
                      >
                        {localizeDynamicText(c.churn_risk_tier, language)}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 font-medium">
                      {(c.churn_probability * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleOpenDetail(c.customer_id)}
                      >
                        {language === 'hindi' ? 'प्रतिधारण प्रोफ़ाइल' : 'Retention Profile'}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Customer Detail Modal */}
      {selectedCustomer && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedCustomer(null)}
          title={`${language === 'hindi' ? 'ग्राहक' : 'Customer'} ${selectedCustomer.customer_id} — ${language === 'hindi' ? 'प्रतिधारण प्रोफ़ाइल' : 'Retention Profile'}`}
          subtitle={`${language === 'hindi' ? 'सेगमेंट:' : 'Segment:'} ${localizeDynamicText(selectedCustomer.segment, language)}`}
          footer={
            <Button variant="secondary" size="sm" onClick={() => setSelectedCustomer(null)}>
              {language === 'hindi' ? 'बंद करें' : 'Close'}
            </Button>
          }
        >
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-paytm-muted">{language === 'hindi' ? 'कुल खर्च' : 'Lifetime Spend'}</span>
              <p className="text-base font-bold text-paytm-dark mt-0.5">₹{selectedCustomer.lifetime_spend.toLocaleString()}</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-paytm-muted">{language === 'hindi' ? 'पूरे किए गए ऑर्डर्स' : 'Completed Orders'}</span>
              <p className="text-base font-bold text-paytm-dark mt-0.5">{selectedCustomer.total_orders}</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-paytm-muted">{language === 'hindi' ? 'अंतिम यात्रा से दिन' : 'Days Since Last Visit'}</span>
              <p className="text-base font-bold text-paytm-dark mt-0.5">{selectedCustomer.recency_days} {language === 'hindi' ? 'दिन' : 'days'}</p>
            </div>
            <div className="p-3 bg-red-50 rounded-lg border border-red-100">
              <span className="text-[10px] uppercase font-bold text-red-800">{language === 'hindi' ? 'चर्न संभावना' : 'Churn Probability'}</span>
              <p className="text-base font-bold text-red-700 mt-0.5">{(selectedCustomer.churn_probability * 100).toFixed(1)}%</p>
            </div>
          </div>

          {/* Retention Action Suggestion */}
          <div className="mt-4 p-4 rounded-xl border border-paytm-border bg-paytm-light">
            <div className="flex items-center gap-2 text-xs font-bold text-paytm-dark">
              <HeartHandshake className="w-4 h-4 text-paytm-blue" />
              <span>{language === 'hindi' ? 'अनुशंसित प्रतिधारण रणनीति (एआई निर्णय इंजन)' : 'Recommended Retention Strategy (AI Decision Engine)'}</span>
            </div>
            <p className="text-xs text-paytm-text mt-2 font-medium">
              {localizeDynamicText(selectedCustomer.suggested_retention_action || (language === 'hindi' ? 'लक्षित श्रेणी की पेशकश के साथ फिर से जोड़ने वाला संदेश।' : 'Re-engagement message with targeted category offer.'), language)}
            </p>
            <div className="mt-3 flex items-center gap-2 text-[11px] text-paytm-muted">
              <span>{language === 'hindi' ? 'गोपनीयता सूचना: डेमो मोड में ग्राहक नंबर और व्यक्तिगत पहचान योग्य डेटा छिपे हुए हैं।' : 'Privacy notice: Customer numbers and personally identifiable data are masked in demo mode.'}</span>
            </div>
          </div>

          {/* Evidence Rationale */}
          {selectedCustomer.evidence && selectedCustomer.evidence.length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-100">
              <h4 className="text-xs font-bold text-paytm-dark mb-2">{language === 'hindi' ? 'ऑडिट साक्ष्य' : 'Audit Evidence'}</h4>
              <div className="space-y-1.5">
                {selectedCustomer.evidence.map((ev, i) => (
                  <div key={i} className="text-xs p-2 rounded bg-slate-50 flex items-center justify-between">
                    <span className="font-semibold text-paytm-dark">{localizeDynamicText(ev.metric, language)}: <span className="font-normal">{ev.value}</span></span>
                    <span className="text-[10px] text-paytm-muted">{localizeDynamicText(ev.source, language)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Modal>
      )}
    </div>
  );
};
