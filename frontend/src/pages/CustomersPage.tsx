import React, { useEffect, useState, useMemo } from 'react';
import {
  Users,
  Filter,
  AlertTriangle,
  ShieldCheck,
  HeartHandshake,
  PhoneCall,
  Search,
  MessageSquare,
  DollarSign,
  TrendingUp,
  UserPlus,
  Upload,
  Download,
  CheckCircle2,
  Phone,
  Mail,
  MapPin,
} from 'lucide-react';
import { api } from '../api/client';
import { CustomerDetail, CustomerListItem } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { PageHeader } from '../components/PageHeader';
import { SectionHeader } from '../components/SectionHeader';
import { Modal } from '../components/Modal';
import { TableSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner, EmptyState } from '../components/EmptyState';
import { useLanguage } from '../i18n/LanguageContext';
import { useToast } from '../components/Toast';
import { localizeDynamicText } from '../i18n/translations';
import { formatCurrency, formatNumber } from '../utils/formatters';

export const CustomersPage: React.FC = () => {
  const { t, language } = useLanguage();
  const { showToast } = useToast();
  const [customers, setCustomers] = useState<CustomerListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedSegment, setSelectedSegment] = useState<string>('');
  const [selectedRisk, setSelectedRisk] = useState<string>('');
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);

  // Modals & Action States
  const [isAddCustomerOpen, setIsAddCustomerOpen] = useState<boolean>(false);
  const [isImportCsvOpen, setIsImportCsvOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Add Customer Form Fields
  const [custName, setCustName] = useState('');
  const [custPhone, setCustPhone] = useState('');
  const [custEmail, setCustEmail] = useState('');
  const [custCity, setCustCity] = useState('');
  const [custAddress, setCustAddress] = useState('');
  const [custCreditLimit, setCustCreditLimit] = useState('5000');

  // CSV Import States
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [csvUploadSuccess, setCsvUploadSuccess] = useState<string | null>(null);

  const loadCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getCustomers({
        segment: selectedSegment || undefined,
        risk_tier: selectedRisk || undefined,
        limit: 120,
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

  const handleAddCustomerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!custName.trim()) {
      showToast('Customer name is required', 'warning');
      return;
    }
    setIsSubmitting(true);
    try {
      await api.createCustomer({
        name: custName.trim(),
        phone: custPhone.trim() || undefined,
        email: custEmail.trim() || undefined,
        city: custCity.trim() || undefined,
        address: custAddress.trim() || undefined,
        credit_limit: parseFloat(custCreditLimit) || 5000,
      });
      showToast(`Customer "${custName}" added successfully!`, 'success');
      setIsAddCustomerOpen(false);
      setCustName('');
      setCustPhone('');
      setCustEmail('');
      setCustCity('');
      setCustAddress('');
      setCustCreditLimit('5000');
      loadCustomers();
    } catch (err: any) {
      showToast(err?.message || 'Failed to add customer', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCsvUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      showToast('Please select a CSV file first', 'warning');
      return;
    }
    setIsSubmitting(true);
    setCsvUploadSuccess(null);
    try {
      const res = await api.uploadCsv(selectedFile, 'customers');
      const count = res.inserted_rows || res.rows_inserted || res.total_rows || 0;
      setCsvUploadSuccess(`Successfully imported ${count} customers!`);
      showToast(`Imported ${count} customers successfully!`, 'success');
      setSelectedFile(null);
      loadCustomers();
      setTimeout(() => {
        setIsImportCsvOpen(false);
        setCsvUploadSuccess(null);
      }, 1500);
    } catch (err: any) {
      showToast(err?.message || 'CSV import failed', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenDetail = async (customerId: string) => {
    setLoadingDetail(true);
    try {
      const detail = await api.getCustomerDetail(customerId);
      setSelectedCustomer(detail);
    } catch (err: any) {
      alert(`Could not load customer detail: ${err?.message}`);
    } finally {
      setLoadingDetail(false);
    }
  };

  const filteredCustomers = useMemo(() => {
    if (!searchTerm.trim()) return customers;
    const term = searchTerm.toLowerCase();
    return customers.filter(
      (c) =>
        c.customer_id.toLowerCase().includes(term) ||
        c.segment.toLowerCase().includes(term)
    );
  }, [customers, searchTerm]);

  // Summary Metrics
  const totalSpend = useMemo(() => {
    return customers.reduce((sum, c) => sum + (c.lifetime_spend || 0), 0);
  }, [customers]);

  const highRiskCount = useMemo(() => {
    return customers.filter((c) => c.churn_risk_tier?.toLowerCase() === 'high').length;
  }, [customers]);

  const championsCount = useMemo(() => {
    return customers.filter(
      (c) => c.segment?.toLowerCase().includes('champion') || c.segment?.toLowerCase().includes('loyal')
    ).length;
  }, [customers]);

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      <PageHeader
        title={language === 'hindi' ? 'ग्राहक बुद्धिमत्ता और प्रतिधारण' : 'Customer Intelligence & Retention Ledger'}
        subtitle={
          language === 'hindi'
            ? 'एआई चर्न जोखिम स्कोरिंग, खरीद नवीनता, और प्राथमिकता प्रतिधारण आउटरीच।'
            : 'AI-driven cohort segmentation, churn prediction, purchase recency, and customer relationship management.'
        }
        actions={
          <div className="flex items-center gap-2 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsImportCsvOpen(true)}
              className="gap-1.5"
            >
              <Upload className="w-4 h-4 text-brand" />
              <span>{language === 'hindi' ? 'CSV आयात करें' : 'Import CSV'}</span>
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsAddCustomerOpen(true)}
              className="gap-1.5"
            >
              <UserPlus className="w-4 h-4" />
              <span>{language === 'hindi' ? 'नया ग्राहक जोड़ें' : 'Add Customer'}</span>
            </Button>
            <Badge variant="info">
              <span className="flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5" />
                <span>{customers.length} Patrons</span>
              </span>
            </Badge>
          </div>
        }
      />

      {/* Summary KPI Strip */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Total Patrons</span>
            <div className="w-8 h-8 rounded-lg bg-brand/10 text-brand flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-text tabular-nums mt-2">{formatNumber(customers.length)}</p>
          <span className="text-xs text-text-muted mt-1 block">Registered in khata ledger</span>
        </Card>

        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Cumulative Spend</span>
            <div className="w-8 h-8 rounded-lg bg-success/10 text-success flex items-center justify-center">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-success tabular-nums mt-2">
            {formatCurrency(totalSpend)}
          </p>
          <span className="text-xs text-text-muted mt-1 block">Lifetime customer revenue</span>
        </Card>

        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Champions / Loyal</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-text tabular-nums mt-2">{formatNumber(championsCount)}</p>
          <span className="text-xs text-text-muted mt-1 block">High frequency shoppers</span>
        </Card>

        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">At Churn Risk</span>
            <div className="w-8 h-8 rounded-lg bg-danger/10 text-danger flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-danger tabular-nums mt-2">{formatNumber(highRiskCount)}</p>
          <span className="text-xs text-text-muted mt-1 block">Requires WhatsApp outreach</span>
        </Card>
      </div>

      {/* Filter and Search Bar */}
      <Card className="p-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-text-muted absolute left-3 top-3" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search customer ID or segment..."
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-border bg-surface-muted/60 text-text focus:bg-surface focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            />
          </div>

          <div className="flex items-center gap-2.5 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-brand shrink-0" />
            <select
              value={selectedRisk}
              onChange={(e) => setSelectedRisk(e.target.value)}
              className="w-full sm:w-auto px-3 py-2 text-xs rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            >
              <option value="">{language === 'hindi' ? 'सभी चर्न स्तर' : 'All Churn Tiers'}</option>
              <option value="high">{language === 'hindi' ? 'उच्च चर्न जोखिम' : 'High Churn Risk'}</option>
              <option value="medium">{language === 'hindi' ? 'मध्यम चर्न जोखिम' : 'Medium Churn Risk'}</option>
              <option value="low">{language === 'hindi' ? 'कम चर्न जोखिम' : 'Low Churn Risk'}</option>
            </select>

            <select
              value={selectedSegment}
              onChange={(e) => setSelectedSegment(e.target.value)}
              className="w-full sm:w-auto px-3 py-2 text-xs rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            >
              <option value="">{language === 'hindi' ? 'सभी सेगमेंट' : 'All Segments'}</option>
              <option value="Champions">{language === 'hindi' ? 'चैंपियंस' : 'Champions'}</option>
              <option value="Loyal">{language === 'hindi' ? 'वफादार ग्राहक' : 'Loyal Customers'}</option>
              <option value="At Risk">{language === 'hindi' ? 'जोखिम में' : 'At Risk'}</option>
              <option value="Low Engagement">{language === 'hindi' ? 'कम जुड़ाव' : 'Low Engagement'}</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Customers Table */}
      {loading ? (
        <TableSkeleton rows={8} />
      ) : error ? (
        <ErrorBanner message={error} onRetry={loadCustomers} />
      ) : filteredCustomers.length === 0 ? (
        <Card className="p-8">
          <EmptyState
            title={customers.length === 0 ? 'No Customers in Ledger' : 'No Matching Customers'}
            message={
              customers.length === 0
                ? 'As you record sales with customer details, their spending profile, visit frequency, and retention scores will automatically compute here.'
                : 'No customers match your active filter or search criteria.'
            }
            actionText={customers.length === 0 ? undefined : 'Clear Filters'}
            onAction={() => {
              setSelectedSegment('');
              setSelectedRisk('');
              setSearchTerm('');
            }}
          />
        </Card>
      ) : (
        <Card className="overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-surface-muted border-b border-border text-text-muted font-bold uppercase tracking-wider">
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
              <tbody className="divide-y divide-border/60">
                {filteredCustomers.map((c) => (
                  <tr
                    key={c.customer_id}
                    onClick={() => handleOpenDetail(c.customer_id)}
                    className="hover:bg-surface-muted/50 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-text">{c.customer_id}</td>
                    <td className="py-3 px-4 font-semibold text-text">
                      {localizeDynamicText(c.segment, language)}
                    </td>
                    <td className="py-3 px-4 font-bold text-success tabular-nums">
                      {formatCurrency(c.lifetime_spend)}
                    </td>
                    <td className="py-3 px-4 font-medium text-text tabular-nums">{c.total_orders}</td>
                    <td className="py-3 px-4 text-text-muted tabular-nums">
                      {c.recency_days} {language === 'hindi' ? 'दिन पहले' : 'days ago'}
                    </td>
                    <td className="py-3 px-4">
                      <Badge
                        variant={
                          c.churn_risk_tier.toLowerCase() === 'high'
                            ? 'danger'
                            : c.churn_risk_tier.toLowerCase() === 'medium'
                            ? 'warning'
                            : 'success'
                        }
                      >
                        {localizeDynamicText(c.churn_risk_tier, language)}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 font-semibold text-text tabular-nums">
                      {(c.churn_probability * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenDetail(c.customer_id);
                        }}
                        className="text-xs py-1 px-2.5 font-semibold"
                      >
                        Profile
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Customer Detail Modal */}
      {selectedCustomer && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedCustomer(null)}
          title={`Patron ${selectedCustomer.customer_id} Profile`}
          subtitle={`Segment: ${localizeDynamicText(selectedCustomer.segment, language)}`}
        >
          <div className="space-y-5 text-xs text-text">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 bg-surface-muted/60 rounded-xl border border-border">
                <span className="text-[10px] uppercase font-bold text-text-muted">Lifetime Spend</span>
                <p className="text-base font-bold text-success mt-1 tabular-nums">
                  {formatCurrency(selectedCustomer.lifetime_spend)}
                </p>
              </div>
              <div className="p-3 bg-surface-muted/60 rounded-xl border border-border">
                <span className="text-[10px] uppercase font-bold text-text-muted">Completed Orders</span>
                <p className="text-base font-bold text-text mt-1 tabular-nums">{selectedCustomer.total_orders}</p>
              </div>
              <div className="p-3 bg-surface-muted/60 rounded-xl border border-border">
                <span className="text-[10px] uppercase font-bold text-text-muted">Last Visit Recency</span>
                <p className="text-base font-bold text-text mt-1 tabular-nums">
                  {selectedCustomer.recency_days} days
                </p>
              </div>
              <div className="p-3 bg-danger/10 rounded-xl border border-danger/20">
                <span className="text-[10px] uppercase font-bold text-danger">Churn Risk</span>
                <p className="text-base font-bold text-danger mt-1 tabular-nums">
                  {(selectedCustomer.churn_probability * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {/* Retention Action Suggestion */}
            <div className="p-4 rounded-xl border border-border bg-surface-muted/40 space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-text">
                <HeartHandshake className="w-4 h-4 text-brand" />
                <span>Recommended Retention Strategy (AI Engine)</span>
              </div>
              <p className="text-xs text-text leading-relaxed font-medium">
                {localizeDynamicText(
                  selectedCustomer.suggested_retention_action ||
                    'Send personalized WhatsApp offer on customer’s favorite grocery category to stimulate repurchase.',
                  language
                )}
              </p>
              <div className="pt-2 flex items-center gap-2">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    const text = encodeURIComponent(
                      `Namaste! VyaparMitra Store misses you. We have a special discount on your next visit!`
                    );
                    window.open(`https://wa.me/?text=${text}`, '_blank');
                  }}
                  className="gap-1.5"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>Send WhatsApp Message</span>
                </Button>
              </div>
            </div>

            {/* Evidence Rationale */}
            {selectedCustomer.evidence && selectedCustomer.evidence.length > 0 && (
              <div className="pt-3 border-t border-border">
                <h4 className="text-xs font-bold text-text mb-2">Audit Rationale &amp; Behavioral Evidence</h4>
                <div className="space-y-1.5">
                  {selectedCustomer.evidence.map((ev, i) => (
                    <div
                      key={i}
                      className="text-xs p-2.5 rounded-xl bg-surface-muted/50 border border-border/60 flex items-center justify-between"
                    >
                      <span className="font-semibold text-text">
                        {localizeDynamicText(ev.metric, language)}: <span className="font-normal text-text-muted">{ev.value}</span>
                      </span>
                      <span className="text-[10px] text-text-muted">{localizeDynamicText(ev.source, language)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end pt-3 border-t border-border">
              <Button variant="secondary" onClick={() => setSelectedCustomer(null)}>
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Add Customer Modal */}
      <Modal
        isOpen={isAddCustomerOpen}
        onClose={() => setIsAddCustomerOpen(false)}
        title={language === 'hindi' ? 'नया ग्राहक जोड़ें' : 'Add New Customer'}
        subtitle={
          language === 'hindi'
            ? 'खाता और उधारी लेजर के लिए ग्राहक का विवरण दर्ज करें।'
            : 'Enter customer contact and credit details for your Khata ledger.'
        }
      >
        <form onSubmit={handleAddCustomerSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block text-text font-semibold mb-1">
              {language === 'hindi' ? 'ग्राहक का नाम *' : 'Customer Full Name *'}
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Ramesh Kumar Sharma"
              value={custName}
              onChange={(e) => setCustName(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-text font-semibold mb-1">
                {language === 'hindi' ? 'मोबाइल नंबर' : 'Phone / Mobile'}
              </label>
              <div className="relative">
                <Phone className="w-3.5 h-3.5 absolute left-3 top-3 text-text-muted" />
                <input
                  type="tel"
                  placeholder="+91 98765 43210"
                  value={custPhone}
                  onChange={(e) => setCustPhone(e.target.value)}
                  className="w-full pl-8 pr-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
                />
              </div>
            </div>

            <div>
              <label className="block text-text font-semibold mb-1">
                {language === 'hindi' ? 'उधारी सीमा (₹)' : 'Credit Limit (₹)'}
              </label>
              <input
                type="number"
                min="0"
                step="500"
                placeholder="5000"
                value={custCreditLimit}
                onChange={(e) => setCustCreditLimit(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-text font-semibold mb-1">
                {language === 'hindi' ? 'ईमेल (वैकल्पिक)' : 'Email (Optional)'}
              </label>
              <div className="relative">
                <Mail className="w-3.5 h-3.5 absolute left-3 top-3 text-text-muted" />
                <input
                  type="email"
                  placeholder="ramesh@example.com"
                  value={custEmail}
                  onChange={(e) => setCustEmail(e.target.value)}
                  className="w-full pl-8 pr-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
                />
              </div>
            </div>

            <div>
              <label className="block text-text font-semibold mb-1">
                {language === 'hindi' ? 'शहर' : 'City'}
              </label>
              <div className="relative">
                <MapPin className="w-3.5 h-3.5 absolute left-3 top-3 text-text-muted" />
                <input
                  type="text"
                  placeholder="e.g. Lucknow, Delhi"
                  value={custCity}
                  onChange={(e) => setCustCity(e.target.value)}
                  className="w-full pl-8 pr-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
                />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-text font-semibold mb-1">
              {language === 'hindi' ? 'दुकान या घर का पता' : 'Address / Locality'}
            </label>
            <input
              type="text"
              placeholder="e.g. Shop 4 Market Complex, Civil Lines"
              value={custAddress}
              onChange={(e) => setCustAddress(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-text focus:outline-none focus:ring-2 focus:ring-brand font-medium"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-border">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsAddCustomerOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Add Customer'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Import Customers CSV Modal */}
      <Modal
        isOpen={isImportCsvOpen}
        onClose={() => setIsImportCsvOpen(false)}
        title={language === 'hindi' ? 'ग्राहक सूची आयात करें (CSV)' : 'Bulk Import Customers (CSV)'}
        subtitle={
          language === 'hindi'
            ? 'name, phone, email, address, city, credit_limit कॉलम वाली CSV फाइल अपलोड करें।'
            : 'Upload a CSV containing customer name, phone, address, and credit limits.'
        }
      >
        <form onSubmit={handleCsvUpload} className="space-y-4 text-xs">
          {csvUploadSuccess && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>{csvUploadSuccess}</span>
            </div>
          )}

          <div className="flex items-center justify-between px-3 py-2 bg-brand/5 border border-brand/20 rounded-xl text-xs">
            <span className="text-text-muted text-[11px]">
              Need a sample CSV template with customer data?
            </span>
            <button
              type="button"
              onClick={() => {
                const content = `name,phone,email,address,city,credit_limit\nRamesh Kumar Sharma,+919811223344,ramesh.sharma@example.com,Shop 4 Market Complex,Gurugram,10000\nSunita Verma,+919822334455,sunita.verma@example.com,B-12 Civil Lines,Jaipur,8000\nVijay Agarwal,+919833445566,vijay.agarwal@example.com,14 MG Road,Indore,15000\nPriya Patel,+919844556677,priya.patel@example.com,Navrangpura,Ahmedabad,12000\nMohammad Farhan,+919855667788,farhan.m@example.com,Hazratganj,Lucknow,6000\nAnil Joshi,+919866778899,anil.joshi@example.com,Kothrud,Pune,7500\n`;
                const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'sample_customers.csv';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
              }}
              className="inline-flex items-center gap-1 text-[11px] font-bold text-brand hover:underline"
            >
              <Download className="w-3.5 h-3.5" />
              Download Template
            </button>
          </div>

          <div className="p-6 border-2 border-dashed border-border rounded-xl flex flex-col items-center justify-center text-center space-y-2 bg-surface-muted/30">
            <Upload className="w-8 h-8 text-brand" />
            <div className="text-text font-semibold">Choose a CSV file from your computer</div>
            <p className="text-[11px] text-text-muted">
              Supported columns: <code>name, phone, email, address, city, credit_limit</code>
            </p>
            <input
              type="file"
              accept=".csv"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setSelectedFile(e.target.files[0]);
                }
              }}
              className="mt-2 text-xs text-text file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-brand file:text-brand-contrast cursor-pointer"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-border">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsImportCsvOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting || !selectedFile}
            >
              {isSubmitting ? 'Importing...' : 'Upload & Import'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
