import React, { useEffect, useState } from 'react';
import { Users, Filter, AlertTriangle, ShieldCheck, HeartHandshake, PhoneCall } from 'lucide-react';
import { api } from '../api/client';
import { CustomerDetail, CustomerListItem } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Modal } from '../components/Modal';
import { TableSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner, EmptyState } from '../components/EmptyState';

export const CustomersPage: React.FC = () => {
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
          <h2 className="text-xl font-bold text-paytm-dark">Customer Intelligence & Retention</h2>
          <p className="text-xs text-paytm-muted mt-0.5">
            Phase 3 churn risk scoring, purchase recency, and prioritized retention outreach.
          </p>
        </div>
        <Badge variant="info">Monitored Customers: {customers.length}</Badge>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-paytm-border p-4 flex flex-wrap items-center gap-3 shadow-xs">
        <Filter className="w-4 h-4 text-slate-400" />
        <select
          value={selectedRisk}
          onChange={(e) => setSelectedRisk(e.target.value)}
          className="px-3 py-2 text-xs rounded-lg border border-paytm-border bg-white text-paytm-text focus:outline-none focus:ring-2 focus:ring-paytm-blue"
        >
          <option value="">All Churn Tiers</option>
          <option value="high">High Churn Risk</option>
          <option value="medium">Medium Churn Risk</option>
          <option value="low">Low Churn Risk</option>
        </select>

        <select
          value={selectedSegment}
          onChange={(e) => setSelectedSegment(e.target.value)}
          className="px-3 py-2 text-xs rounded-lg border border-paytm-border bg-white text-paytm-text focus:outline-none focus:ring-2 focus:ring-paytm-blue"
        >
          <option value="">All Segments</option>
          <option value="Champions">Champions</option>
          <option value="Loyal">Loyal Customers</option>
          <option value="At Risk">At Risk</option>
          <option value="Low Engagement">Low Engagement</option>
        </select>

        <Button variant="secondary" size="sm" onClick={loadCustomers}>
          Filter
        </Button>
      </div>

      {/* Customers Table */}
      {loading ? (
        <TableSkeleton rows={8} />
      ) : error ? (
        <ErrorBanner message={error} onRetry={loadCustomers} />
      ) : customers.length === 0 ? (
        <EmptyState
          title="No Customers Match Filters"
          message="No records found matching the selected segment or risk tier."
          actionText="Clear Filters"
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
                  <th className="py-3 px-4">Customer ID</th>
                  <th className="py-3 px-4">Segment</th>
                  <th className="py-3 px-4">Lifetime Spend</th>
                  <th className="py-3 px-4">Orders</th>
                  <th className="py-3 px-4">Recency (Days)</th>
                  <th className="py-3 px-4">Churn Risk Tier</th>
                  <th className="py-3 px-4">Inactivity Prob.</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {customers.map((c) => (
                  <tr key={c.customer_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono font-semibold text-paytm-dark">{c.customer_id}</td>
                    <td className="py-3 px-4 font-medium text-paytm-text">{c.segment}</td>
                    <td className="py-3 px-4 font-semibold text-emerald-700">₹{c.lifetime_spend.toLocaleString()}</td>
                    <td className="py-3 px-4">{c.total_orders}</td>
                    <td className="py-3 px-4 text-paytm-muted">{c.recency_days} days ago</td>
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
                        {c.churn_risk_tier}
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
                        Retention Profile
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
          title={`Customer ${selectedCustomer.customer_id} — Retention Profile`}
          subtitle={`Segment: ${selectedCustomer.segment}`}
          footer={
            <Button variant="secondary" size="sm" onClick={() => setSelectedCustomer(null)}>
              Close
            </Button>
          }
        >
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-paytm-muted">Lifetime Spend</span>
              <p className="text-base font-bold text-paytm-dark mt-0.5">₹{selectedCustomer.lifetime_spend.toLocaleString()}</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-paytm-muted">Completed Orders</span>
              <p className="text-base font-bold text-paytm-dark mt-0.5">{selectedCustomer.total_orders}</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-paytm-muted">Days Since Last Visit</span>
              <p className="text-base font-bold text-paytm-dark mt-0.5">{selectedCustomer.recency_days} days</p>
            </div>
            <div className="p-3 bg-red-50 rounded-lg border border-red-100">
              <span className="text-[10px] uppercase font-bold text-red-800">Churn Probability</span>
              <p className="text-base font-bold text-red-700 mt-0.5">{(selectedCustomer.churn_probability * 100).toFixed(1)}%</p>
            </div>
          </div>

          {/* Retention Action Suggestion */}
          <div className="mt-4 p-4 rounded-xl border border-paytm-border bg-paytm-light">
            <div className="flex items-center gap-2 text-xs font-bold text-paytm-dark">
              <HeartHandshake className="w-4 h-4 text-paytm-blue" />
              <span>Recommended Retention Strategy (Phase 4 Decision Engine)</span>
            </div>
            <p className="text-xs text-paytm-text mt-2 font-medium">
              {selectedCustomer.suggested_retention_action || 'Re-engagement message with targeted category offer.'}
            </p>
            <div className="mt-3 flex items-center gap-2 text-[11px] text-paytm-muted">
              <span>Privacy notice: Customer numbers and personally identifiable data are masked in demo mode.</span>
            </div>
          </div>

          {/* Evidence Rationale */}
          {selectedCustomer.evidence && selectedCustomer.evidence.length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-100">
              <h4 className="text-xs font-bold text-paytm-dark mb-2">Audit Evidence</h4>
              <div className="space-y-1.5">
                {selectedCustomer.evidence.map((ev, i) => (
                  <div key={i} className="text-xs p-2 rounded bg-slate-50 flex items-center justify-between">
                    <span className="font-semibold text-paytm-dark">{ev.metric}: <span className="font-normal">{ev.value}</span></span>
                    <span className="text-[10px] text-paytm-muted">{ev.source}</span>
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
