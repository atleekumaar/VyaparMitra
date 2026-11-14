/**
 * Centralized API client for VyaparMitra Command Center.
 * Automatically injects tenant authentication and merchant context
 * (Authorization: Bearer <token> & X-Merchant-Id: <id>) on all requests.
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
  RequestOtpResponse,
  AuthTokenResponse,
  InventoryItem,
  CreateSaleRequest,
  UserProfile,
} from '../types';

const BASE_URL = ((import.meta as any).env?.VITE_API_URL as string) || '';

/**
 * Retrieve active auth token and merchant id from localStorage.
 */
export function getStoredAuthContext(): { token: string | null; merchantId: string | null } {
  try {
    const rawUser = localStorage.getItem('vyaparmitra_user');
    const directToken = localStorage.getItem('vyaparmitra_token');
    if (rawUser) {
      const parsed: UserProfile = JSON.parse(rawUser);
      const mId = parsed.business_id || parsed.merchant_id || parsed.id || null;
      const tok = parsed.token || directToken || null;
      return { token: tok, merchantId: mId };
    }
    return { token: directToken, merchantId: null };
  } catch {
    return { token: null, merchantId: null };
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});
  
  if (!headers.has('Content-Type') && options.method && options.method !== 'GET') {
    headers.set('Content-Type', 'application/json');
  }

  // Inject tenant context headers
  const { token, merchantId } = getStoredAuthContext();
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (merchantId && !headers.has('X-Merchant-Id')) {
    headers.set('X-Merchant-Id', merchantId);
  }

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errJson = await response.json();
      if (errJson?.error?.message) {
        errorMsg = errJson.error.message;
      } else if (errJson?.detail) {
        errorMsg = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
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
  getDashboardSummary: (merchantId?: string) => {
    const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : '';
    return request<DashboardSummary>(`/api/dashboard/summary${q}`);
  },
  getDashboardActions: (limit: number = 5, merchantId?: string) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (merchantId) params.set('merchant_id', merchantId);
    return request<{ merchant_id: string; total_actions: number; actions: any[] }>(
      `/api/dashboard/actions?${params.toString()}`
    );
  },

  // Analytics
  getSalesAnalytics: (merchantId?: string) => {
    const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : '';
    return request<SalesAnalytics>(`/api/analytics/sales${q}`);
  },
  getCustomerAnalytics: (merchantId?: string) => {
    const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : '';
    return request<CustomerAnalytics>(`/api/analytics/customers${q}`);
  },
  getProductAnalytics: (merchantId?: string) => {
    const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : '';
    return request<ProductAnalytics>(`/api/analytics/products${q}`);
  },
  getCategoryAnalytics: (merchantId?: string) => {
    const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : '';
    return request<{ categories: CategoryShare[] }>(`/api/analytics/categories${q}`);
  },
  getPaymentAnalytics: (merchantId?: string) => {
    const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : '';
    return request<PaymentAnalytics>(`/api/analytics/payments${q}`);
  },
  recordCashSale: (data: { amount: number; product_name?: string; category?: string }) =>
    request<{
      status: string;
      message: string;
      amount: number;
      transaction_id: string;
      updated_cash_total: number;
      updated_cash_orders: number;
      timestamp: string;
    }>('/api/analytics/cash-sale', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getTrendAnalytics: (merchantId?: string) => {
    const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : '';
    return request<TrendAnalytics>(`/api/analytics/trends${q}`);
  },
  getAnomalyAnalytics: (merchantId?: string) => {
    const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : '';
    return request<{ total_anomalies_detected: number; anomalies: AnomalyItem[] }>(
      `/api/analytics/anomalies${q}`
    );
  },

  // Products
  getProducts: (params?: { category?: string; search?: string; limit?: number; merchantId?: string }) => {
    const q = new URLSearchParams();
    if (params?.category) q.set('category', params.category);
    if (params?.search) q.set('search', params.search);
    if (params?.limit) q.set('limit', String(params.limit));
    if (params?.merchantId) q.set('merchant_id', params.merchantId);
    return request<ProductListItem[]>(`/api/products?${q.toString()}`);
  },
  getProductDetail: (productId: string, merchantId?: string) => {
    const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : '';
    return request<ProductDetail>(`/api/products/${encodeURIComponent(productId)}${q}`);
  },

  // Operational Inventory
  getInventory: (params?: { category?: string; search?: string; low_stock_only?: boolean; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.category) q.set('category', params.category);
    if (params?.search) q.set('search', params.search);
    if (params?.low_stock_only) q.set('low_stock_only', 'true');
    if (params?.limit) q.set('limit', String(params.limit));
    return request<{ total: number; low_stock_count: number; total_valuation: number; items: InventoryItem[] }>(
      `/api/inventory?${q.toString()}`
    );
  },
  createInventoryItem: (data: {
    product_id: string;
    product_name: string;
    category: string;
    selling_price: number;
    unit_cost?: number;
    current_stock?: number;
    min_stock_threshold?: number;
    barcode?: string;
    unit?: string;
  }) =>
    request<InventoryItem>('/api/inventory', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Operational POS Sales
  createSale: (data: CreateSaleRequest) =>
    request<any>('/api/sales', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Data Import (CSV upload)
  uploadCsv: async (file: File, entityType: 'sales' | 'inventory' | 'customers') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('entity_type', entityType);

    const { token, merchantId } = getStoredAuthContext();
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (merchantId) headers['X-Merchant-Id'] = merchantId;

    const res = await fetch(`${BASE_URL}/api/import-data/csv`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || err.message || `CSV import failed (${res.status})`);
    }
    return res.json();
  },

  // Customers
  getCustomers: (params?: { segment?: string; risk_tier?: string; limit?: number; merchantId?: string }) => {
    const q = new URLSearchParams();
    if (params?.segment) q.set('segment', params.segment);
    if (params?.risk_tier) q.set('risk_tier', params.risk_tier);
    if (params?.limit) q.set('limit', String(params.limit));
    if (params?.merchantId) q.set('merchant_id', params.merchantId);
    return request<CustomerListItem[]>(`/api/customers?${q.toString()}`);
  },
  getCustomerDetail: (customerId: string, merchantId?: string) => {
    const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : '';
    return request<CustomerDetail>(`/api/customers/${encodeURIComponent(customerId)}${q}`);
  },

  // Forecasts
  getSalesForecast: (merchantId?: string) => {
    const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : '';
    return request<SalesForecast>(`/api/forecasts/sales${q}`);
  },
  getDemandForecast: (limit: number = 30, merchantId?: string) => {
    const q = new URLSearchParams({ limit: String(limit) });
    if (merchantId) q.set('merchant_id', merchantId);
    return request<{ horizon_days: number; top_demand_skus: SKUForecastItem[] }>(
      `/api/forecasts/demand?${q.toString()}`
    );
  },

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
    const { merchantId } = getStoredAuthContext();
    const res = await request<any>('/api/copilot/ask', {
      method: 'POST',
      body: JSON.stringify({
        query,
        session_id: sessionId,
        merchant_id: merchantId || 'M001',
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
  getMerchantBenchmark: (merchantId?: string) => {
    const { merchantId: currentMId } = getStoredAuthContext();
    const targetId = merchantId || currentMId || 'M001';
    return request<BenchmarkData>(`/api/merchants/${encodeURIComponent(targetId)}/benchmark`);
  },

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

  // OTP Authentication (Brevo SMTP & Mobile OTP)
  requestOtp: (data: { email: string; phone?: string; name?: string }) =>
    request<RequestOtpResponse>('/api/auth/otp/send', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  verifyOtp: (data: { email: string; otp: string; phone?: string; name?: string; store_id?: string }) =>
    request<AuthTokenResponse>('/api/auth/otp/verify', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
