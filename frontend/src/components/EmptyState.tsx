import React from 'react';
import { Inbox, AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

interface EmptyStateProps {
  title?: string;
  message?: string;
  icon?: React.ReactNode;
  actionText?: string;
  onAction?: () => void;
  secondaryActionText?: string;
  onSecondaryAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No Data Available',
  message = 'There are no records matching your criteria in the current period.',
  icon,
  actionText,
  onAction,
  secondaryActionText,
  onSecondaryAction,
  className = '',
}) => {
  return (
    <div
      className={`bg-surface-card rounded-2xl border border-border p-8 sm:p-12 text-center flex flex-col items-center justify-center transition-colors shadow-fintech ${className}`}
    >
      <div className="w-14 h-14 rounded-2xl bg-brand-soft text-brand flex items-center justify-center mb-4 border border-brand/20">
        {icon || <Inbox className="w-7 h-7" />}
      </div>
      <h3 className="text-base font-bold text-text">{title}</h3>
      <p className="text-xs text-text-muted max-w-md mt-1 leading-relaxed">{message}</p>

      {(onAction || onSecondaryAction) && (
        <div className="mt-5 flex items-center gap-3 flex-wrap justify-center">
          {actionText && onAction && (
            <Button variant="primary" size="sm" onClick={onAction}>
              {actionText}
            </Button>
          )}
          {secondaryActionText && onSecondaryAction && (
            <Button variant="secondary" size="sm" onClick={onSecondaryAction}>
              {secondaryActionText}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onRetry, className = '' }) => {
  return (
    <div
      className={`rounded-2xl border border-danger/30 bg-danger-soft p-4 text-danger flex items-start gap-3 transition-colors shadow-2xs ${className}`}
    >
      <AlertCircle className="w-5 h-5 text-danger shrink-0 mt-0.5" />
      <div className="flex-1 text-xs">
        <p className="font-bold text-sm text-text">We couldn't load this information</p>
        <p className="mt-0.5 text-danger/90 leading-normal">{message}</p>
      </div>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry} className="shrink-0">
          <RefreshCw className="w-3.5 h-3.5 mr-1" />
          Retry
        </Button>
      )}
    </div>
  );
};
