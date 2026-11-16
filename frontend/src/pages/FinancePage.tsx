import React, { useEffect, useState, useMemo } from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Receipt,
  PlusCircle,
  CreditCard,
  Building2,
  Calendar,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
  PieChart,
} from 'lucide-react';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Badge } from '../components/Badge';
import { PageHeader } from '../components/PageHeader';
import { Modal } from '../components/Modal';
import { TableSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner, EmptyState } from '../components/EmptyState';
import { useLanguage } from '../i18n/LanguageContext';
import { useToast } from '../components/Toast';
import { formatCurrency, formatNumber } from '../utils/formatters';

interface FinanceSummary {
  business_id: string;
  total_sales_revenue: number;
  cost_of_goods_sold: number;
  gross_profit: number;
  gross_profit_margin_pct: number;
  total_operational_expenses: number;
  net_profit: number;
  net_profit_margin_pct: number;
  total_receivables_khata: number;
  total_payables_suppliers: number;
  cash_inflow: number;
  cash_outflow: number;
}

interface ExpenseItem {
  id: string;
  category: string;
  amount: number;
  payment_method: string;
  description?: string;
  created_at: string;
}

export const FinancePage: React.FC = () => {
  const { language } = useLanguage();
  const { showToast } = useToast();

  const [summary, setSummary] = useState<FinanceSummary | null>(null);
  const [expenses, setExpenses] = useState<ExpenseItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filter & Modal State
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [isAddExpenseOpen, setIsAddExpenseOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // New Expense Form Fields
  const [expCategory, setExpCategory] = useState<string>('UTILITY');
  const [expAmount, setExpAmount] = useState<string>('');
  const [expPaymentMethod, setExpPaymentMethod] = useState<string>('UPI');
  const [expDescription, setExpDescription] = useState<string>('');

  const loadFinanceData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, expRes] = await Promise.all([
        api.getFinanceSummary().catch(() => null),
        api.getExpenses({ limit: 100 }).catch(() => ({ total_count: 0, total_expenses: 0, expenses: [] })),
      ]);

      if (sumRes) {
        setSummary(sumRes);
      }
      if (expRes && expRes.expenses) {
        setExpenses(expRes.expenses);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load financial records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFinanceData();
  }, []);

  const handleRecordExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    const amt = parseFloat(expAmount);
    if (isNaN(amt) || amt <= 0) {
      showToast('Please enter a valid expense amount', 'warning');
      return;
    }

    setIsSubmitting(true);
    try {
      await api.createExpense({
        category: expCategory,
        amount: amt,
        payment_method: expPaymentMethod,
        description: expDescription.trim() || undefined,
      });

      showToast(`Expense of ${formatCurrency(amt)} recorded!`, 'success');
      setIsAddExpenseOpen(false);
      setExpAmount('');
      setExpDescription('');
      loadFinanceData();
    } catch (err: any) {
      showToast(err?.message || 'Failed to record expense', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredExpenses = useMemo(() => {
    if (selectedCategory === 'ALL') return expenses;
    return expenses.filter(
      (exp) => exp.category.toUpperCase() === selectedCategory.toUpperCase()
    );
  }, [expenses, selectedCategory]);

  const isNetProfitPositive = (summary?.net_profit || 0) >= 0;

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      <PageHeader
        title={language === 'hindi' ? 'वित्त व लाभ-हानि लेजर' : 'Finance, Profit & Loss'}
        subtitle={
          language === 'hindi'
            ? 'दुकान की कुल बिक्री, माल की लागत (COGS), परिचालन खर्च और शुद्ध लाभ का ब्यौरा।'
            : 'Track revenue, Cost of Goods Sold (COGS), operating expenses, and net profit margins.'
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsAddExpenseOpen(true)}
              className="gap-1.5"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{language === 'hindi' ? 'खर्च दर्ज करें' : 'Record Expense'}</span>
            </Button>
            <Badge variant={isNetProfitPositive ? 'success' : 'danger'}>
              {isNetProfitPositive ? (
                <span className="flex items-center gap-1">
                  <ArrowUpRight className="w-3.5 h-3.5" />
                  <span>Profitable</span>
                </span>
              ) : (
                <span className="flex items-center gap-1">
                  <ArrowDownRight className="w-3.5 h-3.5" />
                  <span>Net Loss</span>
                </span>
              )}
            </Badge>
          </div>
        }
      />

      {/* Financial Health KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Gross Sales */}
        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              {language === 'hindi' ? 'कुल बिक्री (राजस्व)' : 'Total Revenue'}
            </span>
            <div className="w-8 h-8 rounded-lg bg-brand/10 text-brand flex items-center justify-center">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-text tabular-nums mt-2">
            {formatCurrency(summary?.total_sales_revenue || 0)}
          </p>
          <span className="text-xs text-text-muted mt-1 block">
            COGS: {formatCurrency(summary?.cost_of_goods_sold || 0)}
          </span>
        </Card>

        {/* Gross Profit */}
        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              {language === 'hindi' ? 'सकल लाभ (Gross Profit)' : 'Gross Profit'}
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 tabular-nums mt-2">
            {formatCurrency(summary?.gross_profit || 0)}
          </p>
          <span className="text-xs text-text-muted mt-1 block">
            Margin: {(summary?.gross_profit_margin_pct || 0).toFixed(1)}%
          </span>
        </Card>

        {/* Operating Expenses */}
        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              {language === 'hindi' ? 'परिचालन खर्च' : 'Operating Expenses'}
            </span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-500 flex items-center justify-center">
              <Receipt className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-amber-600 dark:text-amber-400 tabular-nums mt-2">
            {formatCurrency(summary?.total_operational_expenses || 0)}
          </p>
          <span className="text-xs text-text-muted mt-1 block">
            {expenses.length} store expense items
          </span>
        </Card>

        {/* Net Profit */}
        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              {language === 'hindi' ? 'शुद्ध लाभ (Net Profit)' : 'Net Profit'}
            </span>
            <div
              className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                isNetProfitPositive
                  ? 'bg-success/10 text-success'
                  : 'bg-danger/10 text-danger'
              }`}
            >
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <p
            className={`text-2xl font-bold tabular-nums mt-2 ${
              isNetProfitPositive ? 'text-success' : 'text-danger'
            }`}
          >
            {formatCurrency(summary?.net_profit || 0)}
          </p>
          <span className="text-xs text-text-muted mt-1 block">
            Net Margin: {(summary?.net_profit_margin_pct || 0).toFixed(1)}%
          </span>
        </Card>
      </div>

      {/* Balance Sheet Dues (Receivables vs Payables) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-5 border-l-4 border-l-emerald-500">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-text-muted uppercase tracking-wider block">
                {language === 'hindi' ? 'उधारी वसूली (ग्राहक खाता बकाया)' : 'Receivables (Customer Khata Dues)'}
              </span>
              <p className="text-2xl font-bold text-text tabular-nums mt-1.5">
                {formatCurrency(summary?.total_receivables_khata || 0)}
              </p>
              <p className="text-xs text-text-muted mt-1">
                Outstanding credit extended to registered shop patrons.
              </p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
              <CreditCard className="w-6 h-6" />
            </div>
          </div>
        </Card>

        <Card className="p-5 border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-text-muted uppercase tracking-wider block">
                {language === 'hindi' ? 'सप्लायर बकाया (देय राशि)' : 'Payables (Vendor Dues)'}
              </span>
              <p className="text-2xl font-bold text-text tabular-nums mt-1.5">
                {formatCurrency(summary?.total_payables_suppliers || 0)}
              </p>
              <p className="text-xs text-text-muted mt-1">
                Pending supplier invoices to be settled.
              </p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-500 flex items-center justify-center">
              <Building2 className="w-6 h-6" />
            </div>
          </div>
        </Card>
      </div>

      {/* Expenses Breakdown & Ledger */}
      <Card className="p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-4">
          <div>
            <h3 className="text-base font-bold text-text">
              {language === 'hindi' ? 'दुकान खर्च विवरण' : 'Store Expense Ledger'}
            </h3>
            <p className="text-xs text-text-muted mt-0.5">
              Categorized business expenditures (Rent, Salary, Utilities, Logistics).
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-text-muted font-medium">Category:</span>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-1.5 text-xs rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            >
              <option value="ALL">All Categories</option>
              <option value="RENT">Rent</option>
              <option value="SALARY">Staff Salaries</option>
              <option value="UTILITY">Electricity / Water</option>
              <option value="PURCHASE">Stock Purchases</option>
              <option value="LOGISTICS">Transport & Logistics</option>
              <option value="MAINTENANCE">Shop Maintenance</option>
              <option value="MARKETING">Marketing & Offers</option>
              <option value="OTHER">Other Expenses</option>
            </select>
          </div>
        </div>

        {loading ? (
          <TableSkeleton rows={5} />
        ) : error ? (
          <ErrorBanner message={error} onRetry={loadFinanceData} />
        ) : filteredExpenses.length === 0 ? (
          <EmptyState
            title="No Expenses Recorded"
            message="Click 'Record Expense' to log shop rent, utilities, salaries, or supplier outlays."
            actionText="Record First Expense"
            onAction={() => setIsAddExpenseOpen(true)}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-surface-muted border-b border-border text-text-muted font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Description</th>
                  <th className="py-3 px-4">Payment Method</th>
                  <th className="py-3 px-4 text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {filteredExpenses.map((exp) => (
                  <tr key={exp.id} className="hover:bg-surface-muted/40 transition-colors">
                    <td className="py-3 px-4 text-text-muted tabular-nums">
                      {new Date(exp.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 font-bold text-text">
                      <span className="px-2 py-0.5 rounded-md bg-brand/10 text-brand text-[11px]">
                        {exp.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-text font-medium">
                      {exp.description || '—'}
                    </td>
                    <td className="py-3 px-4 text-text-muted uppercase text-[11px]">
                      {exp.payment_method}
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-text tabular-nums">
                      {formatCurrency(exp.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Record Expense Modal */}
      <Modal
        isOpen={isAddExpenseOpen}
        onClose={() => setIsAddExpenseOpen(false)}
        title={language === 'hindi' ? 'नया खर्च दर्ज करें' : 'Record Business Expense'}
        subtitle={
          language === 'hindi'
            ? 'दुकान के परिचालन खर्च का विवरण भरें।'
            : 'Enter expense amount, payment channel, and operational category.'
        }
      >
        <form onSubmit={handleRecordExpense} className="space-y-4 text-xs">
          <div>
            <label className="block text-text font-semibold mb-1">
              Expense Category *
            </label>
            <select
              value={expCategory}
              onChange={(e) => setExpCategory(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            >
              <option value="UTILITY">Electricity / Power / Water</option>
              <option value="RENT">Store Rent</option>
              <option value="SALARY">Employee Salary</option>
              <option value="PURCHASE">Inventory / Stock Purchase</option>
              <option value="LOGISTICS">Delivery & Logistics</option>
              <option value="MAINTENANCE">Shop Repair & Maintenance</option>
              <option value="MARKETING">Marketing & Banners</option>
              <option value="OTHER">Other Operational Expense</option>
            </select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-text font-semibold mb-1">
                Amount (₹) *
              </label>
              <input
                type="number"
                step="0.01"
                min="1"
                required
                placeholder="e.g. 1500"
                value={expAmount}
                onChange={(e) => setExpAmount(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              />
            </div>

            <div>
              <label className="block text-text font-semibold mb-1">
                Payment Channel
              </label>
              <select
                value={expPaymentMethod}
                onChange={(e) => setExpPaymentMethod(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              >
                <option value="UPI">UPI (PhonePe / GPay / Paytm)</option>
                <option value="CASH">Cash in Hand</option>
                <option value="BANK_TRANSFER">Bank NEFT / IMPS</option>
                <option value="CHEQUE">Cheque</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-text font-semibold mb-1">
              Description / Notes
            </label>
            <input
              type="text"
              placeholder="e.g. Electricity bill for November 2026"
              value={expDescription}
              onChange={(e) => setExpDescription(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-border">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsAddExpenseOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={isSubmitting}>
              {isSubmitting ? 'Recording...' : 'Save Expense'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
