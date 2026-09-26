import React, { useEffect, useState } from 'react';
import { TrendingUp, Calendar, Package, AlertCircle, Info } from 'lucide-react';
import { api } from '../api/client';
import { SalesForecast, SKUForecastItem } from '../types';
import { Badge } from '../components/Badge';
import { TableSkeleton, CardSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner } from '../components/EmptyState';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';

export const ForecastsPage: React.FC = () => {
  const { t, language } = useLanguage();
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
        <h2 className="text-xl font-bold text-paytm-dark">
          {language === 'hindi' ? 'बिक्री व मांग का अनुमान (Sales Forecast)' : 'Sales & Demand Forecasts'}
        </h2>
        <p className="text-xs text-paytm-muted mt-0.5">
          {language === 'hindi'
            ? 'अगले 7 दिनों के लिए अनुमानित दुकान की बिक्री और टॉप बिकने वाले सामान की मांग।'
            : 'Expected store revenue and top product demand projections for the upcoming 7 business days.'}
        </p>
      </div>

      {/* KPI Forecast Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-paytm-border p-5">
          <span className="text-xs font-semibold text-paytm-muted uppercase">
            {language === 'hindi' ? '7-दिवसीय अनुमानित कुल बिक्री' : '7-Day Projected Revenue'}
          </span>
          <p className="text-2xl font-bold text-paytm-dark mt-2">
            ₹{salesForecast.forecast_7d_total_revenue.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
          <div className="mt-2 text-xs text-paytm-muted">
            {language === 'hindi' ? 'आगामी 7 व्यावसायिक दिनों का कुल योग' : 'Prediction Window: Next 7 Business Days'}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-paytm-border p-5">
          <span className="text-xs font-semibold text-paytm-muted uppercase">
            {language === 'hindi' ? 'बिक्री का रुझान' : 'Anticipated Trend'}
          </span>
          <p className="text-2xl font-bold text-paytm-blue mt-2">
            {localizeDynamicText(salesForecast.trend_direction, language)}
          </p>
          <div className="mt-2 text-xs text-paytm-muted">
            {language === 'hindi' ? 'साप्ताहिक बिक्री की अनुमानित दिशा' : 'Expected weekly sales momentum'}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-paytm-border p-5">
          <span className="text-xs font-semibold text-paytm-muted uppercase">
            {language === 'hindi' ? 'दैनिक औसत अनुमान (Daily Run-Rate)' : 'Projected Daily Average'}
          </span>
          <p className="text-2xl font-bold text-[#002970] dark:text-[#00BAF2] mt-2">
            ₹{(salesForecast.forecast_7d_total_revenue / 7).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <div className="mt-2 text-xs text-emerald-600 font-medium flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span>
            <span>{language === 'hindi' ? 'उच्च सटीकता • स्वचालित गणना' : 'High Confidence • Automated Calculation'}</span>
          </div>
        </div>
      </div>

      {/* Daily Sales Forecast Table & Chart */}
      <div className="bg-white rounded-xl border border-paytm-border p-5 shadow-xs">
        <h3 className="text-xs font-bold text-paytm-dark uppercase tracking-wider mb-4">
          {language === 'hindi' ? 'दैनिक स्टोर बिक्री पूर्वानुमान (अगले 7 दिन)' : 'Daily Store Sales Forecast (Next 7 Days)'}
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-7 gap-2">
          {salesForecast.daily_forecasts.map((d, i) => (
            <div
              key={i}
              className="p-3 rounded-lg border border-paytm-border bg-paytm-light/50 flex flex-col items-center text-center"
            >
              <span className="text-[11px] text-paytm-muted font-medium">{language === 'hindi' ? 'दिन' : 'Day'} {i + 1}</span>
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
              {language === 'hindi' ? 'शीर्ष SKU अनुमानित मांग (अगले 7 दिन)' : 'Top SKU Projected Demand (Next 7 Days)'}
            </h3>
          </div>
          <span className="text-xs text-paytm-muted">{language === 'hindi' ? 'अनुमानित इकाइयों द्वारा क्रमबद्ध' : 'Sorted by anticipated units'}</span>
        </div>

        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
            <tr>
              <th className="py-2.5 px-4">{language === 'hindi' ? 'रैंक' : 'Rank'}</th>
              <th className="py-2.5 px-4">{language === 'hindi' ? 'उत्पाद का नाम' : 'Product Name'}</th>
              <th className="py-2.5 px-4">{language === 'hindi' ? 'श्रेणी' : 'Category'}</th>
              <th className="py-2.5 px-4">{language === 'hindi' ? 'SKU कोड' : 'SKU Code'}</th>
              <th className="py-2.5 px-4 text-right">{language === 'hindi' ? 'अनुमानित मांग (इकाईयां)' : 'Projected Demand (Units)'}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {demandForecast.map((sku, idx) => (
              <tr key={sku.product_id} className="hover:bg-slate-50/60">
                <td className="py-2.5 px-4 font-bold text-paytm-blue">#{idx + 1}</td>
                <td className="py-2.5 px-4 font-semibold text-paytm-dark">{sku.product_name}</td>
                <td className="py-2.5 px-4 text-paytm-muted">{localizeDynamicText(sku.category, language)}</td>
                <td className="py-2.5 px-4 font-mono text-[11px]">{sku.product_id}</td>
                <td className="py-2.5 px-4 text-right font-bold text-emerald-700">
                  {sku.predicted_7d_units} {language === 'hindi' ? 'इकाईयां' : 'units'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
