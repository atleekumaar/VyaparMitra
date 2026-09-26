import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'critical' | 'high' | 'medium' | 'low' | 'success' | 'info' | 'neutral' | 'demo';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral', className = '' }) => {
  const styles: Record<string, string> = {
    critical: 'bg-red-50 text-red-700 border-red-200 font-semibold',
    high: 'bg-amber-50 text-amber-700 border-amber-200 font-semibold',
    medium: 'bg-blue-50 text-blue-700 border-blue-200',
    low: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    info: 'bg-paytm-light text-paytm-blue border-paytm-border font-medium',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
    demo: 'bg-cyan-50 text-cyan-800 border-cyan-200 font-medium tracking-wide uppercase',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs border ${
        styles[variant] || styles.neutral
      } ${className}`}
    >
      {children}
    </span>
  );
};
