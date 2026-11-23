import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { Printer, MessageSquare, CheckCircle2, X } from 'lucide-react';
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

// Compact, single-page thermal slip content shared between on-screen preview & isolated print root
const ReceiptSlipContent: React.FC<{ receipt: ReceiptData; isPrintOnly?: boolean }> = ({
  receipt,
  isPrintOnly = false,
}) => {
  return (
    <div
      className={
        isPrintOnly
          ? 'print-receipt-slip font-mono text-xs text-black bg-white select-text'
          : 'p-6 overflow-y-auto font-mono text-xs text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-900 select-text'
      }
      style={{ breakInside: 'avoid', pageBreakInside: 'avoid' }}
    >
      {/* Store Header */}
      <div className="text-center pb-2.5 border-b border-dashed border-slate-400 dark:border-slate-700 space-y-0.5">
        <h2 className="text-sm font-black uppercase tracking-wider text-slate-900 dark:text-white print:text-black">
          {receipt.storeName || 'VyaparMitra Store'}
        </h2>
        <p className="text-[11px] text-slate-600 dark:text-slate-400 print:text-black leading-tight">
          {receipt.storeAddress || 'Main Market Road'}
          {receipt.storeCity ? `, ${receipt.storeCity}` : ''}
        </p>
        {receipt.storePhone && (
          <p className="text-[10px] text-slate-600 dark:text-slate-400 print:text-black">
            Tel: {receipt.storePhone}
          </p>
        )}
        <p className="text-[10px] font-bold tracking-tight text-slate-600 dark:text-slate-400 print:text-black">
          GSTIN: {receipt.storeGstin || '09AAAAA0000A1Z5 (Composition)'}
        </p>
      </div>

      {/* Invoice Meta */}
      <div className="py-2 border-b border-dashed border-slate-400 dark:border-slate-700 text-[11px] space-y-0.5">
        <div className="flex justify-between">
          <span className="text-slate-600 dark:text-slate-400 print:text-black">INV NO:</span>
          <span className="font-bold print:text-black">{receipt.invoiceNumber}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-600 dark:text-slate-400 print:text-black">DATE/TIME:</span>
          <span className="print:text-black">{new Date(receipt.timestamp).toLocaleString()}</span>
        </div>
        {receipt.customerName && (
          <div className="flex justify-between">
            <span className="text-slate-600 dark:text-slate-400 print:text-black">PATRON:</span>
            <span className="font-bold print:text-black">{receipt.customerName}</span>
          </div>
        )}
        <div className="flex justify-between">
          <span className="text-slate-600 dark:text-slate-400 print:text-black">PAYMENT:</span>
          <span className="font-bold print:text-black">{receipt.paymentMethod}</span>
        </div>
      </div>

      {/* Items Table */}
      <div className="py-2.5 border-b border-dashed border-slate-400 dark:border-slate-700">
        <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider pb-1 text-slate-600 dark:text-slate-400 print:text-black">
          <span>Item &amp; Qty</span>
          <span>Total</span>
        </div>
        <div className="space-y-1.5 pt-1">
          {receipt.items.map((item, idx) => (
            <div key={idx} className="flex justify-between text-[11px] leading-tight">
              <div className="max-w-[200px] truncate">
                <span className="font-semibold print:text-black">{item.name}</span>
                <span className="text-[10px] block text-slate-600 dark:text-slate-400 print:text-black">
                  {item.quantity} x {formatCurrency(item.price)}
                </span>
              </div>
              <span className="font-bold tabular-nums print:text-black">{formatCurrency(item.total)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Tax Breakup & Grand Total */}
      <div className="py-2 border-b border-dashed border-slate-400 dark:border-slate-700 text-[11px] space-y-0.5">
        <div className="flex justify-between text-slate-600 dark:text-slate-400 print:text-black">
          <span>Taxable Subtotal:</span>
          <span className="tabular-nums print:text-black">{formatCurrency(receipt.subtotal)}</span>
        </div>
        <div className="flex justify-between text-[10px] text-slate-600 dark:text-slate-400 print:text-black">
          <span>CGST (2.5%):</span>
          <span className="tabular-nums print:text-black">{formatCurrency(receipt.cgst)}</span>
        </div>
        <div className="flex justify-between text-[10px] text-slate-600 dark:text-slate-400 print:text-black">
          <span>SGST (2.5%):</span>
          <span className="tabular-nums print:text-black">{formatCurrency(receipt.sgst)}</span>
        </div>
        <div className="flex justify-between text-sm font-black pt-1.5 border-t border-slate-400 dark:border-slate-700 text-slate-900 dark:text-white print:text-black">
          <span>GRAND TOTAL:</span>
          <span className="tabular-nums">{formatCurrency(receipt.totalAmount)}</span>
        </div>
      </div>

      {/* Thermal Slip Footer */}
      <div className="text-center pt-2.5 space-y-0.5">
        <p className="text-[11px] font-bold text-slate-900 dark:text-slate-100 print:text-black">
          *** DHANYAWAD ! VISIT AGAIN ***
        </p>
        <p className="text-[9px] text-slate-500 dark:text-slate-400 print:text-black">
          Computer Generated Tax Invoice &bull; VyaparMitra POS
        </p>
      </div>
    </div>
  );
};

export const ReceiptModal: React.FC<ReceiptModalProps> = ({ isOpen, onClose, receipt }) => {
  const [printContainer, setPrintContainer] = useState<HTMLElement | null>(null);

  // Setup dedicated #receipt-print-root portal container
  useEffect(() => {
    let el = document.getElementById('receipt-print-root');
    if (!el) {
      el = document.createElement('div');
      el.id = 'receipt-print-root';
      document.body.appendChild(el);
    }
    setPrintContainer(el);
  }, []);

  // Compute clean, descriptive PDF filename from invoice and store details
  const getPdfTitle = () => {
    if (!receipt) return 'Receipt';
    const cleanInv = (receipt.invoiceNumber || 'INV')
      .replace(/[^a-zA-Z0-9_-]/g, '_');
    const cleanStore = (receipt.storeName || 'Store')
      .replace(/[^a-zA-Z0-9]/g, '_')
      .replace(/_+/g, '_')
      .slice(0, 20);
    return `Receipt_${cleanInv}_${cleanStore}`;
  };

  // Manage print title & body classes when receipt modal is active
  useEffect(() => {
    if (!isOpen || !receipt) return;

    const originalTitle = document.title;
    const pdfTitle = getPdfTitle();

    document.title = pdfTitle;
    document.body.classList.add('print-receipt-active');

    const handleAfterPrint = () => {
      document.title = originalTitle;
      document.body.classList.remove('print-receipt-active');
    };

    window.addEventListener('afterprint', handleAfterPrint);

    return () => {
      document.title = originalTitle;
      document.body.classList.remove('print-receipt-active');
      window.removeEventListener('afterprint', handleAfterPrint);
    };
  }, [isOpen, receipt]);

  if (!isOpen || !receipt) return null;

  const handlePrint = () => {
    const pdfTitle = getPdfTitle();
    document.title = pdfTitle;
    document.body.classList.add('print-receipt-active');

    // Trigger browser native print/PDF save dialog
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
    <>
      {/* 1. On-Screen Interactive Modal Dialog (hidden during print) */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-xs animate-in fade-in-50 print:hidden">
        <div className="w-full max-w-sm bg-surface-card rounded-2xl border border-border shadow-fintech-lg flex flex-col max-h-[90vh] overflow-hidden">
          {/* Top Action Bar */}
          <div className="flex items-center justify-between p-3.5 border-b border-border bg-surface-muted/50">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span className="text-xs font-bold text-text">Sale Complete &amp; Receipt</span>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="p-1 rounded-lg text-text-muted hover:text-text cursor-pointer"
              title="Close modal"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Thermal Slip Content Preview */}
          <ReceiptSlipContent receipt={receipt} />

          {/* Bottom Actions */}
          <div className="p-3.5 border-t border-border bg-surface-muted/50 flex items-center justify-between gap-2">
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
                className="gap-1.5 text-xs shadow-fintech"
                title="Print slip or save as 1-page PDF"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Print / Save PDF</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Isolated Print Portal (Rendered directly in #receipt-print-root for 1-page print) */}
      {printContainer &&
        createPortal(
          <ReceiptSlipContent receipt={receipt} isPrintOnly />,
          printContainer
        )}
    </>
  );
};
