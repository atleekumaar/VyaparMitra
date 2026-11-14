import React, { useEffect, useState, useMemo } from 'react';
import {
  TrendingUp,
  Sparkles,
  Bot,
  ArrowRight,
  ShoppingBag,
  DollarSign,
  Package,
  Trophy,
  Volume2,
  Activity,
  PlusCircle,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  CreditCard,
  X,
  Upload,
} from 'lucide-react';
import { api } from '../api/client';
import {
  ActionItem,
  BenchmarkData,
  DashboardSummary,
  SalesAnalytics,
  ProductRank,
  CategoryShare,
  PaymentAnalytics,
  UserProfile,
} from '../types';
import { MetricCard } from '../components/MetricCard';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { AreaTrendChart } from '../components/charts/AreaTrendChart';
import { DonutChart } from '../components/charts/DonutChart';
import { HorizontalBarChart } from '../components/charts/HorizontalBarChart';
import { Card } from '../components/Card';
import { PageHeader } from '../components/PageHeader';
import { SectionHeader } from '../components/SectionHeader';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';
import { formatCurrency, formatNumber } from '../utils/formatters';

interface DashboardPageProps {
  onNavigateTab: (tab: any) => void;
  onSelectAction: (actionId: string) => void;
  onQuickCopilot: (query: string) => void;
  currentUser?: UserProfile | null;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigateTab,
  onSelectAction,
  onQuickCopilot,
  currentUser,
}) => {
  const { t, language } = useLanguage();

  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [actions, setActions] = useState<ActionItem[]>([]);
  const [salesAnalytics, setSalesAnalytics] = useState<SalesAnalytics | null>(null);
  const [benchmark, setBenchmark] = useState<BenchmarkData | null>(null);
  const [topProducts, setTopProducts] = useState<any[]>([]);
  const [paymentAnalytics, setPaymentAnalytics] = useState<PaymentAnalytics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Quick Action Modals
  const [isRecordSaleOpen, setIsRecordSaleOpen] = useState(false);
  const [isAddProductOpen, setIsAddProductOpen] = useState(false);
  const [isImportCsvOpen, setIsImportCsvOpen] = useState(false);

  // Record Sale Form state
  const [saleAmount, setSaleAmount] = useState('');
  const [saleProductName, setSaleProductName] = useState('');
  const [salePaymentMethod, setSalePaymentMethod] = useState<'CASH' | 'UPI' | 'CARD'>('CASH');
  const [isSubmittingSale, setIsSubmittingSale] = useState(false);

  // Add Product Form state
  const [newProductName, setNewProductName] = useState('');
  const [newProductCategory, setNewProductCategory] = useState('Groceries');
  const [newProductPrice, setNewProductPrice] = useState('');
  const [newProductStock, setNewProductStock] = useState('50');
  const [isSubmittingProduct, setIsSubmittingProduct] = useState(false);

  // Chart range state
  const [chartRange, setChartRange] = useState<'7D' | '30D' | '90D'>('7D');
  const [quickQuery, setQuickQuery] = useState('');
  const [csvEntityType, setCsvEntityType] = useState<'inventory' | 'customers' | 'sales'>('inventory');

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, actRes, salesRes, prodRes, payRes] = await Promise.all([
        api.getDashboardSummary(),
        api.getDashboardActions(5),
        api.getSalesAnalytics(),
        api.getProductAnalytics().catch(() => ({ top_performers: [] })),
        api.getPaymentAnalytics().catch(() => null),
      ]);

      setSummary(sumRes);
      setActions(actRes.actions || []);
      setSalesAnalytics(salesRes);
      setTopProducts(prodRes?.top_performers || []);
      setPaymentAnalytics(payRes);

      try {
        const benchRes = await api.getMerchantBenchmark(sumRes.merchant_id);
        setBenchmark(benchRes);
      } catch {
        // Fallback silently if benchmark not yet computed
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  // Greeting
  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    const timeGreeting =
      hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
    const firstName = currentUser?.name ? currentUser.name.split(' ')[0] : null;
    return firstName ? `${timeGreeting}, ${firstName}` : 'Welcome to VyaparMitra';
  }, [currentUser]);

  // Check onboarding progress
  const totalOrders = summary?.kpis?.orders?.value ? Number(summary.kpis.orders.value) : 0;
  const hasProducts = topProducts.length > 0;
  const hasSales = totalOrders > 0;
  const onboardingCompletedCount = 1 + (hasProducts ? 1 : 0) + (hasSales ? 1 : 0);
  const showOnboarding = onboardingCompletedCount < 3 && !summary?.demo_mode;

  // Sparkline data from daily series
  const sparklineSeries = useMemo(() => {
    if (!salesAnalytics?.daily_series) return [];
    return salesAnalytics.daily_series.slice(-7).map((d) => d.revenue);
  }, [salesAnalytics]);

  // Handle Quick Ask
  const handleQuickAsk = (e: React.FormEvent) => {
    e.preventDefault();
    if (quickQuery.trim()) {
      onQuickCopilot(quickQuery.trim());
    }
  };

  // Submit Quick Sale
  const handleRecordSaleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const amt = parseFloat(saleAmount);
    if (isNaN(amt) || amt <= 0) return;

    setIsSubmittingSale(true);
    try {
      await api.recordCashSale({
        amount: amt,
        product_name: saleProductName || 'Direct Counter Sale',
      });
      setIsRecordSaleOpen(false);
      setSaleAmount('');
      setSaleProductName('');
      await loadDashboardData();
    } catch (err: any) {
      alert(`Error recording sale: ${err?.message}`);
    } finally {
      setIsSubmittingSale(false);
    }
  };

  // Submit Quick Product
  const handleAddProductSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const price = parseFloat(newProductPrice);
    const stock = parseInt(newProductStock, 10);
    if (!newProductName.trim() || isNaN(price) || price <= 0) return;

    setIsSubmittingProduct(true);
    try {
      const pid = `SKU_${Date.now().toString().slice(-6)}`;
      await api.createInventoryItem({
        product_id: pid,
        product_name: newProductName.trim(),
        category: newProductCategory,
        selling_price: price,
        current_stock: isNaN(stock) ? 50 : stock,
      });
      setIsAddProductOpen(false);
      setNewProductName('');
      setNewProductPrice('');
      await loadDashboardData();
    } catch (err: any) {
      alert(`Error adding product: ${err?.message}`);
    } finally {
      setIsSubmittingProduct(false);
    }
  };

  // Trend data formatted for AreaTrendChart
  const trendPoints = useMemo(() => {
    if (!salesAnalytics?.daily_series) return [];
    return salesAnalytics.daily_series.map((d) => ({
      date: d.date,
      revenue: d.revenue,
      orders: d.orders,
    }));
  }, [salesAnalytics]);

  // Donut data for Payment methods
  const paymentDonutData = useMemo(() => {
    if (!paymentAnalytics?.payment_methods) return [];
    return paymentAnalytics.payment_methods.map((p) => ({
      label: p.payment_method,
      value: p.total_revenue,
      subtext: `${p.transaction_count} txns`,
    }));
  }, [paymentAnalytics]);

  // Horizontal bar data for Top Products
  const topProductsBarData = useMemo(() => {
    return topProducts.map((p) => ({
      id: p.product_id,
      label: p.product_name,
      value: p.revenue,
      category: p.category,
      subtext: `${p.units || 0} units`,
    }));
  }, [topProducts]);

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in-50 duration-200">
      {/* Top Header with Greeting & Quick Action Buttons */}
      <PageHeader
        title={greeting}
        subtitle="Bharat's intelligent retail command center — real-time sales, inventory, and AI copilot."
        badge={
          summary?.demo_mode ? (
            <Badge variant="demo" dot>
              Demo Simulation
            </Badge>
          ) : (
            <Badge variant="success" dot>
              Live Store
            </Badge>
          )
        }
        dateRange={summary?.date_range || 'Last 30 Days'}
        actions={
          <div className="flex items-center gap-2 flex-wrap">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setIsAddProductOpen(true)}
              className="gap-1.5"
            >
              <Package className="w-3.5 h-3.5 text-brand" />
              <span>Add Product</span>
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setIsImportCsvOpen(true)}
              className="gap-1.5"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-brand" />
              <span>Import CSV</span>
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsRecordSaleOpen(true)}
              className="gap-1.5 shadow-fintech"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Record Sale</span>
            </Button>
          </div>
        }
      />

      {/* Demo Simulation Alert Banner (only when in demo mode) */}
      {summary?.demo_mode && (
        <div className="rounded-2xl border border-purple-500/20 bg-purple-500/5 p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-2xs">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-text">Demo Simulation Active</span>
                <span className="text-[10px] text-purple-600 dark:text-purple-300 font-semibold px-2 py-0.5 rounded-full bg-purple-500/10">
                  Pre-loaded Data
                </span>
              </div>
              <p className="text-xs text-text-muted mt-0.5">
                VyaparMitra is showing simulated kirana benchmarks. Add a product or record a sale to switch seamlessly to your own live store books.
              </p>
            </div>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIsRecordSaleOpen(true)}
            className="shrink-0"
          >
            Record Your Real Sale
          </Button>
        </div>
      )}

      {/* 3-Step Onboarding Checklist for New Merchants */}
      {showOnboarding && (
        <Card className="border-brand/30 bg-gradient-to-r from-brand-soft/40 via-surface-card to-surface-card">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-brand">
                  Quick Store Setup
                </span>
                <span className="px-2 py-0.2 rounded-full text-[10px] font-bold bg-brand text-white">
                  {onboardingCompletedCount} of 3 completed
                </span>
              </div>
              <h3 className="text-sm font-bold text-text">Complete setup to unlock AI Copilot forecasts</h3>
              <p className="text-xs text-text-muted">
                Add your items and record your first transaction to initialize automated inventory alerts.
              </p>
            </div>

            {/* Checklist items */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-surface-card border border-border">
                <CheckCircle2 className="w-4 h-4 text-success shrink-0" />
                <span className="text-xs font-semibold text-text">1. Store Initialized</span>
              </div>

              <div
                onClick={() => setIsAddProductOpen(true)}
                className={`flex items-center gap-2 p-2.5 rounded-xl border cursor-pointer transition-all ${
                  hasProducts
                    ? 'bg-surface-card border-border'
                    : 'bg-brand-soft/50 border-brand text-brand hover:bg-brand-soft'
                }`}
              >
                {hasProducts ? (
                  <CheckCircle2 className="w-4 h-4 text-success shrink-0" />
                ) : (
                  <Package className="w-4 h-4 text-brand shrink-0" />
                )}
                <span className="text-xs font-semibold">2. Add First SKU</span>
              </div>

              <div
                onClick={() => setIsRecordSaleOpen(true)}
                className={`flex items-center gap-2 p-2.5 rounded-xl border cursor-pointer transition-all ${
                  hasSales
                    ? 'bg-surface-card border-border'
                    : 'bg-brand-soft/50 border-brand text-brand hover:bg-brand-soft'
                }`}
              >
                {hasSales ? (
                  <CheckCircle2 className="w-4 h-4 text-success shrink-0" />
                ) : (
                  <PlusCircle className="w-4 h-4 text-brand shrink-0" />
                )}
                <span className="text-xs font-semibold">3. Record First Sale</span>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* KPI Cards Row (Revenue, Orders, AOV, Units) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <MetricCard
          card={
            summary?.kpis?.revenue || {
              label: 'Total Revenue',
              value: 0,
              formatted_value: '₹0.00',
              change_pct: null,
              subtext: 'No sales recorded yet',
            }
          }
          icon={<DollarSign className="w-4 h-4 text-brand" />}
          isHero
          loading={loading}
          sparklineData={sparklineSeries}
        />
        <MetricCard
          card={
            summary?.kpis?.orders || {
              label: 'Total Orders',
              value: 0,
              formatted_value: '0',
              change_pct: null,
              subtext: 'Awaiting transactions',
            }
          }
          icon={<ShoppingBag className="w-4 h-4 text-brand" />}
          loading={loading}
          sparklineData={sparklineSeries}
        />
        <MetricCard
          card={
            summary?.kpis?.aov || {
              label: 'Average Order Value',
              value: 0,
              formatted_value: '₹0.00',
              change_pct: null,
              subtext: 'Calculated per order',
            }
          }
          icon={<TrendingUp className="w-4 h-4 text-brand" />}
          loading={loading}
        />
        <MetricCard
          card={
            summary?.kpis?.units || {
              label: 'Units Sold',
              value: 0,
              formatted_value: '0',
              change_pct: null,
              subtext: 'Inventory volume',
            }
          }
          icon={<Package className="w-4 h-4 text-brand" />}
          loading={loading}
        />
      </div>

      {/* Revenue Trend Chart & Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main 2-column Area Trend Chart */}
        <div className="lg:col-span-2">
          <AreaTrendChart
            data={trendPoints}
            title="Revenue & Daily Run-Rate"
            subtitle="Historical sales velocity and real-time transaction updates"
            range={chartRange}
            onRangeChange={setChartRange}
            loading={loading}
            error={error}
            onRetry={loadDashboardData}
            onEmptyAction={() => setIsRecordSaleOpen(true)}
            emptyActionLabel="Record Your First Sale"
          />
        </div>

        {/* 1-column Payment Split Donut */}
        <div className="lg:col-span-1">
          <DonutChart
            data={paymentDonutData}
            title="Payments Split"
            subtitle="UPI vs Cash vs Card mix"
            loading={loading}
            emptyMessage="No payment method records yet"
          />
        </div>
      </div>

      {/* Top Products & Action Center Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Performing Products */}
        <div className="lg:col-span-2">
          <HorizontalBarChart
            data={topProductsBarData}
            title="Top Performing Products"
            subtitle="Ranked by cumulative revenue"
            loading={loading}
            emptyMessage="No product sales recorded yet"
          />
        </div>

        {/* Action Center & Copilot Quick Prompt Preview */}
        <div className="lg:col-span-1 space-y-6">
          {/* Action Center Card */}
          <Card
            title="Commercial Action Center"
            subtitle="AI prioritized reorders & opportunities"
            action={
              actions.length > 0 ? (
                <button
                  type="button"
                  onClick={() => onNavigateTab('recommendations')}
                  className="text-xs font-semibold text-brand hover:underline inline-flex items-center gap-1"
                >
                  View All ({actions.length})
                  <ArrowRight className="w-3 h-3" />
                </button>
              ) : null
            }
          >
            {actions.length === 0 ? (
              <div className="py-6 text-center space-y-1">
                <CheckCircle2 className="w-8 h-8 text-success mx-auto mb-2" />
                <h4 className="text-xs font-bold text-text">Sab kuch badhiya hai!</h4>
                <p className="text-[11px] text-text-muted">
                  Abhi koi pending commercial risk ya stock-out alert nahi hai.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {actions.slice(0, 3).map((act) => (
                  <div
                    key={act.recommendation_id}
                    onClick={() => onSelectAction(act.recommendation_id)}
                    className="p-3 rounded-xl border border-border hover:border-brand bg-surface-muted/30 hover:bg-surface-card cursor-pointer transition-all space-y-1"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-text truncate max-w-[180px]">
                        {act.title}
                      </span>
                      <Badge
                        variant={
                          act.priority_band === 'CRITICAL'
                            ? 'critical'
                            : act.priority_band === 'HIGH'
                            ? 'high'
                            : 'medium'
                        }
                      >
                        {act.priority_band}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-text-muted line-clamp-1">
                      {act.action}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Copilot Quick Ask Card */}
          <Card
            title="Ask VyaparMitra Copilot"
            subtitle="Hinglish / Hindi AI business assistance"
          >
            <form onSubmit={handleQuickAsk} className="space-y-2.5">
              <div className="relative">
                <Bot className="w-4 h-4 text-brand absolute left-3 top-3" />
                <input
                  type="text"
                  value={quickQuery}
                  onChange={(e) => setQuickQuery(e.target.value)}
                  placeholder="e.g. Aaj ki sabse zyada bikne wali item?"
                  className="w-full pl-9 pr-3 py-2 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text placeholder-text-subtle focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand"
                />
              </div>
              <div className="flex items-center gap-1.5 flex-wrap">
                {[
                  'Top 5 sales?',
                  'Low stock items?',
                  'Customer Udhaar summary?',
                ].map((prompt, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => onQuickCopilot(prompt)}
                    className="px-2 py-1 text-[10px] font-semibold rounded-lg bg-surface-muted text-text-muted hover:text-text hover:bg-surface-muted/80 border border-border"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </form>
          </Card>
        </div>
      </div>

      {/* Record Sale Modal */}
      {isRecordSaleOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in-50">
          <div className="w-full max-w-md bg-surface-card rounded-2xl border border-border shadow-fintech-lg p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div className="flex items-center gap-2">
                <PlusCircle className="w-5 h-5 text-brand" />
                <h3 className="text-sm font-bold text-text">Record POS Sale</h3>
              </div>
              <button
                type="button"
                onClick={() => setIsRecordSaleOpen(false)}
                className="p-1 rounded-lg text-text-muted hover:text-text"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleRecordSaleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-text">Sale Amount (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  autoFocus
                  value={saleAmount}
                  onChange={(e) => setSaleAmount(e.target.value)}
                  placeholder="e.g. 1500"
                  className="w-full px-3.5 py-2.5 text-sm font-bold rounded-xl border border-border bg-surface-muted text-text focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand tabular-nums"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-text">Product / Description</label>
                <input
                  type="text"
                  value={saleProductName}
                  onChange={(e) => setSaleProductName(e.target.value)}
                  placeholder="e.g. Fortune Sunflower Oil 1L"
                  className="w-full px-3.5 py-2 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-text">Payment Method</label>
                <div className="grid grid-cols-3 gap-2">
                  {(['CASH', 'UPI', 'CARD'] as const).map((method) => (
                    <button
                      key={method}
                      type="button"
                      onClick={() => setSalePaymentMethod(method)}
                      className={`py-2 rounded-xl text-xs font-bold border transition-all ${
                        salePaymentMethod === method
                          ? 'border-brand bg-brand-soft text-brand shadow-xs'
                          : 'border-border text-text-muted hover:text-text'
                      }`}
                    >
                      {method}
                    </button>
                  ))}
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                className="w-full py-2.5 justify-center font-bold"
                disabled={isSubmittingSale}
              >
                {isSubmittingSale ? 'Saving...' : 'Confirm & Record Sale'}
              </Button>
            </form>
          </div>
        </div>
      )}

      {/* Add Product Modal */}
      {isAddProductOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in-50">
          <div className="w-full max-w-md bg-surface-card rounded-2xl border border-border shadow-fintech-lg p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div className="flex items-center gap-2">
                <Package className="w-5 h-5 text-brand" />
                <h3 className="text-sm font-bold text-text">Add Product to Catalog</h3>
              </div>
              <button
                type="button"
                onClick={() => setIsAddProductOpen(false)}
                className="p-1 rounded-lg text-text-muted hover:text-text"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleAddProductSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-text">Product Name</label>
                <input
                  type="text"
                  required
                  autoFocus
                  value={newProductName}
                  onChange={(e) => setNewProductName(e.target.value)}
                  placeholder="e.g. Tata Salt 1kg"
                  className="w-full px-3.5 py-2 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text">Selling Price (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={newProductPrice}
                    onChange={(e) => setNewProductPrice(e.target.value)}
                    placeholder="28"
                    className="w-full px-3.5 py-2 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand tabular-nums"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text">Initial Stock</label>
                  <input
                    type="number"
                    value={newProductStock}
                    onChange={(e) => setNewProductStock(e.target.value)}
                    placeholder="50"
                    className="w-full px-3.5 py-2 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand tabular-nums"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-text">Category</label>
                <select
                  value={newProductCategory}
                  onChange={(e) => setNewProductCategory(e.target.value)}
                  className="w-full px-3.5 py-2 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand"
                >
                  <option value="Groceries">Groceries &amp; Staples</option>
                  <option value="Snacks & Beverages">Snacks &amp; Beverages</option>
                  <option value="Personal Care">Personal Care</option>
                  <option value="Dairy & Bakery">Dairy &amp; Bakery</option>
                  <option value="Household">Household &amp; Cleaning</option>
                </select>
              </div>

              <Button
                type="submit"
                variant="primary"
                className="w-full py-2.5 justify-center font-bold"
                disabled={isSubmittingProduct}
              >
                {isSubmittingProduct ? 'Saving...' : 'Add Product'}
              </Button>
            </form>
          </div>
        </div>
      )}

      {/* Import CSV Modal */}
      {isImportCsvOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in-50">
          <div className="w-full max-w-md bg-surface-card rounded-2xl border border-border shadow-fintech-lg p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div className="flex items-center gap-2">
                <FileSpreadsheet className="w-5 h-5 text-brand" />
                <h3 className="text-sm font-bold text-text">Import Store Data via CSV</h3>
              </div>
              <button
                type="button"
                onClick={() => setIsImportCsvOpen(false)}
                className="p-1 rounded-lg text-text-muted hover:text-text"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Entity Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-text block">Data Type to Import:</label>
              <div className="grid grid-cols-3 gap-1.5 p-1 rounded-xl bg-surface-muted border border-border text-xs">
                {[
                  { id: 'inventory', label: 'Inventory / SKUs' },
                  { id: 'customers', label: 'Customers' },
                  { id: 'sales', label: 'Sales Records' },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setCsvEntityType(tab.id as any)}
                    className={`py-1.5 px-2 rounded-lg text-[11px] font-semibold transition-all ${
                      csvEntityType === tab.id
                        ? 'bg-brand text-white shadow-xs'
                        : 'text-text-muted hover:text-text'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="p-6 border-2 border-dashed border-border rounded-xl text-center space-y-2 hover:border-brand transition-colors cursor-pointer bg-surface-muted/30">
              <Upload className="w-8 h-8 text-brand mx-auto" />
              <div className="text-xs font-bold text-text">Choose CSV file or drag &amp; drop</div>
              <p className="text-[11px] text-text-muted">
                {csvEntityType === 'inventory' && 'Requires: product_name, selling_price (e.g. sample_inventory.csv)'}
                {csvEntityType === 'customers' && 'Requires: name, phone or credit_limit (e.g. sample_customers.csv)'}
                {csvEntityType === 'sales' && 'Requires: product_id, quantity (items must exist in inventory)'}
              </p>
              <input
                type="file"
                accept=".csv"
                className="hidden"
                id="csv-file-upload"
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  try {
                    // Auto-detect entity type from header if needed
                    const slice = await file.slice(0, 1024).text();
                    const firstLine = slice.split('\n')[0].toLowerCase();
                    let targetType = csvEntityType;
                    if (firstLine.includes('product_name') && firstLine.includes('selling_price')) {
                      targetType = 'inventory';
                    } else if (firstLine.includes('name') && (firstLine.includes('credit_limit') || firstLine.includes('phone') || firstLine.includes('email'))) {
                      targetType = 'customers';
                    } else if (firstLine.includes('product_id') && firstLine.includes('quantity')) {
                      targetType = 'sales';
                    }

                    const res = await api.uploadCsv(file, targetType);
                    alert(`CSV processed successfully! ${res.inserted_rows || 0} rows imported into ${targetType}.`);
                    setIsImportCsvOpen(false);
                    await loadDashboardData();
                  } catch (err: any) {
                    alert(`Import failed: ${err?.message}`);
                  }
                }}
              />
              <label
                htmlFor="csv-file-upload"
                className="inline-block mt-2 px-3 py-1.5 rounded-lg bg-brand text-white text-xs font-semibold cursor-pointer hover:bg-brand-hover shadow-xs"
              >
                Browse File
              </label>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
