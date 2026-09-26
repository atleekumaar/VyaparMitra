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

export const AnalyticsPage: React.FC = () => {
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
        <h2 className="text-xl font-bold text-paytm-dark">Business Intelligence & Analytics</h2>
        <p className="text-xs text-paytm-muted mt-0.5">
          Empirical sales patterns, customer segments, category distributions, and payment methods.
        </p>
      </div>

      {/* Analytics Tabs */}
      <div className="flex items-center gap-1.5 border-b border-paytm-border pb-1 overflow-x-auto text-xs font-semibold">
        {[
          { id: 'sales', label: 'Sales & Daily Series', icon: BarChart2 },
          { id: 'customers', label: 'Customer Segments', icon: Users },
          { id: 'products', label: 'Top Products & Pareto', icon: Package },
          { id: 'categories', label: 'Categories Share', icon: Layers },
          { id: 'payments', label: 'Payment Methods', icon: CreditCard },
          { id: 'anomalies', label: 'Trends & Anomalies', icon: Activity },
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
              <span className="text-xs text-paytm-muted uppercase font-medium">Total Revenue</span>
              <p className="text-xl font-bold text-paytm-dark mt-1">₹{sales.total_revenue.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">Total Orders</span>
              <p className="text-xl font-bold text-paytm-dark mt-1">{sales.total_orders.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">Average Order Value</span>
              <p className="text-xl font-bold text-paytm-dark mt-1">₹{sales.average_order_value.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">Discount Rate</span>
              <p className="text-xl font-bold text-paytm-dark mt-1">{(sales.discount_rate * 100).toFixed(1)}%</p>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-paytm-border overflow-hidden shadow-xs">
            <div className="px-5 py-3 border-b border-paytm-border flex items-center justify-between">
              <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider">
                Daily Sales Records ({sales.daily_series.length} Days)
              </h3>
            </div>
            <div className="overflow-x-auto max-h-96">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
                  <tr>
                    <th className="py-2.5 px-4">Date</th>
                    <th className="py-2.5 px-4">Revenue (₹)</th>
                    <th className="py-2.5 px-4">Orders</th>
                    <th className="py-2.5 px-4">Avg Order Value</th>
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
              <span className="text-xs text-paytm-muted uppercase font-medium">Total Patrons</span>
              <p className="text-xl font-bold text-paytm-dark mt-1">{customers.total_customers.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">High Churn Risk</span>
              <p className="text-xl font-bold text-red-600 mt-1">{customers.high_risk_count.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">Medium Risk</span>
              <p className="text-xl font-bold text-amber-600 mt-1">{customers.medium_risk_count.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl border border-paytm-border p-4">
              <span className="text-xs text-paytm-muted uppercase font-medium">Low Churn Risk</span>
              <p className="text-xl font-bold text-emerald-600 mt-1">{customers.low_risk_count.toLocaleString()}</p>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-paytm-border p-5 shadow-xs">
            <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider mb-4">
              RFM Segmentation & Commercial Contribution
            </h3>
            <div className="space-y-4">
              {customers.segments.map((seg, idx) => (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-medium">
                    <span className="text-paytm-dark font-semibold">{seg.segment_name}</span>
                    <span className="text-paytm-muted">
                      {seg.customer_count} customers &bull; ₹{seg.total_revenue.toLocaleString()} ({(seg.revenue_share * 100).toFixed(1)}%)
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
              <span className="text-xs text-paytm-muted uppercase font-medium">Pareto Concentration</span>
              <p className="text-base font-bold text-paytm-dark mt-0.5">
                Top 20% products contribute ~{((products.pareto_80_20_ratio || 0.8) * 100).toFixed(0)}% of store sales
              </p>
            </div>
            <Badge variant="info">Total SKUs: {products.total_products_tracked}</Badge>
          </div>

          <div className="bg-white rounded-xl border border-paytm-border overflow-hidden shadow-xs">
            <div className="px-5 py-3 border-b border-paytm-border">
              <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider">Top 15 Revenue Drivers</h3>
            </div>
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
                <tr>
                  <th className="py-2.5 px-4">Rank</th>
                  <th className="py-2.5 px-4">Product ID</th>
                  <th className="py-2.5 px-4">Category</th>
                  <th className="py-2.5 px-4">Revenue</th>
                  <th className="py-2.5 px-4">Units Sold</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {products.top_performers.map((p) => (
                  <tr key={p.product_id} className="hover:bg-slate-50/60">
                    <td className="py-2.5 px-4 font-bold text-paytm-blue">#{p.rank}</td>
                    <td className="py-2.5 px-4 font-medium text-paytm-dark">{p.product_name}</td>
                    <td className="py-2.5 px-4 text-paytm-muted">{p.category}</td>
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
              Product Category Revenue & Order Shares
            </h3>
          </div>
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
              <tr>
                <th className="py-2.5 px-4">Category</th>
                <th className="py-2.5 px-4">Revenue (₹)</th>
                <th className="py-2.5 px-4">Orders</th>
                <th className="py-2.5 px-4">Share of Revenue</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {categories.map((c, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60">
                  <td className="py-2.5 px-4 font-semibold text-paytm-dark">{c.category}</td>
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
          <div className="bg-white rounded-xl border border-paytm-border p-4 flex items-center justify-between">
            <div>
              <span className="text-xs text-paytm-muted uppercase font-medium">Primary Payment Mode</span>
              <p className="text-xl font-bold text-paytm-dark mt-0.5">{payments.primary_payment_method}</p>
            </div>
            <Badge variant="success">Fintech Settlement Ready</Badge>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {payments.payment_methods.map((pm, idx) => (
              <div key={idx} className="bg-white rounded-xl border border-paytm-border p-5">
                <span className="text-xs font-semibold text-paytm-muted uppercase">{pm.payment_method}</span>
                <p className="text-2xl font-bold text-paytm-dark mt-2">₹{pm.total_revenue.toLocaleString()}</p>
                <div className="mt-3 flex items-center justify-between text-xs text-paytm-muted">
                  <span>{pm.transaction_count} transactions</span>
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
                <span className="text-xs font-semibold text-paytm-muted uppercase">Business Momentum</span>
                <p className="text-base font-bold text-paytm-dark mt-1">
                  Expected Trend: <span className="text-paytm-blue">{trends.predicted_trend}</span> ({trends.horizon_days}-day horizon)
                </p>
                <p className="text-xs text-paytm-muted mt-0.5">
                  Historical revenue momentum: {trends.historical_revenue_change_pct}% &bull; Prediction Confidence: {(trends.confidence * 100).toFixed(0)}%
                </p>
              </div>
              <Badge variant="info">Phase 3 Trend Model</Badge>
            </div>
          )}

          <div className="bg-white rounded-xl border border-paytm-border overflow-hidden shadow-xs">
            <div className="px-5 py-3 border-b border-paytm-border flex items-center justify-between">
              <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider">
                Detected Statistical Revenue Anomalies ({anomalies.length})
              </h3>
            </div>
            {anomalies.length === 0 ? (
              <EmptyState message="No statistical anomalies detected in the current recording window." />
            ) : (
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
                  <tr>
                    <th className="py-2.5 px-4">Date</th>
                    <th className="py-2.5 px-4">Observed Value</th>
                    <th className="py-2.5 px-4">Rolling Mean Expected</th>
                    <th className="py-2.5 px-4">Deviation Z-Score</th>
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
    </div>
  );
};
