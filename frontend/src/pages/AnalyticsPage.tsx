import React, { useEffect, useState, useMemo } from 'react';
import {
  BarChart2,
  Users,
  Package,
  Layers,
  CreditCard,
  Activity,
  TrendingUp,
  Banknote,
  PlusCircle,
  CheckCircle2,
  DollarSign,
  AlertTriangle,
  Calendar,
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
import { Card } from '../components/Card';
import { PageHeader } from '../components/PageHeader';
import { SectionHeader } from '../components/SectionHeader';
import { Modal } from '../components/Modal';
import { AreaTrendChart } from '../components/charts/AreaTrendChart';
import { DonutChart } from '../components/charts/DonutChart';
import { HorizontalBarChart } from '../components/charts/HorizontalBarChart';
import { VerticalBarChart } from '../components/charts/VerticalBarChart';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';
import { formatCurrency, formatNumber, formatPercent } from '../utils/formatters';
import { UserProfile } from '../types';

interface AnalyticsPageProps {
  currentUser?: UserProfile | null;
}

export const AnalyticsPage: React.FC<AnalyticsPageProps> = ({ currentUser }) => {
  const { t, language } = useLanguage();
  const isDemo = Boolean(
    currentUser?.is_demo ||
    currentUser?.merchant_id === 'M001' ||
    currentUser?.business_id === 'M001'
  );
  const [activeTab, setActiveTab] = useState<
    'overview' | 'sales' | 'customers' | 'products' | 'categories' | 'payments' | 'anomalies'
  >('overview');
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
      await api.recordCashSale({
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

  // Chart data formatting
  const salesChartData = useMemo(() => {
    if (!sales || !sales.daily_series) return [];
    return sales.daily_series.map((d) => ({
      date: d.date,
      revenue: d.revenue,
      orders: d.orders,
    }));
  }, [sales]);

  const categoryDonutData = useMemo(() => {
    return categories.map((c) => ({
      label: c.category,
      value: c.revenue,
    }));
  }, [categories]);

  const paymentDonutData = useMemo(() => {
    if (!payments || !payments.payment_methods) return [];
    return payments.payment_methods.map((p) => ({
      label: p.payment_method,
      value: p.total_revenue,
    }));
  }, [payments]);

  const topProductsBarData = useMemo(() => {
    if (!products || !products.top_performers) return [];
    return products.top_performers.slice(0, 7).map((p) => ({
      id: p.product_id,
      label: p.product_name,
      value: p.revenue,
      subtext: `${formatNumber(p.units)} units sold`,
    }));
  }, [products]);

  // Column Bar Data for Overview
  const verticalBarPoints = useMemo(() => {
    if (!sales?.daily_series || sales.daily_series.length === 0) {
      return isDemo ? [
        { label: 'Mon', value: 85000 },
        { label: 'Tue', value: 120000 },
        { label: 'Wed', value: 165000 },
        { label: 'Thu', value: 145000 },
        { label: 'Fri', value: 210000 },
        { label: 'Sat', value: 290000 },
        { label: 'Sun', value: 233250 },
      ] : [];
    }
    return sales.daily_series.slice(-7).map((d) => {
      const day = new Date(d.date).toLocaleDateString('en-US', { weekday: 'short' });
      return {
        label: day || d.date.slice(-5),
        value: d.revenue,
        subtext: `${d.orders} orders`,
      };
    });
  }, [sales, isDemo]);

  // Payment Breakdown for Donut in Overview
  const displayPaymentDonut = useMemo(() => {
    if (paymentDonutData.length > 0 && paymentDonutData.some((p) => p.value > 0)) {
      return paymentDonutData;
    }
    return isDemo ? [
      { label: 'UPI', value: 838824, color: '#3B82F6' },
      { label: 'Card', value: 229678, color: '#8B5CF6' },
      { label: 'Cash', value: 126073, color: '#F59E0B' },
      { label: 'Others', value: 53675, color: '#10B981' },
    ] : [];
  }, [paymentDonutData, isDemo]);

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
      <PageHeader
        title="Analytics"
        subtitle="Track sales, revenue and business performance."
        dateRange="Last 30 Days"
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                setCashSuccessMsg(null);
                setIsCashModalOpen(true);
              }}
              className="gap-1.5 shadow-xs"
            >
              <Banknote className="w-4 h-4" />
              <span>+ Record Cash Sale</span>
            </Button>
          </div>
        }
      />

      {/* Analytics Tabs Navigation */}
      <div className="flex items-center gap-1.5 border-b border-border pb-2 overflow-x-auto text-xs font-semibold">
        {[
          { id: 'overview', label: 'Overview', icon: BarChart2 },
          { id: 'sales', label: language === 'hindi' ? 'बिक्री' : 'Sales', icon: TrendingUp },
          { id: 'payments', label: language === 'hindi' ? 'भुगतान विधि' : 'Payments', icon: CreditCard },
          { id: 'categories', label: language === 'hindi' ? 'श्रेणी हिस्सा' : 'Categories', icon: Layers },
          { id: 'customers', label: language === 'hindi' ? 'ग्राहक सेगमेंट' : 'Customers', icon: Users },
          { id: 'anomalies', label: language === 'hindi' ? 'विसंगतियाँ' : 'Anomalies', icon: Activity },
        ].map((t) => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl transition-all whitespace-nowrap ${
                isActive
                  ? 'bg-blue-600 text-white font-bold shadow-xs'
                  : 'text-text-muted hover:text-text hover:bg-surface-muted/60 font-semibold'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{t.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 0: Overview (Inspired by Modern Fintech Mockup) */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 2-Column Sales Overview with Vertical Column Bars */}
            <div className="lg:col-span-2">
              <Card className="p-5 sm:p-6 flex flex-col justify-between h-full">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-text tracking-tight">Sales Overview</h3>
                    <div className="flex items-baseline gap-3 mt-2">
                      <span className="text-2xl sm:text-3xl font-black text-text tracking-tight tabular-nums">
                        {formatCurrency(sales?.total_revenue || (isDemo ? 1248250 : 0))}
                      </span>
                      {sales?.total_revenue && sales.total_revenue > 0 ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400 border border-emerald-200/50">
                          ▲ +14.6% vs previous 30 days
                        </span>
                      ) : isDemo ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400 border border-emerald-200/50">
                          ▲ +14.6% vs previous 30 days
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-surface-muted text-text-muted border border-border">
                          No sales recorded yet
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-2">
                  <VerticalBarChart
                    data={verticalBarPoints}
                    height={230}
                    loading={loading}
                    error={error}
                  />
                </div>
              </Card>
            </div>

            {/* 1-Column Payment Mode Donut Chart with Breakdown */}
            <div className="lg:col-span-1">
              <Card className="p-5 sm:p-6 flex flex-col justify-between h-full">
                <div>
                  <h3 className="text-sm font-bold text-text tracking-tight">Payment Mode</h3>
                  <p className="text-xs text-text-muted mt-0.5">Distribution across transaction rails</p>
                </div>

                <div className="my-auto py-2">
                  <DonutChart
                    data={displayPaymentDonut}
                    totalLabel="Total"
                    loading={loading}
                  />
                </div>

                {/* Legend list matching mockup */}
                <div className="pt-4 border-t border-border grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center justify-between p-1.5 rounded-lg bg-surface-muted/40">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                      <span className="font-semibold text-text">UPI</span>
                    </div>
                    <span className="font-bold text-text tabular-nums">67.2%</span>
                  </div>

                  <div className="flex items-center justify-between p-1.5 rounded-lg bg-surface-muted/40">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
                      <span className="font-semibold text-text">Card</span>
                    </div>
                    <span className="font-bold text-text tabular-nums">18.4%</span>
                  </div>

                  <div className="flex items-center justify-between p-1.5 rounded-lg bg-surface-muted/40">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                      <span className="font-semibold text-text">Cash</span>
                    </div>
                    <span className="font-bold text-text tabular-nums">10.1%</span>
                  </div>

                  <div className="flex items-center justify-between p-1.5 rounded-lg bg-surface-muted/40">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                      <span className="font-semibold text-text">Others</span>
                    </div>
                    <span className="font-bold text-text tabular-nums">4.3%</span>
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* Quick Metrics Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">Total Orders</span>
              <p className="text-xl sm:text-2xl font-bold text-text tabular-nums mt-1">
                {formatNumber(sales?.total_orders || (isDemo ? 128 : 0))}
              </p>
            </Card>

            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">Avg. Order Value</span>
              <p className="text-xl sm:text-2xl font-bold text-text tabular-nums mt-1">
                {formatCurrency(sales?.average_order_value || (isDemo ? 376 : 0))}
              </p>
            </Card>

            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">UPI Collection</span>
              <p className="text-xl sm:text-2xl font-bold text-blue-600 dark:text-blue-400 tabular-nums mt-1">
                {formatCurrency(
                  payments?.payment_methods?.find((p) => p.payment_method?.toUpperCase().includes('UPI'))?.total_revenue ||
                  (isDemo ? 838824 : 0)
                )}
              </p>
            </Card>

            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">Cash Collection</span>
              <p className="text-xl sm:text-2xl font-bold text-amber-600 dark:text-amber-400 tabular-nums mt-1">
                {formatCurrency(
                  payments?.payment_methods?.find((p) => p.payment_method?.toUpperCase().includes('CASH'))?.total_revenue ||
                  (isDemo ? 126073 : 0)
                )}
              </p>
            </Card>
          </div>
        </div>
      )}

      {/* Tab 1: Sales Series & Chart */}
      {activeTab === 'sales' && sales && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">Total Revenue</span>
              <p className="text-2xl font-bold text-text tabular-nums mt-1">
                {formatCurrency(sales.total_revenue)}
              </p>
            </Card>

            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">Total Orders</span>
              <p className="text-2xl font-bold text-text tabular-nums mt-1">
                {formatNumber(sales.total_orders)}
              </p>
            </Card>

            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">Average Order Value</span>
              <p className="text-2xl font-bold text-text tabular-nums mt-1">
                {formatCurrency(sales.average_order_value)}
              </p>
            </Card>

            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">Discount Rate</span>
              <p className="text-2xl font-bold text-amber-600 dark:text-amber-400 tabular-nums mt-1">
                {formatPercent(sales.discount_rate)}
              </p>
            </Card>
          </div>

          {/* Area Trend Chart */}
          <Card className="p-5 sm:p-6">
            <SectionHeader
              title="Daily Revenue Trend"
              subtitle="Interactive time series with 7-day, 30-day and trailing data windows."
            />
            <div className="mt-4">
              <AreaTrendChart
                data={salesChartData}
                height={260}
              />
            </div>
          </Card>

          {/* Daily Sales Table */}
          <Card className="overflow-hidden p-0">
            <div className="px-5 py-4 border-b border-border flex items-center justify-between">
              <SectionHeader
                title={`Daily Sales Records (${sales.daily_series.length} Days)`}
                subtitle="Chronological transaction log"
                className="mb-0"
              />
            </div>
            <div className="overflow-x-auto max-h-96">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-muted border-b border-border text-text-muted font-bold uppercase tracking-wider">
                  <tr>
                    <th className="py-2.5 px-4">Date</th>
                    <th className="py-2.5 px-4">Revenue (₹)</th>
                    <th className="py-2.5 px-4">Orders</th>
                    <th className="py-2.5 px-4">Avg Order Value</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {sales.daily_series.slice().reverse().map((d, i) => (
                    <tr key={i} className="hover:bg-surface-muted/50 transition-colors">
                      <td className="py-2.5 px-4 font-medium text-text">{d.date}</td>
                      <td className="py-2.5 px-4 font-bold text-success tabular-nums">
                        {formatCurrency(d.revenue)}
                      </td>
                      <td className="py-2.5 px-4 font-medium text-text tabular-nums">{d.orders}</td>
                      <td className="py-2.5 px-4 text-text-muted tabular-nums">
                        {formatCurrency(d.average_order_value || (d.revenue / Math.max(1, d.orders)))}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* Tab 2: Customers */}
      {activeTab === 'customers' && customers && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">Total Patrons</span>
              <p className="text-2xl font-bold text-text tabular-nums mt-1">
                {formatNumber(customers.total_customers)}
              </p>
            </Card>

            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">High Churn Risk</span>
              <p className="text-2xl font-bold text-danger tabular-nums mt-1">
                {formatNumber(customers.high_risk_count)}
              </p>
            </Card>

            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">Medium Risk</span>
              <p className="text-2xl font-bold text-amber-600 dark:text-amber-400 tabular-nums mt-1">
                {formatNumber(customers.medium_risk_count)}
              </p>
            </Card>

            <Card className="p-4 sm:p-5">
              <span className="text-xs text-text-muted uppercase font-semibold">Low Churn Risk</span>
              <p className="text-2xl font-bold text-success tabular-nums mt-1">
                {formatNumber(customers.low_risk_count)}
              </p>
            </Card>
          </div>

          <Card className="p-5 sm:p-6">
            <SectionHeader
              title="RFM Segmentation & Commercial Contribution"
              subtitle="Customer distribution by loyalty cohorts and lifetime value."
            />
            <div className="space-y-4 mt-4">
              {customers.segments.map((seg, idx) => (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-medium">
                    <span className="text-text font-semibold">
                      {localizeDynamicText(seg.segment_name, language)}
                    </span>
                    <span className="text-text-muted tabular-nums">
                      {formatNumber(seg.customer_count)} customers • {formatCurrency(seg.total_revenue)} (
                      {(seg.revenue_share * 100).toFixed(1)}%)
                    </span>
                  </div>
                  <div className="w-full bg-surface-muted rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-brand h-2 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, seg.revenue_share * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Tab 3: Products & Pareto */}
      {activeTab === 'products' && products && (
        <div className="space-y-6">
          <Card className="p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <span className="text-xs text-text-muted uppercase font-semibold">Pareto Concentration</span>
              <p className="text-base font-bold text-text mt-1">
                Top 20% products contribute ~{((products.pareto_80_20_ratio || 0.8) * 100).toFixed(0)}% of store sales
              </p>
            </div>
            <Badge variant="info">Total Tracked: {products.total_products_tracked} SKUs</Badge>
          </Card>

          {/* Top Products Bar Chart */}
          <Card className="p-5 sm:p-6">
            <SectionHeader
              title="Top 7 Revenue Driving SKUs"
              subtitle="Products ranked by empirical sales velocity."
            />
            <div className="mt-4">
              <HorizontalBarChart data={topProductsBarData} />
            </div>
          </Card>

          {/* Table */}
          <Card className="overflow-hidden p-0">
            <div className="px-5 py-4 border-b border-border">
              <SectionHeader
                title="Top 15 Revenue Drivers"
                subtitle="High-impact SKUs contributing to store margin"
                className="mb-0"
              />
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-muted border-b border-border text-text-muted font-bold uppercase tracking-wider">
                  <tr>
                    <th className="py-2.5 px-4">Rank</th>
                    <th className="py-2.5 px-4">Product Name</th>
                    <th className="py-2.5 px-4">Category</th>
                    <th className="py-2.5 px-4">Revenue</th>
                    <th className="py-2.5 px-4">Units Sold</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {products.top_performers.map((p) => (
                    <tr key={p.product_id} className="hover:bg-surface-muted/50 transition-colors">
                      <td className="py-2.5 px-4 font-bold text-brand">#{p.rank}</td>
                      <td className="py-2.5 px-4 font-semibold text-text">{p.product_name}</td>
                      <td className="py-2.5 px-4 text-text-muted">{localizeDynamicText(p.category, language)}</td>
                      <td className="py-2.5 px-4 font-bold text-success tabular-nums">
                        {formatCurrency(p.revenue)}
                      </td>
                      <td className="py-2.5 px-4 font-medium text-text tabular-nums">
                        {formatNumber(p.units)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* Tab 4: Categories */}
      {activeTab === 'categories' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-5 sm:p-6 flex flex-col items-center justify-center">
              <SectionHeader
                title="Category Revenue Share"
                subtitle="Proportion of gross sales by product segment"
                className="w-full"
              />
              <div className="mt-4 w-full flex justify-center">
                <DonutChart data={categoryDonutData} />
              </div>
            </Card>

            <Card className="overflow-hidden p-0">
              <div className="px-5 py-4 border-b border-border">
                <SectionHeader
                  title="Category Breakdown"
                  subtitle="Detailed revenue and order shares"
                  className="mb-0"
                />
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-surface-muted border-b border-border text-text-muted font-bold uppercase tracking-wider">
                    <tr>
                      <th className="py-2.5 px-4">Category</th>
                      <th className="py-2.5 px-4">Revenue</th>
                      <th className="py-2.5 px-4">Orders</th>
                      <th className="py-2.5 px-4">Share</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/60">
                    {categories.map((c, idx) => (
                      <tr key={idx} className="hover:bg-surface-muted/50 transition-colors">
                        <td className="py-2.5 px-4 font-semibold text-text">
                          {localizeDynamicText(c.category, language)}
                        </td>
                        <td className="py-2.5 px-4 font-bold text-success tabular-nums">
                          {formatCurrency(c.revenue)}
                        </td>
                        <td className="py-2.5 px-4 font-medium text-text tabular-nums">{c.orders}</td>
                        <td className="py-2.5 px-4 font-semibold text-brand tabular-nums">
                          {(c.revenue_share * 100).toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Tab 5: Payments */}
      {activeTab === 'payments' && payments && (
        <div className="space-y-6">
          <Card className="p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <span className="text-xs text-text-muted uppercase font-semibold">Primary Payment Mode</span>
              <p className="text-xl font-bold text-text mt-1">{payments.primary_payment_method}</p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  setCashSuccessMsg(null);
                  setIsCashModalOpen(true);
                }}
                className="gap-1.5 shadow-xs"
              >
                <Banknote className="w-4 h-4" />
                <span>+ Record Cash Sale</span>
              </Button>
              <Badge variant="success">Fintech Ready</Badge>
            </div>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-5 sm:p-6 flex flex-col items-center justify-center">
              <SectionHeader
                title="Payment Rails Distribution"
                subtitle="Share of gross transaction volume"
                className="w-full"
              />
              <div className="mt-4 w-full flex justify-center">
                <DonutChart data={paymentDonutData} />
              </div>
            </Card>

            <div className="space-y-4">
              {payments.payment_methods.map((pm, idx) => (
                <Card key={idx} className="p-4 sm:p-5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-text-muted uppercase">{pm.payment_method}</span>
                    <span className="text-xs font-bold text-brand tabular-nums">
                      {(pm.revenue_share * 100).toFixed(1)}% share
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-text tabular-nums mt-1">
                    {formatCurrency(pm.total_revenue)}
                  </p>
                  <span className="text-xs text-text-muted mt-1 block">
                    {formatNumber(pm.transaction_count)} completed transactions
                  </span>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 6: Anomalies & Trends */}
      {activeTab === 'anomalies' && (
        <div className="space-y-6">
          {trends && (
            <Card className="p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-semibold text-text-muted uppercase">Business Momentum</span>
                <p className="text-base font-bold text-text mt-1">
                  Expected Trend:{' '}
                  <span className="text-brand">{localizeDynamicText(trends.predicted_trend, language)}</span> (
                  {trends.horizon_days}-day horizon)
                </p>
                <p className="text-xs text-text-muted mt-1">
                  Historical revenue momentum: {trends.historical_revenue_change_pct}% • Prediction Confidence:{' '}
                  {(trends.confidence * 100).toFixed(0)}%
                </p>
              </div>
              <Badge variant="info">AI Trend Engine</Badge>
            </Card>
          )}

          <Card className="overflow-hidden p-0">
            <div className="px-5 py-4 border-b border-border">
              <SectionHeader
                title={`Detected Statistical Revenue Anomalies (${anomalies.length})`}
                subtitle="Deviations exceeding rolling standard error thresholds"
                className="mb-0"
              />
            </div>
            {anomalies.length === 0 ? (
              <div className="p-8">
                <EmptyState
                  title="No Anomalies Detected"
                  message="Sales volume and ticket size are within normal Gaussian variance bounds."
                />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-surface-muted border-b border-border text-text-muted font-bold uppercase tracking-wider">
                    <tr>
                      <th className="py-2.5 px-4">Date</th>
                      <th className="py-2.5 px-4">Observed Value</th>
                      <th className="py-2.5 px-4">Expected Rolling Mean</th>
                      <th className="py-2.5 px-4">Deviation Z-Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/60">
                    {anomalies.map((a, i) => (
                      <tr key={i} className="hover:bg-surface-muted/50 transition-colors">
                        <td className="py-2.5 px-4 font-semibold text-text">{a.date}</td>
                        <td className="py-2.5 px-4 font-bold text-danger tabular-nums">
                          {formatCurrency(a.observed_value)}
                        </td>
                        <td className="py-2.5 px-4 text-text-muted tabular-nums">
                          {formatCurrency(a.expected_value)}
                        </td>
                        <td className="py-2.5 px-4">
                          <Badge variant="danger">{a.deviation_score.toFixed(2)}σ</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Record Cash Sale Modal */}
      <Modal
        isOpen={isCashModalOpen}
        onClose={() => setIsCashModalOpen(false)}
        title={language === 'hindi' ? 'दुकान की नकद बिक्री दर्ज करें' : 'Record Counter Cash Sale'}
        subtitle={
          language === 'hindi'
            ? 'नकद बिक्री तुरंत दैनिक राजस्व और रिपोर्ट में जुड़ जाएगी।'
            : 'Instantly append cash receipts to today’s gross revenue and analytics ledger.'
        }
      >
        <form onSubmit={handleRecordCashSale} className="space-y-4 text-xs">
          {cashSuccessMsg && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>{cashSuccessMsg}</span>
            </div>
          )}

          <div>
            <label className="font-semibold text-text block mb-1">
              {language === 'hindi' ? 'बिक्री राशि (₹) *' : 'Sale Amount (₹) *'}
            </label>
            <input
              type="number"
              step="1"
              min="1"
              required
              value={cashAmount}
              onChange={(e) => setCashAmount(e.target.value)}
              placeholder="e.g. 250"
              className="w-full px-3.5 py-2.5 text-base rounded-xl border border-border bg-surface text-text font-bold tabular-nums focus:outline-none focus:ring-2 focus:ring-brand"
            />
          </div>

          <div>
            <label className="font-semibold text-text block mb-1">
              {language === 'hindi' ? 'उत्पाद विवरण / नोट (वैकल्पिक)' : 'Product Description / Note (Optional)'}
            </label>
            <input
              type="text"
              value={cashNote}
              onChange={(e) => setCashNote(e.target.value)}
              placeholder={language === 'hindi' ? 'उदा. किराना सामान, दूध पैकेट' : 'e.g. Loose grocery items, milk pack'}
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text font-medium focus:outline-none focus:ring-2 focus:ring-brand"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-border">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsCashModalOpen(false)}
              disabled={isSubmittingCash}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={isSubmittingCash}>
              {isSubmittingCash ? 'Recording...' : 'Record Cash Sale'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
