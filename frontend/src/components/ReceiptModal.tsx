import React from 'react';
import { Printer, MessageSquare, CheckCircle2, X, Store, QrCode } from 'lucide-react';
import { Button } from './Button';
import { formatCurrency } from '../utils/formatters';

export interface ReceiptData {
  invoiceNumber: string;
  storeName: string;
  storeAddress?: string;
  storeCity?: string;
  storePhone?: string;
  storeGstin?: string;
  customerName?: string;
  customerPhone?: string;
  items: Array<{
    name: string;
    quantity: number;
    price: number;
    total: number;
  }>;
  subtotal: number;
  cgst: number;
  sgst: number;
  totalAmount: number;
  paymentMethod: string;
  timestamp: string;
}

interface ReceiptModalProps {
  isOpen: boolean;
  onClose: () => void;
  receipt: ReceiptData | null;
}

export const ReceiptModal: React.FC<ReceiptModalProps> = ({ isOpen, onClose, receipt }) => {
  if (!isOpen || !receipt) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleWhatsAppShare = () => {
    const text = encodeURIComponent(
      `*${receipt.storeName} - Bill Receipt*\n` +
      `Invoice: ${receipt.invoiceNumber}\n` +
      `Date: ${new Date(receipt.timestamp).toLocaleDateString()}\n` +
      `Items: ${receipt.items.map(i => `${i.name} (x${i.quantity})`).join(', ')}\n` +
      `Total: ${formatCurrency(receipt.totalAmount)}\n` +
      `Payment: ${receipt.paymentMethod}\n` +
      `Dhanyawad! Please visit again.`
    );
    const phone = receipt.customerPhone ? receipt.customerPhone.replace(/\D/g, '') : '';
    window.open(`https://wa.me/${phone}?text=${text}`, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-xs animate-in fade-in-50">
      <div className="w-full max-w-sm bg-surface-card rounded-2xl border border-border shadow-fintech-lg flex flex-col max-h-[90vh] overflow-hidden">
        {/* Top Action Bar (Hidden when printing) */}
        <div className="flex items-center justify-between p-3.5 border-b border-border bg-surface-muted/50 print:hidden">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span className="text-xs font-bold text-text">Sale Complete &amp; Receipt</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-text-muted hover:text-text cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Thermal Slip Content (Print Area) */}
        <div className="p-6 overflow-y-auto font-mono text-xs text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-900 print:p-0 print:m-0 print:text-black print:bg-white select-text">
          {/* Store Header */}
          <div className="text-center pb-3 border-b border-dashed border-slate-300 dark:border-slate-700 space-y-1">
            <h2 className="text-sm font-black uppercase tracking-wider text-slate-900 dark:text-white print:text-black">
              {receipt.storeName}
            </h2>
            <p className="text-[11px] text-slate-600 dark:text-slate-400 print:text-black">
              {receipt.storeAddress || 'Main Market Road'}
              {receipt.storeCity ? `, ${receipt.storeCity}` : ''}
            </p>
            {receipt.storePhone && (
              <p className="text-[10px] text-slate-500 dark:text-slate-400 print:text-black">
                Tel: {receipt.storePhone}
              </p>
            )}
            <p className="text-[10px] font-bold tracking-tight text-slate-500 dark:text-slate-400 print:text-black">
              GSTIN: {receipt.storeGstin || '09AAAAA0000A1Z5 (Composition)'}
            </p>
          </div>

          {/* Invoice Meta */}
          <div className="py-2.5 border-b border-dashed border-slate-300 dark:border-slate-700 text-[11px] space-y-0.5">
            <div className="flex justify-between">
              <span>INV NO:</span>
              <span className="font-bold">{receipt.invoiceNumber}</span>
            </div>
            <div className="flex justify-between">
              <span>DATE/TIME:</span>
              <span>{new Date(receipt.timestamp).toLocaleString()}</span>
            </div>
            {receipt.customerName && (
              <div className="flex justify-between">
                <span>PATRON:</span>
                <span className="font-bold">{receipt.customerName}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span>MODE:</span>
              <span className="font-bold">{receipt.paymentMethod}</span>
            </div>
          </div>

          {/* Items Table */}
          <div className="py-3 border-b border-dashed border-slate-300 dark:border-slate-700">
            <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider pb-1 text-slate-500 dark:text-slate-400">
              <span>Item &amp; Qty</span>
              <span>Total</span>
            </div>
            <div className="space-y-1.5 pt-1">
              {receipt.items.map((item, idx) => (
                <div key={idx} className="flex justify-between text-[11px]">
                  <div className="max-w-[190px] truncate">
                    <span className="font-semibold">{item.name}</span>
                    <span className="text-[10px] block text-slate-500 dark:text-slate-400">
                      {item.quantity} x {formatCurrency(item.price)}
                    </span>
                  </div>
                  <span className="font-bold tabular-nums">{formatCurrency(item.total)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Tax Breakup & Grand Total */}
          <div className="py-2.5 border-b border-dashed border-slate-300 dark:border-slate-700 text-[11px] space-y-1">
            <div className="flex justify-between text-slate-600 dark:text-slate-400">
              <span>Taxable Subtotal:</span>
              <span className="tabular-nums">{formatCurrency(receipt.subtotal)}</span>
            </div>
            <div className="flex justify-between text-[10px] text-slate-500 dark:text-slate-400">
              <span>CGST (2.5%):</span>
              <span className="tabular-nums">{formatCurrency(receipt.cgst)}</span>
            </div>
            <div className="flex justify-between text-[10px] text-slate-500 dark:text-slate-400">
              <span>SGST (2.5%):</span>
              <span className="tabular-nums">{formatCurrency(receipt.sgst)}</span>
            </div>
            <div className="flex justify-between text-sm font-black pt-1.5 border-t border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white print:text-black">
              <span>GRAND TOTAL:</span>
              <span className="tabular-nums">{formatCurrency(receipt.totalAmount)}</span>
            </div>
          </div>

          {/* Thermal Slip Footer */}
          <div className="text-center pt-3 space-y-1">
            <p className="text-[11px] font-bold text-slate-800 dark:text-slate-200">
              *** DHANYAWAD ! VISIT AGAIN ***
            </p>
            <p className="text-[9px] text-slate-400 dark:text-slate-500">
              Powered by VyaparMitra Retail POS
            </p>
          </div>
        </div>

        {/* Bottom Actions (Hidden when printing) */}
        <div className="p-3.5 border-t border-border bg-surface-muted/50 flex items-center justify-between gap-2 print:hidden">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleWhatsAppShare}
            className="gap-1.5 text-xs text-emerald-600 border-emerald-500/30 hover:bg-emerald-500/10"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>WhatsApp</span>
          </Button>

          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={onClose}
              className="text-xs"
            >
              Close
            </Button>
            <Button
              type="button"
              variant="primary"
              size="sm"
              onClick={handlePrint}
              className="gap-1.5 text-xs"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print Slip</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
