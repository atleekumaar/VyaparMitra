/**
 * TypeScript Data Models matching VyaparMitra backend contracts.
 */

export interface MetricCardData {
  label: string;
  value: number | string;
  formatted_value: string;
  change_pct?: number | null;
  trend?: 'UP' | 'DOWN' | 'STABLE' | null;
  subtext?: string | null;
}

export interface DashboardSummary {
  merchant_id: string;
  merchant_name: string;
  date_range: string;
  kpis: {
    revenue: MetricCardData;
    orders: MetricCardData;
    aov: MetricCardData;
    units: MetricCardData;
  };
  sales_trend_direction: string;
  forecast_7d_total_revenue: number;
  total_actions_pending: number;
  critical_actions_count: number;
  demo_mode: boolean;
}

export interface ActionItem {
  recommendation_id: string;
  type: string;
  priority_band: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  priority_score: number;
  title: string;
  action: string;
  reason: string;
  expected_impact: number;
  entity_id?: string | null;
  status: 'GENERATED' | 'VIEWED' | 'ACCEPTED' | 'REJECTED' | 'EXECUTED' | 'EXPIRED';
  evidence_snippet?: string | null;
}

export interface DailySalesPoint {
  date: string;
  revenue: number;
  orders: number;
  units?: number | null;
  average_order_value?: number | null;
}

export interface SalesAnalytics {
  total_revenue: number;
  total_orders: number;
  average_order_value: number;
  discount_rate: number;
  daily_series: DailySalesPoint[];
}

export interface CustomerSegment {
  segment_name: string;
  customer_count: number;
  total_revenue: number;
  revenue_share: number;
}

export interface CustomerAnalytics {
  total_customers: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  segments: CustomerSegment[];
}

export interface ProductRank {
  product_id: string;
  product_name: string;
  category: string;
  revenue: number;
  units: number;
  rank: number;
}

export interface ProductAnalytics {
  total_products_tracked: number;
  top_performers: ProductRank[];
  pareto_80_20_ratio?: number | null;
}

export interface CategoryShare {
  category: string;
  revenue: number;
  orders: number;
  revenue_share: number;
}

export interface PaymentMethodShare {
  payment_method: string;
  transaction_count: number;
  total_revenue: number;
  revenue_share: number;
}

export interface PaymentAnalytics {
  payment_methods: PaymentMethodShare[];
  primary_payment_method: string;
}

export interface TrendAnalytics {
  predicted_trend: string;
  confidence: number;
  horizon_days: number;
  historical_revenue_change_pct: number;
}

export interface AnomalyItem {
  date: string;
  metric: string;
  observed_value: number;
  expected_value: number;
  deviation_score: number;
  is_anomaly: boolean;
}

export interface ProductListItem {
  product_id: string;
  product_name: string;
  category: string;
  selling_price: number;
  total_revenue: number;
  total_units: number;
  forecast_7d_units: number;
  status: 'STAR' | 'FOCUS' | 'MONITOR';
}

export interface ProductDetail extends ProductListItem {
  unit_cost: number;
  margin: number;
  total_units_sold: number;
  cross_sell_recommendations: Array<{
    paired_sku: string;
    confidence: number;
    action: string;
  }>;
  active_recommendations: ActionItem[];
  stock_status_text?: string;
}

export interface CustomerListItem {
  customer_id: string;
  segment: string;
  lifetime_spend: number;
  total_orders: number;
  recency_days: number;
  churn_risk_tier: string;
  churn_probability: number;
}

export interface CustomerDetail extends CustomerListItem {
  suggested_retention_action?: string | null;
  evidence: Array<{
    metric?: string;
    value?: string | number;
    source?: string;
    description?: string;
  }>;
}

export interface DailySalesForecastItem {
  forecast_date: string;
  predicted_revenue: number;
}

export interface SalesForecast {
  forecast_7d_total_revenue: number;
  forecast_horizon_days: number;
  model_name: string;
  daily_forecasts: DailySalesForecastItem[];
  trend_direction: string;
}

export interface SKUForecastItem {
  product_id: string;
  product_name: string;
  category: string;
  predicted_7d_units: number;
}

export interface EvidenceDetail {
  metric: string;
  value: string | number;
  source: string;
  description?: string | null;
}

export interface RecommendationDetail {
  recommendation_id: string;
  type: string;
  priority_band: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  priority_score: number;
  title: string;
  action: string;
  reason: string;
  expected_impact: number;
  entity_id?: string | null;
  status: string;
  evidence: EvidenceDetail[];
  generated_at: string;
}

export interface CopilotMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  intent?: string;
  language?: string;
  sources?: Array<{
    source: string;
    artifact: string;
    description?: string;
  }>;
  evidence?: Array<Record<string, any>>;
  recommendations?: Array<Record<string, any>>;
  timestamp: string;
}

export interface HealthStatus {
  status: string;
  version: string;
  app_env: string;
  demo_mode: boolean;
  active_copilot_sessions: number;
  artifacts_ready: boolean;
  checked_at: string;
}

export interface BenchmarkMetric {
  name: string;
  label: string;
  label_hi?: string | null;
  unit: string;
  you: number;
  peer_median: number;
  peer_min: number;
  peer_max: number;
  percentile: number;
  status: 'green' | 'yellow' | 'red';
  status_text: string;
  status_text_hi?: string | null;
  higher_is_better: boolean;
  action: string;
  action_hi?: string | null;
}

export interface BenchmarkData {
  merchant_id: string;
  merchant_name: string;
  business_type: string;
  city: string;
  state: string;
  peer_group: string;
  peer_count: number;
  is_fallback_group: boolean;
  fallback_reason?: string | null;
  rank: number;
  overall_score: number;
  metrics: BenchmarkMetric[];
  top_performer_practices: string[];
  whatsapp_digest?: string | null;
}

export interface MerchantInfo {
  merchant_id: string;
  merchant_name: string;
  business_type: string;
  city: string;
  state: string;
}

