import React from 'react';
import { Calendar } from 'lucide-react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  dateRange?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  badge,
  actions,
  dateRange,
}) => {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/40">
      <div className="min-w-0">
        <div className="flex items-center gap-2.5 flex-wrap">
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-text">
            {title}
          </h1>
          {badge && <div className="shrink-0">{badge}</div>}
        </div>
        {subtitle && (
          <p className="text-xs sm:text-sm text-text-muted mt-1 leading-normal">
            {subtitle}
          </p>
        )}
      </div>

      <div className="flex items-center gap-3 shrink-0 self-start sm:self-auto flex-wrap">
        {dateRange && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-surface-card border border-border text-xs font-semibold text-text-muted shadow-2xs">
            <Calendar className="w-3.5 h-3.5 text-brand" />
            <span>{dateRange}</span>
          </div>
        )}
        {actions}
      </div>
    </div>
  );
};
