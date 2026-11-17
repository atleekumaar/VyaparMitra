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
  Download,
  Barcode,
  Scan,
  Printer,
} from 'lucide-react';
import { ReceiptModal, ReceiptData } from '../components/ReceiptModal';
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
  const [lastReceipt, setLastReceipt] = useState<ReceiptData | null>(null);
  const [isReceiptOpen, setIsReceiptOpen] = useState<boolean>(false);

  // Record Sale Form state
  const [saleAmount, setSaleAmount] = useState('');
  const [saleProductName, setSaleProductName] = useState('');
  const [selectedProductId, setSelectedProductId] = useState('');
  const [saleQuantity, setSaleQuantity] = useState(1);
  const [salePaymentMethod, setSalePaymentMethod] = useState<'CASH' | 'UPI' | 'CARD' | 'CREDIT'>('CASH');
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
    return firstName ? `${timeGreeting}, ${firstName} ☀️` : `${timeGreeting} ☀️`;
  }, [currentUser]);

  // Check if current merchant is the preloaded demo persona (Rajesh Sharma / M001)
  const isDemo = Boolean(
    currentUser?.is_demo ||
    summary?.demo_mode ||
    currentUser?.merchant_id === 'M001' ||
    currentUser?.business_id === 'M001' ||
    currentUser?.id === 'M001'
  );

  // UPI / Digital collection calculation for KPI card
  const upiStats = useMemo(() => {
    const totalRev = Number(summary?.kpis?.revenue?.value || 0);
    const upiItem = paymentAnalytics?.payment_methods?.find(
      (p) => p.payment_method?.toUpperCase().includes('UPI')
    );

    // Non-demo users with 0 sales must strictly show 0
    if (!isDemo && totalRev === 0) {
      return {
        value: 0,
        formatted_value: '₹0.00',
        subtext: 'No sales recorded yet',
      };
    }

    const upiRev = upiItem ? upiItem.total_revenue : (isDemo ? 32400 : 0);
    const totalPaymentMethods =
      paymentAnalytics?.payment_methods?.reduce((acc, p) => acc + p.total_revenue, 0) || totalRev;
    const pct = totalPaymentMethods > 0 ? Math.round((upiRev / totalPaymentMethods) * 100) : (isDemo ? 67 : 0);

    return {
      value: upiRev,
      formatted_value: formatCurrency(upiRev),
      subtext: totalPaymentMethods > 0 ? `${pct}% of sales` : 'No sales recorded yet',
    };
  }, [paymentAnalytics, summary, isDemo]);

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

  // Submit POS Sale with atomic database transaction and stock deduction
  const handleRecordSaleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const amt = parseFloat(saleAmount);
    if (isNaN(amt) || amt <= 0) {
      alert('Please enter a valid sale price greater than 0.');
      return;
    }
    if (saleQuantity <= 0) {
      alert('Quantity must be at least 1.');
      return;
    }

    setIsSubmittingSale(true);
    try {
      // Resolve product ID or ensure SKU in inventory
      let targetPid = selectedProductId;
      if (!targetPid) {
        const found = topProducts.find((p) => p.product_name.toLowerCase() === (saleProductName || '').toLowerCase());
        if (found) {
          targetPid = found.product_id;
        } else {
          // If product doesn't exist, create it in inventory first so stock and catalog stay consistent
          const newSku = `SKU_${Date.now().toString().slice(-6)}`;
          await api.createInventoryItem({
            product_id: newSku,
            product_name: saleProductName || 'Counter Sale Item',
            category: 'Counter Sale',
            selling_price: amt,
            unit_cost: Math.round(amt * 0.7 * 100) / 100,
            current_stock: Math.max(50, saleQuantity * 5),
          });
          targetPid = newSku;
        }
      }

      // Execute atomic POS checkout transaction via operational backend API
      const saleRes = await api.createSale({
        payment_method: salePaymentMethod,
        customer_name: 'Walk-in Customer',
        items: [
          {
            product_id: targetPid,
            product_name: saleProductName || 'Counter Sale Item',
            quantity: saleQuantity,
            unit_price: amt,
          },
        ],
      });

      setIsRecordSaleOpen(false);

      // Compute GST invoice breakup (2.5% CGST + 2.5% SGST)
      const totalVal = saleRes.total_amount || (amt * saleQuantity);
      const taxSubtotal = Math.round((totalVal / 1.05) * 100) / 100;
      const taxHalf = Math.round(((totalVal - taxSubtotal) / 2) * 100) / 100;

      setLastReceipt({
        invoiceNumber: saleRes.invoice_number || `INV-${Date.now().toString().slice(-6)}`,
        storeName: currentUser?.storeName || summary?.merchant_name || 'Vyapar Store',
        storeAddress: 'Main Market Road',
        storeCity: currentUser?.city || 'India',
        storePhone: currentUser?.phone,
        items: [
          {
            name: saleProductName || 'Counter Sale Item',
            quantity: saleQuantity,
            price: amt,
            total: totalVal,
          },
        ],
        subtotal: taxSubtotal,
        cgst: taxHalf,
        sgst: taxHalf,
        totalAmount: totalVal,
        paymentMethod: salePaymentMethod,
        timestamp: saleRes.created_at || new Date().toISOString(),
      });
      setIsReceiptOpen(true);

      setSaleAmount('');
      setSaleProductName('');
      setSelectedProductId('');
      setSaleQuantity(1);
      await loadDashboardData();
    } catch (err: any) {
      alert(`POS Checkout Error: ${err?.message || 'Transaction failed'}`);
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
        unit_cost: Math.round(price * 0.8 * 100) / 100,
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
        subtitle="Here's how your business is performing today."
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

      {/* KPI Cards Row (Revenue, Orders, AOV, UPI Collection) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <MetricCard
          card={
            summary?.kpis?.revenue || {
              label: 'Revenue',
              value: isDemo ? 48250 : 0,
              formatted_value: isDemo ? '₹48,250' : '₹0.00',
              change_pct: isDemo ? 12.8 : null,
              subtext: isDemo ? '+12.8% vs last week' : 'No sales recorded yet',
            }
          }
          icon={<ShoppingBag className="w-4 h-4 text-blue-600 dark:text-blue-400" />}
          variant="blue"
          isHero
          loading={loading}
          sparklineData={sparklineSeries}
        />
        <MetricCard
          card={
            summary?.kpis?.orders || {
              label: 'Orders',
              value: isDemo ? 128 : 0,
              formatted_value: isDemo ? '128' : '0',
              change_pct: isDemo ? 6.2 : null,
              subtext: isDemo ? '+6.2% vs last week' : 'Awaiting first transaction',
            }
          }
          icon={<Package className="w-4 h-4 text-purple-600 dark:text-purple-400" />}
          variant="purple"
          loading={loading}
          sparklineData={sparklineSeries}
        />
        <MetricCard
          card={
            summary?.kpis?.aov || {
              label: 'Avg. Order Value',
              value: isDemo ? 376 : 0,
              formatted_value: isDemo ? '₹376' : '₹0.00',
              change_pct: isDemo ? 4.1 : null,
              subtext: isDemo ? '+4.1% vs last week' : 'Calculated after first sale',
            }
          }
          icon={<TrendingUp className="w-4 h-4 text-amber-600 dark:text-amber-400" />}
          variant="amber"
          loading={loading}
        />
        <MetricCard
          card={{
            label: 'UPI Collection',
            value: upiStats.value,
            formatted_value: upiStats.formatted_value,
            change_pct: null,
            subtext: upiStats.subtext,
          }}
          icon={<CreditCard className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />}
          variant="emerald"
          loading={loading}
        />
      </div>

      {/* Sales Trend & AI Insight Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main 2-column Area Trend Chart */}
        <div className="lg:col-span-2">
          <AreaTrendChart
            data={trendPoints}
            title="Sales Trend"
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

        {/* 1-column AI Insight Card */}
        <div className="lg:col-span-1 flex flex-col">
          <div className="bg-gradient-to-br from-purple-500/10 via-surface-card to-indigo-500/5 rounded-2xl border border-purple-500/20 p-5 sm:p-6 shadow-fintech flex flex-col justify-between h-full relative overflow-hidden group">
            <div className="absolute -top-10 -right-10 w-36 h-36 bg-purple-500/10 rounded-full blur-2xl pointer-events-none" />

            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-7 h-7 rounded-lg bg-purple-500/20 text-purple-600 dark:text-purple-400 flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                </div>
                <h3 className="text-sm font-bold text-text tracking-tight flex items-center gap-1.5">
                  AI Insight
                </h3>
              </div>

              <p className="text-xs text-text-muted leading-relaxed mt-2 font-medium">
                {actions.length > 0
                  ? `${actions[0].title}: ${actions[0].reason}`
                  : isDemo
                  ? "Demand for packaged goods is increasing. Consider restocking top 3 items to maximize weekend margins."
                  : "Welcome to your digital store! Add items to inventory and record transactions to generate live AI insights."}
              </p>

              {actions.length > 0 && actions[0].expected_impact > 0 && (
                <div className="mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
                  <span>Est. Impact: +{formatCurrency(actions[0].expected_impact)}</span>
                </div>
              )}
            </div>

            <div className="pt-4 mt-4 border-t border-purple-500/15 flex items-center justify-between">
              <span className="text-[11px] font-semibold text-purple-600 dark:text-purple-400">
                Action Recommended
              </span>
              <button
                type="button"
                onClick={() => {
                  if (actions.length > 0) {
                    onSelectAction(actions[0].recommendation_id);
                  } else {
                    onNavigateTab('recommendations');
                  }
                }}
                className="w-8.5 h-8.5 rounded-full bg-purple-600 hover:bg-purple-700 text-white flex items-center justify-center transition-all shadow-xs hover:scale-105"
                title="View in Action Center"
              >
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
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
              {topProducts.length > 0 && (
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-semibold text-text">Barcode / Quick Product</label>
                    <span className="text-[10px] text-text-muted flex items-center gap-1 font-semibold">
                      <Barcode className="w-3.5 h-3.5 text-brand" />
                      <span>Auto-fills Details</span>
                    </span>
                  </div>
                  <select
                    value={selectedProductId}
                    onChange={(e) => {
                      const pid = e.target.value;
                      setSelectedProductId(pid);
                      const found = topProducts.find((p) => p.product_id === pid);
                      if (found) {
                        setSaleProductName(found.product_name);
                        const unitRate = found.units > 0 ? Math.round((found.revenue / found.units) * 100) / 100 : 50;
                        setSaleAmount(String(unitRate));
                      }
                    }}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-border bg-surface-muted text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
                  >
                    <option value="">-- Select from Catalog or Type below --</option>
                    {topProducts.map((p) => (
                      <option key={p.product_id} value={p.product_id}>
                        {p.product_name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-text">Product / Item Description</label>
                <input
                  type="text"
                  required
                  value={saleProductName}
                  onChange={(e) => {
                    setSaleProductName(e.target.value);
                    if (selectedProductId) setSelectedProductId('');
                  }}
                  placeholder="e.g. Fortune Sunflower Oil 1L"
                  className="w-full px-3.5 py-2 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text">Unit Price (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    required
                    value={saleAmount}
                    onChange={(e) => setSaleAmount(e.target.value)}
                    placeholder="e.g. 150"
                    className="w-full px-3.5 py-2 text-sm font-bold rounded-xl border border-border bg-surface-muted text-text focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand tabular-nums"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text">Quantity</label>
                  <input
                    type="number"
                    min="1"
                    step="1"
                    required
                    value={saleQuantity}
                    onChange={(e) => setSaleQuantity(Math.max(1, parseInt(e.target.value, 10) || 1))}
                    className="w-full px-3.5 py-2 text-sm font-bold rounded-xl border border-border bg-surface-muted text-text focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand tabular-nums"
                  />
                </div>
              </div>

              {/* Total Calculation Preview */}
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-surface-muted border border-border/80 text-xs">
                <span className="font-semibold text-text-muted">Total Payable:</span>
                <span className="font-black text-sm text-text tabular-nums">
                  {formatCurrency((parseFloat(saleAmount) || 0) * (saleQuantity || 1))}
                </span>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-text">Payment Method</label>
                <div className="grid grid-cols-4 gap-2">
                  {(['CASH', 'UPI', 'CARD', 'CREDIT'] as const).map((method) => (
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
                      {method === 'CREDIT' ? 'Khata' : method}
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

            <div className="flex items-center justify-between px-3 py-2 bg-brand/5 border border-brand/20 rounded-xl text-xs">
              <span className="text-text-muted text-[11px]">
                {csvEntityType === 'inventory' && 'Products, categories, price & stock'}
                {csvEntityType === 'customers' && 'Customer names, phone & credit limits'}
                {csvEntityType === 'sales' && 'Product sales, quantities & payment mode'}
              </span>
              <button
                type="button"
                onClick={() => {
                  let content = '';
                  let filename = `sample_${csvEntityType}.csv`;
                  if (csvEntityType === 'inventory') {
                    content = `product_id,product_name,category,selling_price,unit_cost,current_stock,min_stock_threshold,barcode,unit\nPRD_TATA_SALT,Tata Salt 1kg,Groceries,28,22,85,15,8901030381029,pkt\nPRD_FORTUNE_OIL,Fortune Sunflower Oil 1L,Edible Oils,165,138,42,10,8906007281014,btl\nPRD_ATTA_5KG,Aashirvaad Shudh Chakki Atta 5kg,Staples,245,210,30,8,8901030012345,bag\nPRD_AMUL_BUTTER,Amul Butter 500g,Dairy,280,248,24,6,8901262010053,pkt\nPRD_PARLE_G,Parle-G Glucose Biscuits 250g,Snacks & Bakery,30,24,120,25,8901719101019,pkt\nPRD_MAGGI,Maggi 2-Minute Masala Noodles 280g,Instant Foods,56,45,95,20,8901058852372,pkt\nPRD_DETTOL_SOAP,Dettol Original Bathing Soap 125g,Personal Care,58,46,60,12,8901396312450,pcs\n`;
                  } else if (csvEntityType === 'sales') {
                    content = `product_id,product_name,quantity,unit_price,payment_method,customer_name,discount\nPRD_TATA_SALT,Tata Salt 1kg,2,28,UPI,Ramesh Kumar,0\nPRD_FORTUNE_OIL,Fortune Sunflower Oil 1L,1,165,UPI,Sunita Verma,0\nPRD_ATTA_5KG,Aashirvaad Shudh Chakki Atta 5kg,1,245,CASH,Walk-in Customer,0\nPRD_AMUL_BUTTER,Amul Butter 500g,2,280,UPI,Vijay Agarwal,10\nPRD_PARLE_G,Parle-G Glucose Biscuits 250g,5,30,CASH,Walk-in Customer,0\nPRD_MAGGI,Maggi 2-Minute Masala Noodles 280g,4,56,UPI,Priya Patel,0\nPRD_DETTOL_SOAP,Dettol Original Bathing Soap 125g,2,58,CASH,Mohammad Farhan,0\n`;
                  } else {
                    content = `name,phone,email,address,city,credit_limit\nRamesh Kumar Sharma,+919811223344,ramesh.sharma@example.com,Shop 4 Market Complex,Gurugram,10000\nSunita Verma,+919822334455,sunita.verma@example.com,B-12 Civil Lines,Jaipur,8000\nVijay Agarwal,+919833445566,vijay.agarwal@example.com,14 MG Road,Indore,15000\nPriya Patel,+919844556677,priya.patel@example.com,Navrangpura,Ahmedabad,12000\n`;
                  }
                  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
                  const url = URL.createObjectURL(blob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = filename;
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                  URL.revokeObjectURL(url);
                }}
                className="inline-flex items-center gap-1 text-[11px] font-bold text-brand hover:underline"
              >
                <Download className="w-3.5 h-3.5" />
                Template
              </button>
            </div>

            <div className="p-6 border-2 border-dashed border-border rounded-xl text-center space-y-2 hover:border-brand transition-colors cursor-pointer bg-surface-muted/30">
              <Upload className="w-8 h-8 text-brand mx-auto" />
              <div className="text-xs font-bold text-text">Choose CSV file or drag &amp; drop</div>
              <p className="text-[11px] text-text-muted">
                Select your <code>.csv</code> file or use the template above.
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
                    // Auto-detect entity type from header
                    const slice = await file.slice(0, 2048).text();
                    const firstLine = slice.split(/[\r\n]+/)[0].toLowerCase().trim();
                    let targetType = csvEntityType;

                    const hasStock = firstLine.includes('current_stock') || firstLine.includes('min_stock') || firstLine.includes('barcode');
                    const hasSales = firstLine.includes('quantity') || firstLine.includes('qty') || firstLine.includes('payment') || firstLine.includes('discount');
                    const hasCust = firstLine.includes('credit_limit') || ((firstLine.includes('phone') || firstLine.includes('email')) && firstLine.includes('name'));

                    if (hasStock && !hasSales) {
                      targetType = 'inventory';
                    } else if (hasCust && !hasSales && !hasStock) {
                      targetType = 'customers';
                    } else if (hasSales) {
                      targetType = 'sales';
                    } else if (firstLine.includes('selling_price') && (firstLine.includes('product') || firstLine.includes('item'))) {
                      targetType = 'inventory';
                    }

                    const res = await api.uploadCsv(file, targetType);
                    if (res.failed_rows > 0) {
                      alert(`Import completed with warnings: ${res.inserted_rows} rows imported, ${res.failed_rows} skipped.`);
                    } else {
                      alert(`CSV processed successfully! ${res.inserted_rows || 0} rows imported into ${targetType}.`);
                    }
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

      {/* Printable Thermal Receipt Modal */}
      <ReceiptModal
        isOpen={isReceiptOpen}
        onClose={() => setIsReceiptOpen(false)}
        receipt={lastReceipt}
      />
    </div>
  );
};
