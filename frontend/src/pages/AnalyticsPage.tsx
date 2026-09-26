import React, { useEffect, useState } from 'react';
import {
  BarChart2,
  Users,
  Package,
  Layers,
  CreditCard,
  Activity,
  AlertCircle,
  TrendingUp,
  Banknote,
  PlusCircle,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../api/client';
import {
  AnomalyItem,
  CategoryShare,
  CustomerAnalytics,
  PaymentAnalytics,
  ProductAnalytics,
  SalesAnalytics,
  TrendAnalytics,
} from '../types';
import { TableSkeleton, CardSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner, EmptyState } from '../components/EmptyState';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Modal } from '../components/Modal';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';

export const AnalyticsPage: React.FC = () => {
  const { t, language } = useLanguage();
  const [activeTab, setActiveTab] = useState<'sales' | 'customers' | 'products' | 'categories' | 'payments' | 'anomalies'>('sales');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [sales, setSales] = useState<SalesAnalytics | null>(null);
  const [customers, setCustomers] = useState<CustomerAnalytics | null>(null);
  const [products, setProducts] = useState<ProductAnalytics | null>(null);
  const [categories, setCategories] = useState<CategoryShare[]>([]);
  const [payments, setPayments] = useState<PaymentAnalytics | null>(null);
  const [trends, setTrends] = useState<TrendAnalytics | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([]);

  // Cash recording state
  const [isCashModalOpen, setIsCashModalOpen] = useState<boolean>(false);
  const [cashAmount, setCashAmount] = useState<string>('');
  const [cashNote, setCashNote] = useState<string>('');
  const [isSubmittingCash, setIsSubmittingCash] = useState<boolean>(false);
  const [cashSuccessMsg, setCashSuccessMsg] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sRes, cRes, pRes, catRes, payRes, tRes, aRes] = await Promise.all([
        api.getSalesAnalytics(),
        api.getCustomerAnalytics(),
        api.getProductAnalytics(),
        api.getCategoryAnalytics(),
        api.getPaymentAnalytics(),
        api.getTrendAnalytics(),
        api.getAnomalyAnalytics(),
      ]);
      setSales(sRes);
      setCustomers(cRes);
      setProducts(pRes);
      setCategories(catRes.categories || []);
      setPayments(payRes);
      setTrends(tRes);
      setAnomalies(aRes.anomalies || []);
    } catch (err: any) {
      setError(err?.message || 'Failed to load business analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRecordCashSale = async (e: React.FormEvent) => {
    e.preventDefault();
    const amt = parseFloat(cashAmount);
    if (isNaN(amt) || amt <= 0) {
      alert(language === 'hindi' ? 'कृपया सही राशि दर्ज करें (उदा. 100)' : 'Please enter a valid amount (e.g. 100)');
      return;
    }
    setIsSubmittingCash(true);
    setCashSuccessMsg(null);
    try {
      const res = await api.recordCashSale({
        amount: amt,
        product_name: cashNote || (language === 'hindi' ? 'दुकान नकद बिक्री' : 'Manual Cash Sale'),
      });
      setCashSuccessMsg(
        language === 'hindi'
          ? `₹${amt.toLocaleString()} की नकद बिक्री सफलतापूर्वक जोड़ी गई!`
          : `Cash sale of ₹${amt.toLocaleString()} recorded successfully!`
      );
      setCashAmount('');
      setCashNote('');
      await loadData();
      setTimeout(() => {
        setIsCashModalOpen(false);
        setCashSuccessMsg(null);
      }, 1500);
    } catch (err: any) {
      alert(err?.message || 'Failed to record cash sale');
    } finally {
      setIsSubmittingCash(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
        <TableSkeleton rows={8} />
      </div>
    );
  }

  if (error) {
    return <ErrorBanner message={error} onRetry={loadData} />;
  }

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-paytm-dark">{language === 'hindi' ? 'व्यापार विश्लेषण और रिपोर्ट' : 'Business Intelligence & Analytics'}</h2>
        <p className="text-xs text-paytm-muted mt-0.5">
          {language === 'hindi' ? 'बिक्री रुझान, ग्राहक वर्ग, उत्पाद श्रेणी विभाजन और भुगतान माध्यमों का संपूर्ण विवरण।' : 'Empirical sales patterns, customer segments, category distributions, and payment methods.'}
        </p>
      </div>

      {/* Analytics Tabs */}
      <div className="flex items-center gap-1.5 border-b border-paytm-border pb-1 overflow-x-auto text-xs font-semibold">
        {[
          { id: 'sales', label: language === 'hindi' ? 'बिक्री और दैनिक शृंखला' : 'Sales & Daily Series', icon: BarChart2 },
          { id: 'customers', label: language === 'hindi' ? 'ग्राहक सेगमेंट' : 'Customer Segments', icon: Users },
          { id: 'products', label: language === 'hindi' ? 'शीर्ष उत्पाद और पारेतो' : 'Top Products & Pareto', icon: Package },
          { id: 'categories', label: language === 'hindi' ? 'श्रेणी हिस्सा' : 'Categories Share', icon: Layers },
          { id: 'payments', label: language === 'hindi' ? 'भुगतान विधि' : 'Payment Methods', icon: CreditCard },
          { id: 'anomalies', label: language === 'hindi' ? 'रुझान और विसंगतियां' : 'Trends & Anomalies', icon: Activity },
        ].map((t) => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg transition-all whitespace-nowrap ${
                isActive
                  ? 'bg-paytm-dark text-white shadow-xs'
                  : 'text-paytm-muted hover:text-paytm-dark hover:bg-white'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{t.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 1: Sales */}
      {activeTab === 'sales' && sales && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">{language === 'hindi' ? 'कुल राजस्व' : 'Total Revenue'}</span>
              <p className="text-xl font-bold text-paytm-dark mt-1">₹{sales.total_revenue.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">{language === 'hindi' ? 'कुल ऑर्डर्स' : 'Total Orders'}</span>
              <p className="text-xl font-bold text-paytm-dark mt-1">{sales.total_orders.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">{language === 'hindi' ? 'औसत ऑर्डर मूल्य' : 'Average Order Value'}</span>
              <p className="text-xl font-bold text-paytm-dark mt-1">₹{sales.average_order_value.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">{language === 'hindi' ? 'छूट दर' : 'Discount Rate'}</span>
              <p className="text-xl font-bold text-paytm-dark mt-1">{(sales.discount_rate * 100).toFixed(1)}%</p>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-paytm-border overflow-hidden shadow-xs">
            <div className="px-5 py-3 border-b border-paytm-border flex items-center justify-between">
              <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider">
                {language === 'hindi' ? `दैनिक बिक्री रिकॉर्ड (${sales.daily_series.length} दिन)` : `Daily Sales Records (${sales.daily_series.length} Days)`}
              </h3>
            </div>
            <div className="overflow-x-auto max-h-96">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
                  <tr>
                    <th className="py-2.5 px-4">{language === 'hindi' ? 'तारीख' : 'Date'}</th>
                    <th className="py-2.5 px-4">{language === 'hindi' ? 'राजस्व (₹)' : 'Revenue (₹)'}</th>
                    <th className="py-2.5 px-4">{language === 'hindi' ? 'ऑर्डर्स' : 'Orders'}</th>
                    <th className="py-2.5 px-4">{language === 'hindi' ? 'औसत ऑर्डर मूल्य' : 'Avg Order Value'}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {sales.daily_series.slice().reverse().map((d, i) => (
                    <tr key={i} className="hover:bg-slate-50/60">
                      <td className="py-2.5 px-4 font-medium text-paytm-dark">{d.date}</td>
                      <td className="py-2.5 px-4 font-semibold text-emerald-700">₹{d.revenue.toLocaleString()}</td>
                      <td className="py-2.5 px-4 text-paytm-text">{d.orders}</td>
                      <td className="py-2.5 px-4 text-paytm-muted">
                        ₹{d.average_order_value?.toLocaleString() || (d.revenue / Math.max(1, d.orders)).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Customers */}
      {activeTab === 'customers' && customers && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">{language === 'hindi' ? 'कुल संरक्षक' : 'Total Patrons'}</span>
              <p className="text-xl font-bold text-paytm-dark mt-1">{customers.total_customers.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">{language === 'hindi' ? 'उच्च चर्न जोखिम' : 'High Churn Risk'}</span>
              <p className="text-xl font-bold text-red-600 mt-1">{customers.high_risk_count.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">{language === 'hindi' ? 'मध्यम जोखिम' : 'Medium Risk'}</span>
              <p className="text-xl font-bold text-amber-600 mt-1">{customers.medium_risk_count.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">{language === 'hindi' ? 'कम चर्न जोखिम' : 'Low Churn Risk'}</span>
              <p className="text-xl font-bold text-emerald-600 mt-1">{customers.low_risk_count.toLocaleString()}</p>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-paytm-border p-5 shadow-xs">
            <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider mb-4">
              {language === 'hindi' ? 'RFM सेगमेंटेशन और वाणिज्यिक योगदान' : 'RFM Segmentation & Commercial Contribution'}
            </h3>
            <div className="space-y-4">
              {customers.segments.map((seg, idx) => (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-medium">
                    <span className="text-paytm-dark font-semibold">{localizeDynamicText(seg.segment_name, language)}</span>
                    <span className="text-paytm-muted">
                      {seg.customer_count} {language === 'hindi' ? 'ग्राहक' : 'customers'} &bull; ₹{seg.total_revenue.toLocaleString()} ({(seg.revenue_share * 100).toFixed(1)}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-paytm-blue h-2 rounded-full"
                      style={{ width: `${Math.min(100, seg.revenue_share * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Products & Pareto */}
      {activeTab === 'products' && products && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-paytm-border p-4 flex items-center justify-between">
            <div>
              <span className="text-xs text-paytm-muted uppercase font-medium">{language === 'hindi' ? 'पारेतो एकाग्रता' : 'Pareto Concentration'}</span>
              <p className="text-base font-bold text-paytm-dark mt-0.5">
                {language === 'hindi' ? `शीर्ष 20% उत्पाद दुकान की बिक्री का ~${((products.pareto_80_20_ratio || 0.8) * 100).toFixed(0)}% योगदान करते हैं` : `Top 20% products contribute ~${((products.pareto_80_20_ratio || 0.8) * 100).toFixed(0)}% of store sales`}
              </p>
            </div>
            <Badge variant="info">{language === 'hindi' ? 'कुल SKUs:' : 'Total SKUs:'} {products.total_products_tracked}</Badge>
          </div>

          <div className="bg-white rounded-xl border border-paytm-border overflow-hidden shadow-xs">
            <div className="px-5 py-3 border-b border-paytm-border">
              <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider">{language === 'hindi' ? 'शीर्ष 15 राजस्व चालक' : 'Top 15 Revenue Drivers'}</h3>
            </div>
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
                <tr>
                  <th className="py-2.5 px-4">{language === 'hindi' ? 'रैंक' : 'Rank'}</th>
                  <th className="py-2.5 px-4">{language === 'hindi' ? 'उत्पाद ID' : 'Product ID'}</th>
                  <th className="py-2.5 px-4">{language === 'hindi' ? 'श्रेणी' : 'Category'}</th>
                  <th className="py-2.5 px-4">{language === 'hindi' ? 'राजस्व' : 'Revenue'}</th>
                  <th className="py-2.5 px-4">{language === 'hindi' ? 'इकाईयां बिकी' : 'Units Sold'}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {products.top_performers.map((p) => (
                  <tr key={p.product_id} className="hover:bg-slate-50/60">
                    <td className="py-2.5 px-4 font-bold text-paytm-blue">#{p.rank}</td>
                    <td className="py-2.5 px-4 font-medium text-paytm-dark">{p.product_name}</td>
                    <td className="py-2.5 px-4 text-paytm-muted">{localizeDynamicText(p.category, language)}</td>
                    <td className="py-2.5 px-4 font-semibold text-emerald-700">₹{p.revenue.toLocaleString()}</td>
                    <td className="py-2.5 px-4">{p.units.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 4: Categories */}
      {activeTab === 'categories' && (
        <div className="bg-white rounded-xl border border-paytm-border overflow-hidden shadow-xs">
          <div className="px-5 py-3 border-b border-paytm-border">
            <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider">
              {language === 'hindi' ? 'उत्पाद श्रेणी राजस्व और ऑर्डर हिस्सा' : 'Product Category Revenue & Order Shares'}
            </h3>
          </div>
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
              <tr>
                <th className="py-2.5 px-4">{language === 'hindi' ? 'श्रेणी' : 'Category'}</th>
                <th className="py-2.5 px-4">{language === 'hindi' ? 'राजस्व (₹)' : 'Revenue (₹)'}</th>
                <th className="py-2.5 px-4">{language === 'hindi' ? 'ऑर्डर्स' : 'Orders'}</th>
                <th className="py-2.5 px-4">{language === 'hindi' ? 'राजस्व का हिस्सा' : 'Share of Revenue'}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {categories.map((c, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60">
                  <td className="py-2.5 px-4 font-semibold text-paytm-dark">{localizeDynamicText(c.category, language)}</td>
                  <td className="py-2.5 px-4 font-semibold text-emerald-700">₹{c.revenue.toLocaleString()}</td>
                  <td className="py-2.5 px-4">{c.orders}</td>
                  <td className="py-2.5 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-paytm-blue h-2 rounded-full"
                          style={{ width: `${c.revenue_share * 100}%` }}
                        />
                      </div>
                      <span className="text-[11px] text-paytm-muted">{(c.revenue_share * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 5: Payments */}
      {activeTab === 'payments' && payments && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-paytm-border p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
            <div>
              <span className="text-xs text-paytm-muted uppercase font-medium">{language === 'hindi' ? 'प्राथमिक भुगतान माध्यम' : 'Primary Payment Mode'}</span>
              <p className="text-xl font-bold text-paytm-dark mt-0.5">{payments.primary_payment_method}</p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  setCashSuccessMsg(null);
                  setIsCashModalOpen(true);
                }}
                className="bg-[#00B970] hover:bg-[#008A54] text-white font-bold flex items-center gap-1.5 shadow-2xs"
              >
                <Banknote className="w-4 h-4" />
                <span>{language === 'hindi' ? '+ नकद बिक्री जोड़ें' : '+ Record Cash Sale'}</span>
              </Button>
              <Badge variant="success">{language === 'hindi' ? 'फिनटेक सेटलमेंट तैयार' : 'Fintech Settlement Ready'}</Badge>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {payments.payment_methods.map((pm, idx) => (
              <div key={idx} className="bg-white rounded-xl border border-paytm-border p-5">
                <span className="text-xs font-semibold text-paytm-muted uppercase">{pm.payment_method}</span>
                <p className="text-2xl font-bold text-paytm-dark mt-2">₹{pm.total_revenue.toLocaleString()}</p>
                <div className="mt-3 flex items-center justify-between text-xs text-paytm-muted">
                  <span>{pm.transaction_count} {language === 'hindi' ? 'लेनदेन' : 'transactions'}</span>
                  <span className="font-semibold text-paytm-blue">{(pm.revenue_share * 100).toFixed(1)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 6: Anomalies & Trends */}
      {activeTab === 'anomalies' && (
        <div className="space-y-6">
          {trends && (
            <div className="bg-white rounded-xl border border-paytm-border p-5 flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-paytm-muted uppercase">{language === 'hindi' ? 'व्यापार की गति' : 'Business Momentum'}</span>
                <p className="text-base font-bold text-paytm-dark mt-1">
                  {language === 'hindi' ? 'प्रत्याशित रुझान:' : 'Expected Trend:'} <span className="text-paytm-blue">{localizeDynamicText(trends.predicted_trend, language)}</span> ({trends.horizon_days}-{language === 'hindi' ? 'दिवसीय अवधि' : 'day horizon'})
                </p>
                <p className="text-xs text-paytm-muted mt-0.5">
                  {language === 'hindi' ? 'ऐतिहासिक राजस्व गति:' : 'Historical revenue momentum:'} {trends.historical_revenue_change_pct}% &bull; {language === 'hindi' ? 'भविष्यवाणी विश्वास:' : 'Prediction Confidence:'} {(trends.confidence * 100).toFixed(0)}%
                </p>
              </div>
              <Badge variant="info">{language === 'hindi' ? 'एआई रुझान मॉडल' : 'AI Trend Model'}</Badge>
            </div>
          )}

          <div className="bg-white rounded-xl border border-paytm-border overflow-hidden shadow-xs">
            <div className="px-5 py-3 border-b border-paytm-border flex items-center justify-between">
              <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider">
                {language === 'hindi' ? `पाई गई सांख्यिकीय राजस्व विसंगतियां (${anomalies.length})` : `Detected Statistical Revenue Anomalies (${anomalies.length})`}
              </h3>
            </div>
            {anomalies.length === 0 ? (
              <EmptyState message={language === 'hindi' ? 'वर्तमान रिकॉर्डिंग विंडो में कोई सांख्यिकीय विसंगति नहीं मिली।' : 'No statistical anomalies detected in the current recording window.'} />
            ) : (
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
                  <tr>
                    <th className="py-2.5 px-4">{language === 'hindi' ? 'तारीख' : 'Date'}</th>
                    <th className="py-2.5 px-4">{language === 'hindi' ? 'देखा गया मूल्य' : 'Observed Value'}</th>
                    <th className="py-2.5 px-4">{language === 'hindi' ? 'अपेक्षित रोलिंग माध्य' : 'Rolling Mean Expected'}</th>
                    <th className="py-2.5 px-4">{language === 'hindi' ? 'विचलन Z-स्कोर' : 'Deviation Z-Score'}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {anomalies.map((a, i) => (
                    <tr key={i} className="hover:bg-slate-50/60">
                      <td className="py-2.5 px-4 font-semibold text-paytm-dark">{a.date}</td>
                      <td className="py-2.5 px-4 font-semibold text-red-600">₹{a.observed_value.toLocaleString()}</td>
                      <td className="py-2.5 px-4 text-paytm-muted">₹{a.expected_value.toLocaleString()}</td>
                      <td className="py-2.5 px-4">
                        <Badge variant="critical">{a.deviation_score.toFixed(2)}σ</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
      {/* Record Cash Sale Modal */}
      {isCashModalOpen && (
        <Modal
          isOpen={true}
          onClose={() => {
            if (!isSubmittingCash) {
              setIsCashModalOpen(false);
              setCashSuccessMsg(null);
            }
          }}
          title={language === 'hindi' ? 'दुकान नकद बिक्री जोड़ें (Record Cash)' : 'Record Offline / Cash Sale'}
          subtitle={language === 'hindi' ? 'नकद राशि सीधे दैनिक बिक्री व भुगतान रिपोर्ट में जुड़ जाएगी' : 'Add manual cash collections directly into daily revenue & payment analytics'}
          maxWidth="md"
        >
          {cashSuccessMsg ? (
            <div className="p-6 text-center space-y-3">
              <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-900/40 rounded-full flex items-center justify-center mx-auto text-emerald-600">
                <CheckCircle2 className="w-7 h-7" />
              </div>
              <h3 className="text-base font-bold text-paytm-dark dark:text-white">
                {language === 'hindi' ? 'नकद बिक्री दर्ज हो गई!' : 'Cash Sale Recorded!'}
              </h3>
              <p className="text-xs text-paytm-muted">{cashSuccessMsg}</p>
            </div>
          ) : (
            <form onSubmit={handleRecordCashSale} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-paytm-dark dark:text-white mb-1.5">
                  {language === 'hindi' ? 'नकद राशि (₹ Amount) *' : 'Cash Amount (₹) *'}
                </label>
                <div className="relative">
                  <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-base font-extrabold text-[#002970] dark:text-[#00BAF2]">
                    ₹
                  </span>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    required
                    value={cashAmount}
                    onChange={(e) => setCashAmount(e.target.value)}
                    placeholder="0.00"
                    autoFocus
                    className="w-full pl-8 pr-4 py-2.5 text-base font-bold rounded-xl border border-paytm-border bg-white dark:bg-[#0B1528] text-paytm-dark dark:text-white focus:outline-none focus:ring-2 focus:ring-[#00BAF2]"
                  />
                </div>

                {/* Quick select chips */}
                <div className="mt-2.5 flex flex-wrap gap-1.5">
                  {[50, 100, 200, 500, 1000, 2000].map((v) => (
                    <button
                      key={v}
                      type="button"
                      onClick={() => setCashAmount((prev) => String((parseFloat(prev) || 0) + v))}
                      className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-paytm-light dark:bg-[#132342] border border-paytm-border text-[#002970] dark:text-blue-200 hover:bg-[#00BAF2]/10 hover:border-[#00BAF2] transition-colors"
                    >
                      +₹{v}
                    </button>
                  ))}
                  {cashAmount && (
                    <button
                      type="button"
                      onClick={() => setCashAmount('')}
                      className="text-xs font-medium px-2 py-1 text-red-500 hover:underline"
                    >
                      {language === 'hindi' ? 'साफ़ करें' : 'Clear'}
                    </button>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-paytm-dark dark:text-white mb-1">
                  {language === 'hindi' ? 'विवरण या सामान (वैकल्पिक Note)' : 'Item / Note (Optional)'}
                </label>
                <input
                  type="text"
                  value={cashNote}
                  onChange={(e) => setCashNote(e.target.value)}
                  placeholder={language === 'hindi' ? 'उदा. आटा, चाय, या ग्राहक का नाम' : 'e.g. Rice 5kg, Daily Groceries, or Customer Name'}
                  className="w-full px-3.5 py-2 text-xs rounded-lg border border-paytm-border bg-white dark:bg-[#0B1528] text-paytm-dark dark:text-white focus:outline-none focus:ring-2 focus:ring-[#00BAF2]"
                />
              </div>

              <div className="p-3 bg-slate-50 dark:bg-[#0F1D38] rounded-xl border border-paytm-border text-[11px] text-paytm-muted flex items-start gap-2">
                <Banknote className="w-4 h-4 text-[#00B970] shrink-0 mt-0.5" />
                <span>
                  {language === 'hindi'
                    ? 'यह नकद लेनदेन आपके कुल दैनिक संग्रह (Cash Revenue) और पेमेंट मेथड रिपोर्ट में तुरंत जुड़ जाएगा।'
                    : 'This cash transaction will immediately update your daily collections, cash ledger, and payment method share.'}
                </span>
              </div>

              <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-100 dark:border-slate-800">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setIsCashModalOpen(false)}
                  disabled={isSubmittingCash}
                >
                  {language === 'hindi' ? 'रद्द करें' : 'Cancel'}
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  isLoading={isSubmittingCash}
                  className="bg-[#00B970] hover:bg-[#008A54] text-white font-bold"
                >
                  {language === 'hindi' ? 'नकद दर्ज करें (Save Cash)' : 'Save Cash Sale'}
                </Button>
              </div>
            </form>
          )}
        </Modal>
      )}
    </div>
  );
};
