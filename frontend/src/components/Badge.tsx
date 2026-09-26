import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'critical' | 'high' | 'medium' | 'low' | 'success' | 'info' | 'neutral' | 'demo';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral', className = '' }) => {
  const styles: Record<string, string> = {
    critical: 'bg-[#FEECEB] text-[#D92D20] border-[#FECDCA] font-bold',
    high: 'bg-[#FFF6E5] text-[#C27803] border-[#FFE1A8] font-bold',
    medium: 'bg-[#EBF5FE] text-[#0070B8] border-[#BAE0FD] font-semibold',
    low: 'bg-[#E8F8F0] text-[#008A54] border-[#B6E8D0] font-semibold',
    success: 'bg-[#E8F8F0] text-[#008A54] border-[#B6E8D0] font-bold',
    info: 'bg-[#E8F6FD] text-[#0089C9] border-[#B8E3FA] font-bold',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200 font-medium',
    demo: 'bg-[#E8F4FD] text-[#002970] border-[#B3DCF8] font-bold tracking-wide uppercase',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs border shadow-2xs ${
        styles[variant] || styles.neutral
      } ${className}`}
    >
      {children}
    </span>
  );
};
