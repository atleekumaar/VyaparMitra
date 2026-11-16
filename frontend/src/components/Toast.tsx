import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastItem {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType>({
  showToast: () => {},
});

export const useToast = () => useContext(ToastContext);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const showToast = useCallback((message: string, type: ToastType = 'success') => {
    const id = Math.random().toString(36).substring(7);
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3500);
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/* Toast container in top-right */}
      <div className="fixed top-5 right-5 z-50 flex flex-col gap-2 pointer-events-none max-w-sm w-full px-4 sm:px-0">
        {toasts.map((toast) => {
          const isSuccess = toast.type === 'success';
          const isError = toast.type === 'error';
          const isWarning = toast.type === 'warning';
          return (
            <div
              key={toast.id}
              className={`pointer-events-auto flex items-center justify-between gap-3 p-3.5 rounded-xl shadow-fintech-lg border text-xs font-semibold animate-in slide-in-from-top-2 duration-150 ${
                isSuccess
                  ? 'bg-surface-card border-success/30 text-success'
                  : isError
                  ? 'bg-surface-card border-danger/30 text-danger'
                  : isWarning
                  ? 'bg-surface-card border-amber-500/30 text-amber-600 dark:text-amber-400'
                  : 'bg-surface-card border-border text-text'
              }`}
            >
              <div className="flex items-center gap-2 min-w-0">
                {isSuccess && <CheckCircle2 className="w-4 h-4 text-success shrink-0" />}
                {isError && <AlertCircle className="w-4 h-4 text-danger shrink-0" />}
                {isWarning && <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />}
                {!isSuccess && !isError && !isWarning && <Info className="w-4 h-4 text-brand shrink-0" />}
                <span className="text-text truncate">{toast.message}</span>
              </div>
              <button
                type="button"
                onClick={() => removeToast(toast.id)}
                className="p-1 rounded-md text-text-muted hover:text-text shrink-0"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};
