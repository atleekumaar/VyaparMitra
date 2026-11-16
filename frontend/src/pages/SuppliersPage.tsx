import React, { useEffect, useState, useMemo } from 'react';
import {
  Truck,
  Building2,
  Phone,
  Mail,
  MapPin,
  CreditCard,
  PlusCircle,
  Receipt,
  CheckCircle2,
  Clock,
  Search,
  DollarSign,
  PackagePlus,
  ArrowRight,
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

interface SupplierItem {
  id: string;
  name: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  gstin?: string;
  current_payable: number;
  payment_terms?: string;
  status: string;
  created_at: string;
}

interface SupplierInvoiceItem {
  id: string;
  invoice_number: string;
  supplier_id: string;
  supplier_name: string;
  total_amount: number;
  paid_amount: number;
  unpaid_amount: number;
  status: string;
  notes?: string;
  created_at: string;
}

export const SuppliersPage: React.FC = () => {
  const { language } = useLanguage();
  const { showToast } = useToast();

  const [suppliers, setSuppliers] = useState<SupplierItem[]>([]);
  const [invoices, setInvoices] = useState<SupplierInvoiceItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<'suppliers' | 'invoices'>('suppliers');
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Modals
  const [isAddSupplierOpen, setIsAddSupplierOpen] = useState<boolean>(false);
  const [isAddInvoiceOpen, setIsAddInvoiceOpen] = useState<boolean>(false);
  const [isPaySupplierOpen, setIsPaySupplierOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Selected Supplier for Pay / Invoice
  const [selectedSupplier, setSelectedSupplier] = useState<SupplierItem | null>(null);

  // Add Supplier Form
  const [supName, setSupName] = useState('');
  const [supContact, setSupContact] = useState('');
  const [supPhone, setSupPhone] = useState('');
  const [supEmail, setSupEmail] = useState('');
  const [supAddress, setSupAddress] = useState('');
  const [supGstin, setSupGstin] = useState('');
  const [supTerms, setSupTerms] = useState('Net 15');

  // Record Invoice Form
  const [invNumber, setInvNumber] = useState('');
  const [invTotalAmount, setInvTotalAmount] = useState('');
  const [invPaidAmount, setInvPaidAmount] = useState('0');
  const [invNotes, setInvNotes] = useState('');

  // Pay Supplier Form
  const [payAmount, setPayAmount] = useState('');
  const [payMethod, setPayMethod] = useState('BANK_TRANSFER');
  const [payNotes, setPayNotes] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [supRes, invRes] = await Promise.all([
        api.getSuppliers().catch(() => ({ total_suppliers: 0, total_payables: 0, suppliers: [] })),
        api.getSupplierInvoices().catch(() => []),
      ]);
      setSuppliers(supRes.suppliers || []);
      setInvoices(invRes || []);
    } catch (err: any) {
      setError(err?.message || 'Failed to load supplier records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const totalPayables = useMemo(() => {
    return suppliers.reduce((sum, s) => sum + (s.current_payable || 0), 0);
  }, [suppliers]);

  const filteredSuppliers = useMemo(() => {
    if (!searchTerm.trim()) return suppliers;
    const term = searchTerm.toLowerCase();
    return suppliers.filter(
      (s) =>
        s.name.toLowerCase().includes(term) ||
        (s.contact_person && s.contact_person.toLowerCase().includes(term)) ||
        (s.phone && s.phone.includes(term))
    );
  }, [suppliers, searchTerm]);

  // Handlers
  const handleAddSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!supName.trim()) {
      showToast('Supplier name is required', 'warning');
      return;
    }
    setIsSubmitting(true);
    try {
      await api.createSupplier({
        name: supName.trim(),
        contact_person: supContact.trim() || undefined,
        phone: supPhone.trim() || undefined,
        email: supEmail.trim() || undefined,
        address: supAddress.trim() || undefined,
        gstin: supGstin.trim() || undefined,
        payment_terms: supTerms,
      });
      showToast(`Supplier "${supName}" registered successfully!`, 'success');
      setIsAddSupplierOpen(false);
      setSupName('');
      setSupContact('');
      setSupPhone('');
      setSupEmail('');
      setSupAddress('');
      setSupGstin('');
      loadData();
    } catch (err: any) {
      showToast(err?.message || 'Failed to add supplier', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRecordInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSupplier) return;
    const tot = parseFloat(invTotalAmount);
    const pd = parseFloat(invPaidAmount) || 0;
    if (isNaN(tot) || tot <= 0) {
      showToast('Please enter a valid invoice total amount', 'warning');
      return;
    }

    setIsSubmitting(true);
    try {
      await api.createSupplierInvoice(selectedSupplier.id, {
        invoice_number: invNumber.trim() || `PO-${Date.now().toString().slice(-6)}`,
        total_amount: tot,
        paid_amount: pd,
        notes: invNotes.trim() || undefined,
        items: [],
        auto_update_inventory: false,
      });
      showToast(`Purchase bill recorded for ${selectedSupplier.name}!`, 'success');
      setIsAddInvoiceOpen(false);
      setInvNumber('');
      setInvTotalAmount('');
      setInvPaidAmount('0');
      setInvNotes('');
      loadData();
    } catch (err: any) {
      showToast(err?.message || 'Failed to record invoice', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePaySupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSupplier) return;
    const amt = parseFloat(payAmount);
    if (isNaN(amt) || amt <= 0) {
      showToast('Please enter a valid payment amount', 'warning');
      return;
    }

    setIsSubmitting(true);
    try {
      await api.recordSupplierPayment(selectedSupplier.id, {
        amount: amt,
        payment_method: payMethod,
        notes: payNotes.trim() || undefined,
      });
      showToast(`Payment of ${formatCurrency(amt)} recorded for ${selectedSupplier.name}!`, 'success');
      setIsPaySupplierOpen(false);
      setPayAmount('');
      setPayNotes('');
      loadData();
    } catch (err: any) {
      showToast(err?.message || 'Failed to record supplier payment', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      <PageHeader
        title={language === 'hindi' ? 'सप्लायर व खरीद आर्डर' : 'Suppliers & Purchase Orders'}
        subtitle={
          language === 'hindi'
            ? 'थोक विक्रेताओं की डायरेक्टरी, खरीद इनवॉइस और देय उधारी (Payables) का प्रबंधन।'
            : 'Manage vendor directory, purchase invoices, and vendor payables settlements.'
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsAddSupplierOpen(true)}
              className="gap-1.5"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{language === 'hindi' ? 'नया सप्लायर जोड़ें' : 'Add Supplier'}</span>
            </Button>
            <Badge variant="info">
              <span className="flex items-center gap-1.5">
                <Truck className="w-3.5 h-3.5" />
                <span>{suppliers.length} Vendors</span>
              </span>
            </Badge>
          </div>
        }
      />

      {/* Summary KPI Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              {language === 'hindi' ? 'कुल पंजीकृत सप्लायर' : 'Registered Suppliers'}
            </span>
            <div className="w-8 h-8 rounded-lg bg-brand/10 text-brand flex items-center justify-center">
              <Building2 className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-text tabular-nums mt-2">
            {formatNumber(suppliers.length)}
          </p>
          <span className="text-xs text-text-muted mt-1 block">Active commercial partners</span>
        </Card>

        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              {language === 'hindi' ? 'कुल देय राशि (Payables)' : 'Outstanding Payables'}
            </span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-500 flex items-center justify-center">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-amber-600 dark:text-amber-400 tabular-nums mt-2">
            {formatCurrency(totalPayables)}
          </p>
          <span className="text-xs text-text-muted mt-1 block">Pending vendor settlement</span>
        </Card>

        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              {language === 'hindi' ? 'खरीद इनवॉइस' : 'Purchase Invoices'}
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
              <Receipt className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-text tabular-nums mt-2">
            {formatNumber(invoices.length)}
          </p>
          <span className="text-xs text-text-muted mt-1 block">Inward stock records</span>
        </Card>
      </div>

      {/* Segmented View Tabs */}
      <div className="flex items-center gap-2 border-b border-border pb-3">
        <button
          onClick={() => setActiveTab('suppliers')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'suppliers'
              ? 'bg-brand text-brand-contrast shadow-sm'
              : 'text-text-muted hover:text-text hover:bg-surface-muted'
          }`}
        >
          {language === 'hindi' ? 'सप्लायर डायरेक्टरी' : 'Suppliers Directory'}
        </button>
        <button
          onClick={() => setActiveTab('invoices')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'invoices'
              ? 'bg-brand text-brand-contrast shadow-sm'
              : 'text-text-muted hover:text-text hover:bg-surface-muted'
          }`}
        >
          {language === 'hindi' ? 'खरीद इनवॉइस लेजर' : 'Purchase Invoices'} ({invoices.length})
        </button>
      </div>

      {/* Tab 1: Suppliers Directory */}
      {activeTab === 'suppliers' && (
        <Card className="p-0 overflow-hidden space-y-4">
          <div className="p-4 sm:p-5 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 absolute left-3 top-3 text-text-muted" />
              <input
                type="text"
                placeholder={language === 'hindi' ? 'सप्लायर या फोन खोजें...' : 'Search supplier or phone...'}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              />
            </div>
          </div>

          {loading ? (
            <TableSkeleton rows={5} />
          ) : error ? (
            <ErrorBanner message={error} onRetry={loadData} />
          ) : filteredSuppliers.length === 0 ? (
            <div className="p-8">
              <EmptyState
                title="No Suppliers Found"
                message="Add your first distributor or wholesaler to track purchases and payables."
                actionText="Add Supplier"
                onAction={() => setIsAddSupplierOpen(true)}
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-muted border-b border-border text-text-muted font-bold uppercase tracking-wider">
                  <tr>
                    <th className="py-3 px-4">Supplier Name</th>
                    <th className="py-3 px-4">Contact</th>
                    <th className="py-3 px-4">City / Address</th>
                    <th className="py-3 px-4">Terms</th>
                    <th className="py-3 px-4 text-right">Outstanding Payable</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {filteredSuppliers.map((sup) => (
                    <tr key={sup.id} className="hover:bg-surface-muted/40 transition-colors">
                      <td className="py-3 px-4">
                        <div className="font-bold text-text">{sup.name}</div>
                        {sup.contact_person && (
                          <span className="text-[11px] text-text-muted block">
                            Contact: {sup.contact_person}
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-text-muted space-y-0.5">
                        {sup.phone && (
                          <div className="flex items-center gap-1.5 text-[11px]">
                            <Phone className="w-3 h-3 text-brand" />
                            <span>{sup.phone}</span>
                          </div>
                        )}
                        {sup.email && (
                          <div className="flex items-center gap-1.5 text-[11px]">
                            <Mail className="w-3 h-3 text-text-muted" />
                            <span>{sup.email}</span>
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-4 text-text-muted text-[11px]">
                        {sup.address || '—'}
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded-md bg-surface-muted border border-border text-text font-semibold text-[11px]">
                          {sup.payment_terms || 'Net 30'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-text tabular-nums">
                        <span
                          className={
                            sup.current_payable > 0
                              ? 'text-amber-600 dark:text-amber-400'
                              : 'text-text-muted'
                          }
                        >
                          {formatCurrency(sup.current_payable)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedSupplier(sup);
                              setIsAddInvoiceOpen(true);
                            }}
                            className="text-[11px] py-1 px-2.5"
                          >
                            + Bill
                          </Button>
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => {
                              setSelectedSupplier(sup);
                              setIsPaySupplierOpen(true);
                            }}
                            className="text-[11px] py-1 px-2.5"
                          >
                            Pay
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {/* Tab 2: Purchase Invoices */}
      {activeTab === 'invoices' && (
        <Card className="p-0 overflow-hidden">
          {invoices.length === 0 ? (
            <div className="p-8">
              <EmptyState
                title="No Purchase Invoices Yet"
                message="Record stock purchases to track vendor bills and payments."
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-muted border-b border-border text-text-muted font-bold uppercase tracking-wider">
                  <tr>
                    <th className="py-3 px-4">Invoice #</th>
                    <th className="py-3 px-4">Supplier</th>
                    <th className="py-3 px-4">Date</th>
                    <th className="py-3 px-4 text-right">Total Amount</th>
                    <th className="py-3 px-4 text-right">Paid</th>
                    <th className="py-3 px-4 text-right">Unpaid</th>
                    <th className="py-3 px-4 text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {invoices.map((inv) => (
                    <tr key={inv.id} className="hover:bg-surface-muted/40 transition-colors">
                      <td className="py-3 px-4 font-bold text-text">{inv.invoice_number}</td>
                      <td className="py-3 px-4 text-text font-semibold">{inv.supplier_name}</td>
                      <td className="py-3 px-4 text-text-muted tabular-nums">
                        {new Date(inv.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-text tabular-nums">
                        {formatCurrency(inv.total_amount)}
                      </td>
                      <td className="py-3 px-4 text-right text-success font-semibold tabular-nums">
                        {formatCurrency(inv.paid_amount)}
                      </td>
                      <td className="py-3 px-4 text-right text-amber-600 dark:text-amber-400 font-semibold tabular-nums">
                        {formatCurrency(inv.unpaid_amount)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Badge
                          variant={
                            inv.status === 'PAID'
                              ? 'success'
                              : inv.status === 'PARTIAL'
                              ? 'warning'
                              : 'danger'
                          }
                        >
                          {inv.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {/* Add Supplier Modal */}
      <Modal
        isOpen={isAddSupplierOpen}
        onClose={() => setIsAddSupplierOpen(false)}
        title={language === 'hindi' ? 'नया सप्लायर पंजीकृत करें' : 'Register New Supplier'}
        subtitle="Add distributor or wholesaler details for stock purchase and credit terms."
      >
        <form onSubmit={handleAddSupplier} className="space-y-4 text-xs">
          <div>
            <label className="block text-text font-semibold mb-1">Company / Supplier Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. Mahalakshmi Agro Traders"
              value={supName}
              onChange={(e) => setSupName(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-text font-semibold mb-1">Contact Person</label>
              <input
                type="text"
                placeholder="e.g. Suresh Kumar"
                value={supContact}
                onChange={(e) => setSupContact(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              />
            </div>

            <div>
              <label className="block text-text font-semibold mb-1">Mobile / Phone</label>
              <input
                type="tel"
                placeholder="+91 98765 43210"
                value={supPhone}
                onChange={(e) => setSupPhone(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-text font-semibold mb-1">Email</label>
              <input
                type="email"
                placeholder="supplier@example.com"
                value={supEmail}
                onChange={(e) => setSupEmail(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              />
            </div>

            <div>
              <label className="block text-text font-semibold mb-1">Payment Terms</label>
              <select
                value={supTerms}
                onChange={(e) => setSupTerms(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              >
                <option value="Immediate">Immediate / Cash on Delivery</option>
                <option value="Net 7">Net 7 Days</option>
                <option value="Net 15">Net 15 Days</option>
                <option value="Net 30">Net 30 Days</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-text font-semibold mb-1">GSTIN Number (Optional)</label>
            <input
              type="text"
              placeholder="e.g. 09ABCDE1234F1Z5"
              value={supGstin}
              onChange={(e) => setSupGstin(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            />
          </div>

          <div>
            <label className="block text-text font-semibold mb-1">Godown / Office Address</label>
            <input
              type="text"
              placeholder="e.g. Warehouse 12, Transport Nagar"
              value={supAddress}
              onChange={(e) => setSupAddress(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-border">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsAddSupplierOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={isSubmitting}>
              {isSubmitting ? 'Registering...' : 'Register Supplier'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Record Invoice / Purchase Bill Modal */}
      <Modal
        isOpen={isAddInvoiceOpen}
        onClose={() => setIsAddInvoiceOpen(false)}
        title={`Record Purchase Bill: ${selectedSupplier?.name || ''}`}
        subtitle="Log inward stock bill and update supplier outstanding payables."
      >
        <form onSubmit={handleRecordInvoice} className="space-y-4 text-xs">
          <div>
            <label className="block text-text font-semibold mb-1">Invoice / Bill Number *</label>
            <input
              type="text"
              required
              placeholder="e.g. INV-2026-889"
              value={invNumber}
              onChange={(e) => setInvNumber(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-text font-semibold mb-1">Total Bill Amount (₹) *</label>
              <input
                type="number"
                step="0.01"
                min="1"
                required
                placeholder="e.g. 25000"
                value={invTotalAmount}
                onChange={(e) => setInvTotalAmount(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              />
            </div>

            <div>
              <label className="block text-text font-semibold mb-1">Paid Amount Now (₹)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="0"
                value={invPaidAmount}
                onChange={(e) => setInvPaidAmount(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              />
            </div>
          </div>

          <div>
            <label className="block text-text font-semibold mb-1">Notes / Items Description</label>
            <input
              type="text"
              placeholder="e.g. 50 bags sugar, 30 boxes cooking oil"
              value={invNotes}
              onChange={(e) => setInvNotes(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-border">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsAddInvoiceOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={isSubmitting}>
              {isSubmitting ? 'Recording...' : 'Save Bill'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Pay Supplier Modal */}
      <Modal
        isOpen={isPaySupplierOpen}
        onClose={() => setIsPaySupplierOpen(false)}
        title={`Pay Supplier: ${selectedSupplier?.name || ''}`}
        subtitle={`Current outstanding payable: ${formatCurrency(selectedSupplier?.current_payable || 0)}`}
      >
        <form onSubmit={handlePaySupplier} className="space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-text font-semibold mb-1">Amount to Pay (₹) *</label>
              <input
                type="number"
                step="0.01"
                min="1"
                required
                placeholder="e.g. 5000"
                value={payAmount}
                onChange={(e) => setPayAmount(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              />
            </div>

            <div>
              <label className="block text-text font-semibold mb-1">Payment Method</label>
              <select
                value={payMethod}
                onChange={(e) => setPayMethod(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              >
                <option value="BANK_TRANSFER">Bank IMPS / NEFT</option>
                <option value="UPI">UPI</option>
                <option value="CASH">Cash</option>
                <option value="CHEQUE">Cheque</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-text font-semibold mb-1">Transaction Ref / Notes</label>
            <input
              type="text"
              placeholder="e.g. UTR / Cheque # 12903847"
              value={payNotes}
              onChange={(e) => setPayNotes(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-border">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsPaySupplierOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={isSubmitting}>
              {isSubmitting ? 'Recording...' : 'Confirm Payment'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
