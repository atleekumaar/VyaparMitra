import React, { useEffect, useState } from 'react';
import { TrendingUp, Calendar, Package, AlertCircle, Info, Sparkles, ArrowRight, Banknote, Upload } from 'lucide-react';
import { api } from '../api/client';
import { SalesForecast, SKUForecastItem } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { PageHeader } from '../components/PageHeader';
import { SectionHeader } from '../components/SectionHeader';
import { TableSkeleton, CardSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner, EmptyState } from '../components/EmptyState';
import { useLanguage } from '../i18n/LanguageContext';
import { localizeDynamicText } from '../i18n/translations';
import { formatCurrency, formatNumber } from '../utils/formatters';

interface ForecastsPageProps {
  onNavigateTab?: (tab: string) => void;
}

export const ForecastsPage: React.FC<ForecastsPageProps> = ({ onNavigateTab }) => {
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

  const isForecastEmpty =
    (salesForecast.forecast_7d_total_revenue === 0 || !salesForecast.forecast_7d_total_revenue) &&
    demandForecast.length === 0;

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      <PageHeader
        title={language === 'hindi' ? 'बिक्री व मांग का अनुमान (Sales Forecast)' : 'Predictive Sales & Demand Intelligence'}
        subtitle={
          language === 'hindi'
            ? 'अगले 7 दिनों के लिए अनुमानित दुकान की बिक्री और टॉप बिकने वाले सामान की मांग।'
            : 'Multi-day time-series projections and SKU replenishment horizons computed by VyaparMitra ML.'
        }
        actions={
          <Badge variant="info">
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              <span>{salesForecast.model_name || 'Prophet / ARIMA Ensemble'}</span>
            </span>
          </Badge>
        }
      />

      {isForecastEmpty ? (
        <Card className="p-8 sm:p-12 text-center max-w-2xl mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-brand/10 text-brand flex items-center justify-center mx-auto mb-4 border border-brand/20">
            <TrendingUp className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-text">
            Forecast Ke Liye Kam Se Kam 7 Din Ka Data Chahiye
          </h3>
          <p className="text-xs text-text-muted mt-2 leading-relaxed">
            VyaparMitra ML models require at least 7 contiguous days of store sales records to calculate daily seasonality, moving averages, and SKU velocity projections.
          </p>

          {/* Progress Indicator */}
          <div className="mt-6 p-4 rounded-xl bg-surface-muted/60 border border-border text-left">
            <div className="flex items-center justify-between text-xs font-semibold">
              <span className="text-text">Model Training Readiness</span>
              <span className="text-brand tabular-nums">0 / 7 Days Recorded</span>
            </div>
            <div className="w-full bg-surface-muted rounded-full h-2.5 mt-2 overflow-hidden border border-border/40">
              <div className="bg-brand h-2.5 rounded-full w-[10%]" />
            </div>
            <p className="text-[11px] text-text-muted mt-2">
              💡 Tip: Start recording your daily sales counter receipts or upload past CSV invoices to unlock auto-forecasts.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-6">
            {onNavigateTab && (
              <Button
                variant="primary"
                onClick={() => onNavigateTab('dashboard')}
                className="gap-1.5 w-full sm:w-auto"
              >
                <Banknote className="w-4 h-4" />
                <span>Go to Dashboard to Record Sales</span>
              </Button>
            )}
            {onNavigateTab && (
              <Button
                variant="secondary"
                onClick={() => onNavigateTab('products')}
                className="gap-1.5 w-full sm:w-auto"
              >
                <Upload className="w-4 h-4" />
                <span>Upload Inventory CSV</span>
              </Button>
            )}
          </div>
        </Card>
      ) : (
        <>
          {/* KPI Forecast Overview */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card className="p-5">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
                {language === 'hindi' ? '7-दिवसीय अनुमानित कुल बिक्री' : '7-Day Projected Gross Revenue'}
              </span>
              <p className="text-2xl font-bold text-text tabular-nums mt-2">
                {formatCurrency(salesForecast.forecast_7d_total_revenue)}
              </p>
              <div className="mt-2 text-xs text-text-muted">
                {language === 'hindi' ? 'आगामी 7 व्यावसायिक दिनों का कुल योग' : 'Horizon: Next 7 Business Days'}
              </div>
            </Card>

            <Card className="p-5">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
                {language === 'hindi' ? 'बिक्री का रुझान' : 'Predicted Momentum Direction'}
              </span>
              <p className="text-2xl font-bold text-brand mt-2 flex items-center gap-2">
                <TrendingUp className="w-6 h-6" />
                <span>{localizeDynamicText(salesForecast.trend_direction, language)}</span>
              </p>
              <div className="mt-2 text-xs text-text-muted">
                {language === 'hindi' ? 'साप्ताहिक बिक्री की अनुमानित दिशा' : 'Macro trend based on trailing 30-day velocity'}
              </div>
            </Card>

            <Card className="p-5">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
                {language === 'hindi' ? 'दैनिक औसत अनुमान (Daily Run-Rate)' : 'Projected Daily Average'}
              </span>
              <p className="text-2xl font-bold text-success tabular-nums mt-2">
                {formatCurrency(salesForecast.forecast_7d_total_revenue / 7)}
              </p>
              <div className="mt-2 text-xs text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-pulse" />
                <span>High Confidence Model</span>
              </div>
            </Card>
          </div>

          {/* Daily Sales Forecast Strip */}
          <Card className="p-5 sm:p-6">
            <SectionHeader
              title={language === 'hindi' ? 'दैनिक स्टोर बिक्री पूर्वानुमान (अगले 7 दिन)' : 'Daily Store Sales Forecast (Next 7 Days)'}
              subtitle="Expected daily counter receipts computed by time-series seasonality weights"
            />

            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mt-4">
              {salesForecast.daily_forecasts.map((d, i) => (
                <div
                  key={i}
                  className="p-3.5 rounded-xl border border-border bg-surface-muted/40 flex flex-col items-center text-center transition-all hover:border-brand/40 hover:bg-surface"
                >
                  <span className="text-xs text-text-muted font-semibold">
                    {language === 'hindi' ? 'दिन' : 'Day'} {i + 1}
                  </span>
                  <span className="text-[10px] text-text-muted mt-0.5">{d.forecast_date}</span>
                  <span className="text-sm font-bold text-text tabular-nums mt-2">
                    {formatCurrency(d.predicted_revenue)}
                  </span>
                </div>
              ))}
            </div>
          </Card>

          {/* SKU-level Demand Forecast */}
          <Card className="overflow-hidden p-0">
            <div className="px-5 py-4 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Package className="w-4 h-4 text-brand" />
                <SectionHeader
                  title={language === 'hindi' ? 'शीर्ष SKU अनुमानित मांग (अगले 7 दिन)' : 'Top SKU Replenishment Forecast (Next 7 Days)'}
                  subtitle="Units to order before stockout risk emerges"
                  className="mb-0"
                />
              </div>
              <span className="text-xs text-text-muted hidden sm:inline">Ranked by unit velocity</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-muted border-b border-border text-text-muted font-bold uppercase tracking-wider">
                  <tr>
                    <th className="py-2.5 px-4">Rank</th>
                    <th className="py-2.5 px-4">Product Name</th>
                    <th className="py-2.5 px-4">Category</th>
                    <th className="py-2.5 px-4">SKU Code</th>
                    <th className="py-2.5 px-4 text-right">Projected Demand</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {demandForecast.map((sku, idx) => (
                    <tr key={sku.product_id} className="hover:bg-surface-muted/50 transition-colors">
                      <td className="py-2.5 px-4 font-bold text-brand">#{idx + 1}</td>
                      <td className="py-2.5 px-4 font-semibold text-text">{sku.product_name}</td>
                      <td className="py-2.5 px-4 text-text-muted">{localizeDynamicText(sku.category, language)}</td>
                      <td className="py-2.5 px-4 font-mono text-[11px] text-text-muted">{sku.product_id}</td>
                      <td className="py-2.5 px-4 text-right font-bold text-success tabular-nums">
                        {sku.predicted_7d_units} units
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </div>
  );
};
