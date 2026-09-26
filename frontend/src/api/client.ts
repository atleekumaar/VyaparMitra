/**
 * Centralized API client for VyaparMitra Command Center.
 */

import {
  AnomalyItem,
  CategoryShare,
  CopilotMessage,
  CustomerAnalytics,
  CustomerDetail,
  CustomerListItem,
  DashboardSummary,
  HealthStatus,
  PaymentAnalytics,
  ProductAnalytics,
  ProductDetail,
  ProductListItem,
  RecommendationDetail,
  SalesAnalytics,
  SalesForecast,
  SKUForecastItem,
  TrendAnalytics,
  BenchmarkData,
  MerchantInfo,
} from '../types';

const BASE_URL = ((import.meta as any).env?.VITE_API_URL as string) || '';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});
  
  if (!headers.has('Content-Type') && options.method && options.method !== 'GET') {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errJson = await response.json();
      if (errJson?.error?.message) {
        errorMsg = errJson.error.message;
      }
    } catch {
      // Fallback to response statusText
    }
    throw new Error(errorMsg);
  }

  return response.json();
}

export const api = {
  // System Health
  getHealth: () => request<HealthStatus>('/api/health'),

  // Dashboard
  getDashboardSummary: () => request<DashboardSummary>('/api/dashboard/summary'),
  getDashboardActions: (limit: number = 5) =>
    request<{ merchant_id: string; total_actions: number; actions: any[] }>(
      `/api/dashboard/actions?limit=${limit}`
    ),

  // Analytics
  getSalesAnalytics: () => request<SalesAnalytics>('/api/analytics/sales'),
  getCustomerAnalytics: () => request<CustomerAnalytics>('/api/analytics/customers'),
  getProductAnalytics: () => request<ProductAnalytics>('/api/analytics/products'),
  getCategoryAnalytics: () =>
    request<{ categories: CategoryShare[] }>('/api/analytics/categories'),
  getPaymentAnalytics: () => request<PaymentAnalytics>('/api/analytics/payments'),
  getTrendAnalytics: () => request<TrendAnalytics>('/api/analytics/trends'),
  getAnomalyAnalytics: () =>
    request<{ total_anomalies_detected: number; anomalies: AnomalyItem[] }>(
      '/api/analytics/anomalies'
    ),

  // Products
  getProducts: (params?: { category?: string; search?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.category) q.set('category', params.category);
    if (params?.search) q.set('search', params.search);
    if (params?.limit) q.set('limit', String(params.limit));
    return request<ProductListItem[]>(`/api/products?${q.toString()}`);
  },
  getProductDetail: (productId: string) =>
    request<ProductDetail>(`/api/products/${encodeURIComponent(productId)}`),

  // Customers
  getCustomers: (params?: { segment?: string; risk_tier?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.segment) q.set('segment', params.segment);
    if (params?.risk_tier) q.set('risk_tier', params.risk_tier);
    if (params?.limit) q.set('limit', String(params.limit));
    return request<CustomerListItem[]>(`/api/customers?${q.toString()}`);
  },
  getCustomerDetail: (customerId: string) =>
    request<CustomerDetail>(`/api/customers/${encodeURIComponent(customerId)}`),

  // Forecasts
  getSalesForecast: () => request<SalesForecast>('/api/forecasts/sales'),
  getDemandForecast: (limit: number = 30) =>
    request<{ horizon_days: number; top_demand_skus: SKUForecastItem[] }>(
      `/api/forecasts/demand?limit=${limit}`
    ),

  // Recommendations / Action Center
  getRecommendations: (params?: {
    type?: string;
    priority?: string;
    status?: string;
    limit?: number;
  }) => {
    let url = '/api/recommendations';
    const parts = [];
    if (params?.type && params.type !== 'ALL') parts.push(`type=${encodeURIComponent(params.type)}`);
    if (params?.priority && params.priority !== 'ALL') parts.push(`priority=${encodeURIComponent(params.priority)}`);
    if (params?.status && params.status !== 'ALL') parts.push(`status=${encodeURIComponent(params.status)}`);
    if (params?.limit) parts.push(`limit=${params.limit}`);
    
    if (parts.length > 0) {
      url += '?' + parts.join('&');
    }
    
    return request<{ total_count: number; recommendations: RecommendationDetail[] }>(url);
  },
  getRecommendationDetail: (id: string) =>
    request<RecommendationDetail>(`/api/recommendations/${encodeURIComponent(id)}`),
  updateActionStatus: (id: string, newStatus: string) =>
    request<{ recommendation_id: string; previous_status: string; new_status: string; message: string }>(
      `/api/recommendations/${encodeURIComponent(id)}/status`,
      {
        method: 'POST',
        body: JSON.stringify({ status: newStatus }),
      }
    ),

  // Multilingual Copilot
  askCopilot: async (
    query: string,
    sessionId: string = 'merchant_session_1',
    language: string = 'hinglish'
  ): Promise<CopilotMessage> => {
    const res = await request<any>('/api/copilot/ask', {
      method: 'POST',
      body: JSON.stringify({
        query,
        session_id: sessionId,
        merchant_id: 'M001',
        language,
      }),
    });
    return {
      id: Math.random().toString(36).substring(7),
      sender: 'assistant',
      text: res.answer,
      intent: res.intent,
      language: res.language,
      sources: res.sources,
      evidence: res.evidence,
      recommendations: res.recommendations,
      timestamp: res.generated_at || new Date().toISOString(),
    };
  },
  getDailyBrief: async (
    sessionId: string = 'merchant_session_1',
    language: string = 'hinglish'
  ): Promise<CopilotMessage> => {
    const res = await request<{ brief: any }>(
      `/api/copilot/daily-brief?session_id=${sessionId}&language=${language}`
    );
    const b = res.brief;
    return {
      id: Math.random().toString(36).substring(7),
      sender: 'assistant',
      text: b.answer,
      intent: b.intent,
      language: b.language,
      sources: b.sources,
      evidence: b.evidence,
      recommendations: b.recommendations,
      timestamp: b.generated_at || new Date().toISOString(),
    };
  },

  // Benchmarking & Merchants
  getMerchants: () => request<{ total: number; merchants: MerchantInfo[] }>('/api/merchants'),
  getMerchantBenchmark: (merchantId: string = 'M015') =>
    request<BenchmarkData>(`/api/merchants/${merchantId}/benchmark`),

  // Notifications (Twilio WhatsApp & SMS)
  sendWhatsAppDigest: (phone: string, message: string, merchantId?: string) =>
    request<{
      success: boolean;
      status: string;
      message: string;
      to?: string;
      message_sid?: string;
    }>('/api/notifications/whatsapp', {
      method: 'POST',
      body: JSON.stringify({ phone, message, merchant_id: merchantId }),
    }),
  getNotificationStatus: () =>
    request<{
      configured: boolean;
      ready_for_live_delivery: boolean;
      api_key_sid?: string;
      mode: string;
    }>('/api/notifications/status'),
};
