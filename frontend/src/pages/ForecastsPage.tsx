import React, { useEffect, useState } from 'react';
import { TrendingUp, Calendar, Package, AlertCircle, Info } from 'lucide-react';
import { api } from '../api/client';
import { SalesForecast, SKUForecastItem } from '../types';
import { Badge } from '../components/Badge';
import { TableSkeleton, CardSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner } from '../components/EmptyState';

export const ForecastsPage: React.FC = () => {
  const [salesForecast, setSalesForecast] = useState<SalesForecast | null>(null);
  const [demandForecast, setDemandForecast] = useState<SKUForecastItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadForecasts = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sfRes, dfRes] = await Promise.all([
        api.getSalesForecast(),
        api.getDemandForecast(30),
      ]);
      setSalesForecast(sfRes);
      setDemandForecast(dfRes.top_demand_skus || []);
    } catch (err: any) {
      setError(err?.message || 'Failed to load predictive forecasts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadForecasts();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
        <TableSkeleton rows={8} />
      </div>
    );
  }

  if (error || !salesForecast) {
    return <ErrorBanner message={error || 'Could not load forecasts.'} onRetry={loadForecasts} />;
  }

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-paytm-dark">Predictive AI Engine & Forecasts</h2>
        <p className="text-xs text-paytm-muted mt-0.5">
          Forward-looking autoregressive forecasts trained on historical transaction momentum and seasonal patterns.
        </p>
      </div>

      {/* KPI Forecast Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-paytm-border p-5">
          <span className="text-xs font-semibold text-paytm-muted uppercase">7-Day Projected Revenue</span>
          <p className="text-2xl font-bold text-paytm-dark mt-2">
            ₹{salesForecast.forecast_7d_total_revenue.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
          <div className="mt-2 text-xs text-paytm-muted">
            Prediction Window: Next 7 Business Days
          </div>
        </div>

        <div className="bg-white rounded-xl border border-paytm-border p-5">
          <span className="text-xs font-semibold text-paytm-muted uppercase">Anticipated Trend</span>
          <p className="text-2xl font-bold text-paytm-blue mt-2">
            {salesForecast.trend_direction}
          </p>
          <div className="mt-2 text-xs text-paytm-muted">
            Based on Phase 3 Trend Classifier
          </div>
        </div>

        <div className="bg-white rounded-xl border border-paytm-border p-5">
          <span className="text-xs font-semibold text-paytm-muted uppercase">Active ML Model</span>
          <p className="text-lg font-bold text-slate-700 mt-2 truncate">
            {salesForecast.model_name}
          </p>
          <div className="mt-2 text-xs text-emerald-600 font-medium">
            Strict Non-Lookahead Validated
          </div>
        </div>
      </div>

      {/* Daily Sales Forecast Table & Chart */}
      <div className="bg-white rounded-xl border border-paytm-border p-5 shadow-xs">
        <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider mb-4">
          Daily Store Sales Forecast (Next 7 Days)
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-7 gap-2">
          {salesForecast.daily_forecasts.map((d, i) => (
            <div
              key={i}
              className="p-3 rounded-lg border border-paytm-border bg-paytm-light/50 flex flex-col items-center text-center"
            >
              <span className="text-[11px] text-paytm-muted font-medium">Day {i + 1}</span>
              <span className="text-[10px] text-slate-400 mt-0.5">{d.forecast_date}</span>
              <span className="text-sm font-bold text-paytm-dark mt-2">
                ₹{d.predicted_revenue.toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* SKU-level Demand Forecast */}
      <div className="bg-white rounded-xl border border-paytm-border overflow-hidden shadow-xs">
        <div className="px-5 py-3.5 border-b border-paytm-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Package className="w-4 h-4 text-paytm-blue" />
            <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider">
              Top SKU Projected Demand (Next 7 Days)
            </h3>
          </div>
          <span className="text-xs text-paytm-muted">Sorted by anticipated units</span>
        </div>

        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
            <tr>
              <th className="py-2.5 px-4">Rank</th>
              <th className="py-2.5 px-4">Product Name</th>
              <th className="py-2.5 px-4">Category</th>
              <th className="py-2.5 px-4">SKU Code</th>
              <th className="py-2.5 px-4 text-right">Projected Demand (Units)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {demandForecast.map((sku, idx) => (
              <tr key={sku.product_id} className="hover:bg-slate-50/60">
                <td className="py-2.5 px-4 font-bold text-paytm-blue">#{idx + 1}</td>
                <td className="py-2.5 px-4 font-semibold text-paytm-dark">{sku.product_name}</td>
                <td className="py-2.5 px-4 text-paytm-muted">{sku.category}</td>
                <td className="py-2.5 px-4 font-mono text-[11px]">{sku.product_id}</td>
                <td className="py-2.5 px-4 text-right font-bold text-emerald-700">
                  {sku.predicted_7d_units} units
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
