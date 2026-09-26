import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'success' | 'navy';
  size?: 'sm' | 'md' | 'lg';
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
    'inline-flex items-center justify-center font-bold transition-all duration-150 rounded-xl focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed select-none active:scale-[0.98]';

  const sizeClasses = {
    sm: 'text-xs px-3 py-1.5 gap-1.5',
    md: 'text-sm px-4 py-2.5 gap-2',
    lg: 'text-base px-6 py-3 gap-2.5',
  };

  const variants = {
    primary:
      'bg-gradient-to-r from-[#00BAF2] to-[#009EDB] hover:from-[#00A8DE] hover:to-[#008CC4] text-white shadow-md shadow-[#00BAF2]/25 focus:ring-[#00BAF2] border border-transparent',
    navy:
      'bg-gradient-to-r from-[#002970] to-[#001D52] hover:from-[#00388F] hover:to-[#002970] text-white shadow-md shadow-[#002970]/25 focus:ring-[#002970] border border-transparent',
    secondary:
      'bg-white text-[#002970] border border-[#CDE5F7] hover:bg-[#F0F8FE] hover:border-[#00BAF2] focus:ring-[#00BAF2] shadow-xs',
    outline:
      'border-2 border-[#00BAF2] text-[#0089C9] bg-transparent hover:bg-[#F0F8FE] focus:ring-[#00BAF2]',
    danger:
      'bg-[#FF4D4D] hover:bg-[#E03E3E] text-white shadow-sm focus:ring-red-500 border border-transparent',
    success:
      'bg-gradient-to-r from-[#00B970] to-[#00A362] hover:from-[#00A362] hover:to-[#008C53] text-white shadow-md shadow-[#00B970]/25 focus:ring-[#00B970] border border-transparent',
  };

  return (
    <button
      className={`${base} ${sizeClasses[size]} ${variants[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
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
