import React from 'react';

export type ButtonVariant =
  | 'primary'
  | 'secondary'
  | 'outline'
  | 'ghost'
  | 'success'
  | 'warning'
  | 'danger'
  | 'destructive'
  | 'navy'
  | 'ai';

export type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  className = '',
  disabled,
  ...props
}) => {
  const base =
    'inline-flex items-center justify-center font-medium transition-all duration-150 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none active:scale-[0.98]';

  const sizeClasses: Record<ButtonSize, string> = {
    sm: 'h-8 px-3 text-xs font-medium gap-1.5 rounded-lg',
    md: 'h-9 px-4 text-sm font-medium gap-2 rounded-lg',
    lg: 'h-11 px-5 text-base font-medium gap-2.5 rounded-lg',
  };

  const variants: Record<ButtonVariant, string> = {
    primary:
      'bg-blue-600 hover:bg-blue-700 text-white shadow-xs focus-visible:ring-blue-600 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900 border border-transparent',
    secondary:
      'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/80 focus-visible:ring-slate-400 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900 shadow-2xs',
    outline:
      'border border-blue-600 dark:border-blue-500 text-blue-600 dark:text-blue-400 bg-transparent hover:bg-blue-50 dark:hover:bg-blue-950/30 focus-visible:ring-blue-600 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900',
    ghost:
      'bg-transparent hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 focus-visible:ring-slate-400 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900',
    danger:
      'bg-red-600 hover:bg-red-700 text-white shadow-xs focus-visible:ring-red-600 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900 border border-transparent',
    destructive:
      'bg-red-600 hover:bg-red-700 text-white shadow-xs focus-visible:ring-red-600 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900 border border-transparent',
    warning:
      'bg-amber-600 hover:bg-amber-700 text-white shadow-xs focus-visible:ring-amber-600 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900 border border-transparent',
    success:
      'bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs focus-visible:ring-emerald-600 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900 border border-transparent',
    navy:
      'bg-slate-900 dark:bg-slate-800 hover:bg-slate-800 dark:hover:bg-slate-700 text-white shadow-xs focus-visible:ring-slate-900 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900 border border-transparent',
    ai:
      'bg-purple-600 hover:bg-purple-700 text-white shadow-xs focus-visible:ring-purple-600 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900 border border-transparent',
  };

  return (
    <button
      className={`${base} ${sizeClasses[size]} ${variants[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <svg
          className="animate-spin -ml-0.5 mr-2 h-4 w-4 text-current"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v8H4z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};
