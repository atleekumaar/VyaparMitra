import React from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
  bodyClassName?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  action,
  footer,
  className = '',
  bodyClassName = '',
  onClick,
  hoverable = false,
}) => {
  return (
    <div
      onClick={onClick}
      className={`bg-surface-card rounded-2xl border border-border shadow-fintech transition-all duration-150 overflow-hidden ${
        hoverable ? 'hover:border-border-strong hover:shadow-fintech-md cursor-pointer' : ''
      } ${className}`}
    >
      {(title || subtitle || action) && (
        <div className="px-5 sm:px-6 py-4 border-b border-border/60 flex items-center justify-between gap-3">
          <div className="min-w-0">
            {title && (
              <h3 className="text-sm font-semibold text-text tracking-tight truncate">{title}</h3>
            )}
            {subtitle && (
              <p className="text-xs text-text-muted mt-0.5 truncate">{subtitle}</p>
            )}
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}

      <div className={`p-5 sm:px-6 ${bodyClassName}`}>{children}</div>

      {footer && (
        <div className="px-5 sm:px-6 py-3 bg-surface-muted/50 border-t border-border/60 text-xs text-text-muted">
          {footer}
        </div>
      )}
    </div>
  );
};
