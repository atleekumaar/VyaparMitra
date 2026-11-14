/**
 * Centralized formatting helpers for VyaparMitra Fintech UI.
 * Standardizes Indian Rupee currency, compact notation (₹1.2L, ₹3.4Cr),
 * percentages, and timestamps.
 */

export const inrFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

export const inrDecimalFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export const indianNumberFormatter = new Intl.NumberFormat('en-IN');

/**
 * Format an amount in Indian Rupees.
 * Example: 125000 -> "₹1,25,000", or compact: 125000 -> "₹1.25L"
 */
export function formatCurrency(
  amount: number | null | undefined,
  options?: { compact?: boolean; decimals?: boolean; fallback?: string }
): string {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return options?.fallback ?? '—';
  }

  if (options?.compact && Math.abs(amount) >= 100000) {
    return formatCompactINR(amount);
  }

  if (options?.decimals) {
    return inrDecimalFormatter.format(amount);
  }

  return inrFormatter.format(amount);
}

/**
 * Compact Indian currency formatting (Lakhs & Crores).
 * Example: 150000 -> ₹1.50L, 25000000 -> ₹2.50Cr
 */
export function formatCompactINR(amount: number): string {
  const isNegative = amount < 0;
  const abs = Math.abs(amount);

  if (abs >= 10000000) {
    const cr = abs / 10000000;
    return `${isNegative ? '-' : ''}₹${cr.toFixed(cr >= 10 ? 1 : 2)}Cr`;
  }
  if (abs >= 100000) {
    const lakh = abs / 100000;
    return `${isNegative ? '-' : ''}₹${lakh.toFixed(lakh >= 10 ? 1 : 2)}L`;
  }
  if (abs >= 1000) {
    const k = abs / 1000;
    return `${isNegative ? '-' : ''}₹${k.toFixed(1)}k`;
  }
  return formatCurrency(amount);
}

/**
 * Format quantity or count in standard Indian grouping (1,23,456).
 */
export function formatNumber(
  num: number | null | undefined,
  fallback: string = '—'
): string {
  if (num === null || num === undefined || isNaN(num)) {
    return fallback;
  }
  return indianNumberFormatter.format(num);
}

/**
 * Format percentage with positive/negative prefix.
 * Example: 12.4 -> "+12.4%", -5.1 -> "-5.1%"
 */
export function formatPercent(
  pct: number | null | undefined,
  options?: { showPlus?: boolean }
): string {
  if (pct === null || pct === undefined || isNaN(pct)) {
    return '0.0%';
  }
  const prefix = options?.showPlus && pct > 0 ? '+' : '';
  return `${prefix}${pct.toFixed(1)}%`;
}

/**
 * Friendly localized date format.
 */
export function formatDate(
  dateStr: string | null | undefined,
  options?: { time?: boolean }
): string {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    if (options?.time) {
      return d.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    }
    return d.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}
