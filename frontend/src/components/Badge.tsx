import React from 'react';

export type BadgeVariant =
  | 'critical'
  | 'high'
  | 'medium'
  | 'low'
  | 'success'
  | 'info'
  | 'neutral'
  | 'demo'
  | 'warning'
  | 'danger'
  | 'brand'
  | 'ai';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  dot?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  dot = false,
  className = '',
}) => {
  const styles: Record<BadgeVariant, { badge: string; dot: string }> = {
    critical: {
      badge: 'bg-danger-soft text-danger border-danger/30 font-bold',
      dot: 'bg-danger',
    },
    danger: {
      badge: 'bg-danger-soft text-danger border-danger/30 font-bold',
      dot: 'bg-danger',
    },
    high: {
      badge: 'bg-warning-soft text-warning border-warning/30 font-bold',
      dot: 'bg-warning',
    },
    warning: {
      badge: 'bg-warning-soft text-warning border-warning/30 font-bold',
      dot: 'bg-warning',
    },
    medium: {
      badge: 'bg-brand-soft text-brand border-brand/20 font-semibold',
      dot: 'bg-brand',
    },
    brand: {
      badge: 'bg-brand-soft text-brand border-brand/20 font-semibold',
      dot: 'bg-brand',
    },
    low: {
      badge: 'bg-surface-muted text-text-muted border-border font-medium',
      dot: 'bg-text-subtle',
    },
    success: {
      badge: 'bg-success-soft text-success border-success/30 font-bold',
      dot: 'bg-success',
    },
    info: {
      badge: 'bg-info-soft text-info border-info/30 font-medium',
      dot: 'bg-info',
    },
    neutral: {
      badge: 'bg-surface-muted text-text-muted border-border font-medium',
      dot: 'bg-text-subtle',
    },
    demo: {
      badge: 'bg-purple-500/10 text-purple-600 dark:text-purple-300 border-purple-500/30 font-bold uppercase tracking-wider',
      dot: 'bg-purple-500',
    },
    ai: {
      badge: 'bg-purple-500/10 text-purple-600 dark:text-purple-300 border-purple-500/30 font-semibold',
      dot: 'bg-purple-500',
    },
  };

  const current = styles[variant] || styles.neutral;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs border shadow-2xs transition-colors select-none ${
        current.badge
      } ${className}`}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${current.dot}`} />}
      <span>{children}</span>
    </span>
  );
};
