import React from 'react';
import { Store, Boxes, CreditCard, Building2, ChevronRight, X, Sparkles } from 'lucide-react';
import { UserCategory } from '../../types';
import { Badge } from '../Badge';

export interface DemoPersona {
  category: UserCategory;
  id: string;
  name: string;
  email: string;
  storeName: string;
  role: string;
  phone: string;
  city: string;
  avatarInitials: string;
  title: string;
  sub: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const DEMO_PERSONAS: DemoPersona[] = [
  {
    category: 'small_merchant',
    id: 'M001',
    name: 'Rajesh Sharma',
    email: 'rajesh.kirana@gmail.com',
    storeName: 'Shree Ganesh Kirana & General Store',
    role: 'Store Owner',
    phone: '9876543210',
    city: 'Lucknow, UP',
    avatarInitials: 'RS',
    title: 'Kirana & Retail Store (M001)',
    sub: 'Small Merchant • Daily POS & Audio alerts with prefilled sales',
    icon: Store,
  },
  {
    category: 'wholesaler',
    id: 'M015',
    name: 'Amit Agarwal',
    email: 'agarwal.fmcg@gmail.com',
    storeName: 'Agarwal Wholesale FMCG Distributors',
    role: 'Wholesale Partner',
    phone: '9812345678',
    city: 'Kanpur, UP',
    avatarInitials: 'AA',
    title: 'Wholesale & Distributor (M015)',
    sub: 'Bulk Distribution, Invoicing & Supplier Khata',
    icon: Boxes,
  },
  {
    category: 'billing_staff',
    id: 'OP-04',
    name: 'Pooja Verma',
    email: 'pooja.verma@superstore.in',
    storeName: 'Counter Terminal #01 (SuperStore)',
    role: 'Billing Operator',
    phone: '9834567890',
    city: 'Lucknow, UP',
    avatarInitials: 'PV',
    title: 'Billing Operator / Staff',
    sub: 'Fast POS counter billing & daily shift tally',
    icon: CreditCard,
  },
  {
    category: 'enterprise',
    id: 'GRP-09',
    name: 'Vikram Malhotra',
    email: 'vikram@malhotragroup.in',
    storeName: 'Malhotra Retail Chain (4 Outlets)',
    role: 'Managing Director',
    phone: '9899911223',
    city: 'Uttar Pradesh Region',
    avatarInitials: 'VM',
    title: 'Multi-Store Enterprise',
    sub: 'Multi-outlet chain owner & central admin view',
    icon: Building2,
  },
];

interface DemoProfilesModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (persona: DemoPersona) => void;
}

export const DemoProfilesModal: React.FC<DemoProfilesModalProps> = ({
  isOpen,
  onClose,
  onSelect,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in-50 duration-150">
      <div
        className="w-full max-w-lg bg-surface-card rounded-2xl border border-border shadow-fintech-lg overflow-hidden animate-in zoom-in-95 duration-150"
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="p-5 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-text">Pre-loaded Demo Accounts</h3>
                <Badge variant="demo">Simulation</Badge>
              </div>
              <p className="text-xs text-text-muted mt-0.5">
                Explore simulated business scenarios with pre-generated transactions.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-text-muted hover:text-text hover:bg-surface-muted transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Persona list */}
        <div className="p-4 space-y-2.5 max-h-[65vh] overflow-y-auto">
          {DEMO_PERSONAS.map((p) => {
            const Icon = p.icon;
            return (
              <div
                key={p.id}
                onClick={() => {
                  onSelect(p);
                  onClose();
                }}
                className="p-3.5 rounded-xl border border-border hover:border-brand hover:bg-brand-soft/40 cursor-pointer transition-all flex items-center justify-between gap-3 group"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-10 h-10 rounded-xl bg-surface-muted group-hover:bg-brand-soft text-text group-hover:text-brand flex items-center justify-center shrink-0 border border-border transition-colors">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs text-text truncate group-hover:text-brand transition-colors">
                        {p.name}
                      </span>
                      <span className="text-[10px] font-semibold text-text-muted">
                        ({p.role})
                      </span>
                    </div>
                    <p className="text-[11px] text-text-muted truncate mt-0.5">
                      {p.storeName}
                    </p>
                    <p className="text-[10px] text-brand/80 font-medium truncate mt-0.5">
                      {p.sub}
                    </p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-text-subtle group-hover:text-brand shrink-0 transition-transform group-hover:translate-x-0.5" />
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-4 bg-surface-muted/60 border-t border-border flex items-center justify-between text-xs text-text-muted">
          <span>Real merchants can simply enter their mobile &amp; email on the login page.</span>
          <button
            type="button"
            onClick={onClose}
            className="font-semibold text-text hover:text-brand"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};
