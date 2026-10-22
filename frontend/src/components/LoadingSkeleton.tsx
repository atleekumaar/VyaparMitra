import React from 'react';

export const CardSkeleton: React.FC = () => (
  <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 animate-pulse transition-colors">
    <div className="h-3.5 bg-slate-200 dark:bg-slate-800 rounded w-1/3 mb-3"></div>
    <div className="h-7 bg-slate-200 dark:bg-slate-800 rounded w-2/3 mb-2"></div>
    <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-1/2"></div>
  </div>
);

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden animate-pulse transition-colors">
    <div className="h-11 bg-slate-100 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800"></div>
    <div className="divide-y divide-slate-100 dark:divide-slate-800 p-4 space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 pt-2">
          <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/4"></div>
          <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/3"></div>
          <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/6"></div>
          <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/4"></div>
        </div>
      ))}
    </div>
  </div>
);

export const ChartSkeleton: React.FC = () => (
  <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 animate-pulse transition-colors">
    <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/4 mb-6"></div>
    <div className="h-64 bg-slate-50 dark:bg-slate-800/40 rounded-lg flex items-end justify-between p-4 gap-2">
      {Array.from({ length: 12 }).map((_, i) => (
        <div
          key={i}
          className="bg-slate-200 dark:bg-slate-700/60 rounded-t w-full"
          style={{ height: `${20 + (i * 7) % 80}%` }}
        ></div>
      ))}
    </div>
  </div>
);
