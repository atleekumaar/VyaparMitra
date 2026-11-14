import React from 'react';
import { ArrowUpDown, AlertCircle } from 'lucide-react';
import { TableSkeleton } from './LoadingSkeleton';

export interface Column<T> {
  key: string;
  header: string;
  render?: (row: T, index: number) => React.ReactNode;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T, index: number) => string;
  onRowClick?: (row: T) => void;
  loading?: boolean;
  emptyMessage?: string;
  emptyAction?: React.ReactNode;
  onSort?: (key: string) => void;
  sortKey?: string;
  sortDirection?: 'asc' | 'desc';
  renderMobileCard?: (row: T, index: number) => React.ReactNode;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
  loading = false,
  emptyMessage = 'No records found',
  emptyAction,
  onSort,
  sortKey,
  sortDirection,
  renderMobileCard,
}: DataTableProps<T>) {
  if (loading) {
    return <TableSkeleton rows={6} />;
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-surface-card rounded-2xl border border-border p-8 text-center flex flex-col items-center justify-center">
        <div className="w-12 h-12 rounded-2xl bg-surface-muted text-text-muted flex items-center justify-center mb-3">
          <AlertCircle className="w-6 h-6 text-text-subtle" />
        </div>
        <h4 className="text-sm font-semibold text-text">{emptyMessage}</h4>
        {emptyAction && <div className="mt-4">{emptyAction}</div>}
      </div>
    );
  }

  return (
    <div className="bg-surface-card rounded-2xl border border-border shadow-fintech overflow-hidden">
      {/* Mobile Card List View (< sm) */}
      <div className="sm:hidden divide-y divide-border">
        {data.map((row, idx) => {
          const rowKey = keyExtractor(row, idx);
          if (renderMobileCard) {
            return (
              <div
                key={rowKey}
                onClick={() => onRowClick?.(row)}
                className={`p-4 ${onRowClick ? 'cursor-pointer active:bg-surface-muted' : ''}`}
              >
                {renderMobileCard(row, idx)}
              </div>
            );
          }
          // Default mobile card
          return (
            <div
              key={rowKey}
              onClick={() => onRowClick?.(row)}
              className={`p-4 space-y-2 ${onRowClick ? 'cursor-pointer active:bg-surface-muted' : ''}`}
            >
              {columns.map((col) => (
                <div key={col.key} className="flex items-center justify-between text-xs">
                  <span className="text-text-muted font-medium">{col.header}</span>
                  <span className="font-semibold text-text text-right">
                    {col.render ? col.render(row, idx) : (row as any)[col.key]}
                  </span>
                </div>
              ))}
            </div>
          );
        })}
      </div>

      {/* Desktop / Tablet Full Table (>= sm) */}
      <div className="hidden sm:block overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-border bg-surface-muted/60 text-[11px] font-semibold text-text-muted uppercase tracking-wider select-none sticky top-0 z-10 backdrop-blur-xs">
              {columns.map((col) => {
                const isSorted = sortKey === col.key;
                return (
                  <th
                    key={col.key}
                    scope="col"
                    onClick={() => col.sortable && onSort?.(col.key)}
                    className={`px-5 py-3.5 ${
                      col.align === 'right'
                        ? 'text-right'
                        : col.align === 'center'
                        ? 'text-center'
                        : 'text-left'
                    } ${col.sortable ? 'cursor-pointer hover:text-text' : ''} ${
                      col.className || ''
                    }`}
                  >
                    <div
                      className={`inline-flex items-center gap-1.5 ${
                        col.align === 'right' ? 'justify-end' : ''
                      }`}
                    >
                      <span>{col.header}</span>
                      {col.sortable && (
                        <ArrowUpDown
                          className={`w-3 h-3 ${
                            isSorted ? 'text-brand' : 'text-text-subtle'
                          }`}
                        />
                      )}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60 text-xs text-text">
            {data.map((row, idx) => {
              const rowKey = keyExtractor(row, idx);
              return (
                <tr
                  key={rowKey}
                  onClick={() => onRowClick?.(row)}
                  className={`transition-colors duration-100 ${
                    onRowClick
                      ? 'cursor-pointer hover:bg-surface-muted/70 active:bg-surface-muted'
                      : 'hover:bg-surface-muted/40'
                  }`}
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={`px-5 py-3.5 whitespace-nowrap ${
                        col.align === 'right'
                          ? 'text-right tabular-nums'
                          : col.align === 'center'
                          ? 'text-center'
                          : 'text-left'
                      } ${col.className || ''}`}
                    >
                      {col.render ? col.render(row, idx) : (row as any)[col.key]}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
