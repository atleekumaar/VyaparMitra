-- ====================================================================
-- VyaparMitra Complete Supabase PostgreSQL Schema & Multi-Tenant Setup
-- Generated for Supabase Project: pthcubbwukibmmmsmjpm
-- Run directly in Supabase Dashboard -> SQL Editor -> New Query
-- ====================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- --------------------------------------------------------------------
-- 1. DDL: Table Definitions
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public."businesses" (
    "id" TEXT PRIMARY KEY,
    "name" TEXT NOT NULL,
    "business_type" TEXT DEFAULT 'Retail',
    "gstin" TEXT,
    "phone" TEXT,
    "email" TEXT,
    "address" TEXT,
    "city" TEXT,
    "state" TEXT,
    "created_at" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."branches" (
    "id" TEXT PRIMARY KEY,
    "business_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "code" TEXT,
    "city" TEXT,
    "state" TEXT,
    "address" TEXT,
    "phone" TEXT,
    "is_main" INTEGER DEFAULT 1,
    "created_at" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."users" (
    "id" TEXT PRIMARY KEY,
    "business_id" TEXT NOT NULL,
    "branch_id" TEXT,
    "username" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "full_name" TEXT NOT NULL,
    "password_hash" TEXT NOT NULL,
    "role" TEXT NOT NULL,
    "phone" TEXT,
    "is_active" INTEGER DEFAULT 1,
    "created_at" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."inventory" (
    "id" TEXT PRIMARY KEY,
    "business_id" TEXT NOT NULL,
    "branch_id" TEXT NOT NULL,
    "product_id" TEXT NOT NULL,
    "product_name" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "current_stock" INTEGER NOT NULL DEFAULT 0,
    "min_stock_threshold" INTEGER NOT NULL DEFAULT 10,
    "unit_cost" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "selling_price" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "barcode" TEXT,
    "unit" TEXT DEFAULT 'pcs',
    "updated_at" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."sales" (
    "id" TEXT PRIMARY KEY,
    "invoice_number" TEXT NOT NULL,
    "business_id" TEXT NOT NULL,
    "branch_id" TEXT NOT NULL,
    "customer_id" TEXT,
    "customer_name" TEXT,
    "subtotal" DOUBLE PRECISION NOT NULL,
    "discount" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "tax" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "total_amount" DOUBLE PRECISION NOT NULL,
    "payment_method" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'COMPLETED',
    "created_by" TEXT NOT NULL,
    "created_by_name" TEXT,
    "notes" TEXT,
    "created_at" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."sale_items" (
    "id" TEXT PRIMARY KEY,
    "sale_id" TEXT NOT NULL,
    "product_id" TEXT NOT NULL,
    "product_name" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL,
    "unit_price" DOUBLE PRECISION NOT NULL,
    "unit_cost" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "discount" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "total_price" DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS public."customers" (
    "id" TEXT PRIMARY KEY,
    "business_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "phone" TEXT,
    "email" TEXT,
    "address" TEXT,
    "city" TEXT,
    "credit_limit" DOUBLE PRECISION NOT NULL DEFAULT 5000.0,
    "current_balance" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "loyalty_points" INTEGER DEFAULT 0,
    "status" TEXT DEFAULT 'ACTIVE',
    "created_at" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."customer_ledgers" (
    "id" TEXT PRIMARY KEY,
    "business_id" TEXT NOT NULL,
    "customer_id" TEXT NOT NULL,
    "entry_type" TEXT NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "balance_after" DOUBLE PRECISION NOT NULL,
    "reference_id" TEXT,
    "notes" TEXT,
    "created_by" TEXT,
    "created_at" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."suppliers" (
    "id" TEXT PRIMARY KEY,
    "business_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "contact_person" TEXT,
    "phone" TEXT,
    "email" TEXT,
    "address" TEXT,
    "gstin" TEXT,
    "current_payable" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "payment_terms" TEXT DEFAULT 'Net 30',
    "status" TEXT DEFAULT 'ACTIVE',
    "created_at" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."supplier_invoices" (
    "id" TEXT PRIMARY KEY,
    "invoice_number" TEXT NOT NULL,
    "business_id" TEXT NOT NULL,
    "branch_id" TEXT NOT NULL,
    "supplier_id" TEXT NOT NULL,
    "total_amount" DOUBLE PRECISION NOT NULL,
    "paid_amount" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "status" TEXT NOT NULL DEFAULT 'UNPAID',
    "items_json" TEXT,
    "notes" TEXT,
    "created_by" TEXT,
    "created_at" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."expenses" (
    "id" TEXT PRIMARY KEY,
    "business_id" TEXT NOT NULL,
    "branch_id" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "payment_method" TEXT NOT NULL,
    "description" TEXT,
    "receipt_url" TEXT,
    "created_by" TEXT NOT NULL,
    "created_at" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."audit_logs" (
    "id" TEXT PRIMARY KEY,
    "business_id" TEXT NOT NULL,
    "branch_id" TEXT,
    "user_id" TEXT NOT NULL,
    "user_name" TEXT NOT NULL,
    "user_role" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "resource" TEXT NOT NULL,
    "resource_id" TEXT,
    "details" TEXT,
    "ip_address" TEXT,
    "timestamp" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."agent_approvals" (
    "id" TEXT PRIMARY KEY,
    "business_id" TEXT NOT NULL,
    "branch_id" TEXT,
    "action_type" TEXT NOT NULL DEFAULT 'PURCHASE_REORDER',
    "sku" TEXT NOT NULL,
    "product_name" TEXT,
    "quantity" INTEGER NOT NULL,
    "unit_cost" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "estimated_cost" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "vendor" TEXT DEFAULT 'Standard Supplier',
    "status" TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
    "requested_by" TEXT NOT NULL,
    "requested_by_role" TEXT NOT NULL,
    "reviewed_by" TEXT,
    "review_notes" TEXT,
    "created_at" TEXT NOT NULL,
    "reviewed_at" TEXT
);

CREATE TABLE IF NOT EXISTS public."otps" (
    "id" TEXT PRIMARY KEY,
    "identifier" TEXT NOT NULL,
    "otp_code" TEXT NOT NULL,
    "purpose" TEXT DEFAULT 'LOGIN',
    "expires_at" TEXT NOT NULL,
    "attempts" INTEGER DEFAULT 0,
    "is_used" INTEGER DEFAULT 0,
    "created_at" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public."all_recommendations" (
    "recommendation_id" TEXT,
    "merchant_id" TEXT,
    "type" TEXT,
    "priority" DOUBLE PRECISION,
    "priority_band" TEXT,
    "confidence" DOUBLE PRECISION,
    "urgency" DOUBLE PRECISION,
    "expected_impact" DOUBLE PRECISION,
    "entity_type" TEXT,
    "entity_id" TEXT,
    "title" TEXT,
    "action" TEXT,
    "reason" TEXT,
    "created_at" TEXT,
    "status" TEXT
);

CREATE TABLE IF NOT EXISTS public."anomaly_analysis" (
    "date" TEXT,
    "metric" TEXT,
    "value" DOUBLE PRECISION,
    "baseline" DOUBLE PRECISION,
    "deviation" DOUBLE PRECISION,
    "method" TEXT,
    "status" TEXT
);

CREATE TABLE IF NOT EXISTS public."business_trend_predictions" (
    "prediction_date" TEXT,
    "horizon_days" INTEGER,
    "predicted_trend" TEXT,
    "confidence" DOUBLE PRECISION,
    "model_name" TEXT,
    "model_version" TEXT
);

CREATE TABLE IF NOT EXISTS public."category_monthly" (
    "product_category" TEXT,
    "month_key" TEXT,
    "category_revenue" DOUBLE PRECISION,
    "category_units" INTEGER,
    "category_orders" INTEGER
);

CREATE TABLE IF NOT EXISTS public."category_summary" (
    "product_category" TEXT,
    "category_revenue" DOUBLE PRECISION,
    "category_units" INTEGER,
    "category_orders" INTEGER,
    "unique_customers" INTEGER,
    "average_order_value" DOUBLE PRECISION,
    "revenue_share" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."churn_feature_importance" (
    "feature" TEXT,
    "importance" DOUBLE PRECISION,
    "std" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."clean_customers" (
    "customer_id" TEXT,
    "customer_name" TEXT,
    "customer_type" TEXT,
    "city" TEXT,
    "signup_date" TEXT
);

CREATE TABLE IF NOT EXISTS public."clean_festivals" (
    "date" TEXT,
    "festival_name" TEXT,
    "festival_type" TEXT,
    "is_festival" INTEGER,
    "festival_intensity" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."clean_merchants" (
    "merchant_id" TEXT,
    "merchant_name" TEXT,
    "business_type" TEXT,
    "city" TEXT,
    "state" TEXT,
    "pincode" TEXT,
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."clean_products" (
    "product_id" TEXT,
    "product_name" TEXT,
    "product_category" TEXT,
    "unit_cost" DOUBLE PRECISION,
    "selling_price" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."clean_transactions" (
    "transaction_id" TEXT,
    "merchant_id" TEXT,
    "customer_id" TEXT,
    "timestamp" TEXT,
    "product_id" TEXT,
    "product_category" TEXT,
    "quantity" INTEGER,
    "unit_price" DOUBLE PRECISION,
    "discount" DOUBLE PRECISION,
    "payment_method" TEXT
);

CREATE TABLE IF NOT EXISTS public."clean_weather" (
    "date" TEXT,
    "city" TEXT,
    "temperature" DOUBLE PRECISION,
    "humidity" DOUBLE PRECISION,
    "rainfall" DOUBLE PRECISION,
    "weather_condition" TEXT
);

CREATE TABLE IF NOT EXISTS public."cross_sell_recommendations" (
    "recommendation_id" TEXT,
    "merchant_id" TEXT,
    "type" TEXT,
    "priority" DOUBLE PRECISION,
    "priority_band" TEXT,
    "confidence" DOUBLE PRECISION,
    "urgency" DOUBLE PRECISION,
    "expected_impact" DOUBLE PRECISION,
    "entity_type" TEXT,
    "entity_id" TEXT,
    "title" TEXT,
    "action" TEXT,
    "reason" TEXT,
    "created_at" TEXT,
    "status" TEXT
);

CREATE TABLE IF NOT EXISTS public."customer_cohorts" (
    "cohort_month" TEXT,
    "cohort_size" DOUBLE PRECISION,
    "M1" DOUBLE PRECISION,
    "M2" DOUBLE PRECISION,
    "M3" DOUBLE PRECISION,
    "M4" DOUBLE PRECISION,
    "M5" DOUBLE PRECISION,
    "M6" DOUBLE PRECISION,
    "M7" DOUBLE PRECISION,
    "M8" DOUBLE PRECISION,
    "M9" DOUBLE PRECISION,
    "M10" DOUBLE PRECISION,
    "M11" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."customer_features" (
    "customer_id" TEXT,
    "customer_name" TEXT,
    "customer_type" TEXT,
    "city" TEXT,
    "signup_date" TEXT,
    "customer_total_spend" DOUBLE PRECISION,
    "customer_order_count" INTEGER,
    "customer_average_order_value" DOUBLE PRECISION,
    "customer_recency" DOUBLE PRECISION,
    "customer_purchase_frequency" DOUBLE PRECISION,
    "customer_first_purchase" TEXT,
    "customer_last_purchase" TEXT
);

CREATE TABLE IF NOT EXISTS public."customer_recommendations" (
    "recommendation_id" TEXT,
    "merchant_id" TEXT,
    "type" TEXT,
    "priority" DOUBLE PRECISION,
    "priority_band" TEXT,
    "confidence" DOUBLE PRECISION,
    "urgency" DOUBLE PRECISION,
    "expected_impact" DOUBLE PRECISION,
    "entity_type" TEXT,
    "entity_id" TEXT,
    "title" TEXT,
    "action" TEXT,
    "reason" TEXT,
    "created_at" TEXT,
    "status" TEXT
);

CREATE TABLE IF NOT EXISTS public."customer_risk_scores" (
    "customer_id" TEXT,
    "snapshot_date" TEXT,
    "risk_probability" DOUBLE PRECISION,
    "risk_band" TEXT,
    "model_name" TEXT,
    "model_version" TEXT
);

CREATE TABLE IF NOT EXISTS public."customer_segments" (
    "customer_id" TEXT,
    "customer_name" TEXT,
    "customer_type" TEXT,
    "city" TEXT,
    "customer_recency" DOUBLE PRECISION,
    "customer_order_count" INTEGER,
    "customer_total_spend" DOUBLE PRECISION,
    "r_score" INTEGER,
    "f_score" INTEGER,
    "m_score" INTEGER,
    "rfm_score" TEXT,
    "rfm_segment" TEXT
);

CREATE TABLE IF NOT EXISTS public."customer_summary" (
    "total_customers" INTEGER,
    "active_customers" INTEGER,
    "repeat_customers" INTEGER,
    "one_time_customers" INTEGER,
    "average_customer_spend" DOUBLE PRECISION,
    "average_orders_per_customer" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."daily_features" (
    "date" TEXT,
    "daily_total_revenue" DOUBLE PRECISION,
    "daily_total_orders" INTEGER,
    "daily_total_units" INTEGER,
    "daily_active_merchants" INTEGER,
    "daily_active_customers" INTEGER,
    "daily_avg_order_value" DOUBLE PRECISION,
    "is_festival" INTEGER,
    "festival_intensity" DOUBLE PRECISION,
    "days_to_festival" INTEGER,
    "days_after_festival" INTEGER,
    "avg_temperature" DOUBLE PRECISION,
    "avg_humidity" DOUBLE PRECISION,
    "total_rainfall" DOUBLE PRECISION,
    "is_rainy_day" INTEGER,
    "day_of_week" INTEGER,
    "day_name" TEXT,
    "day_of_month" INTEGER,
    "week_of_year" INTEGER,
    "month" INTEGER,
    "quarter" INTEGER,
    "year" INTEGER,
    "is_weekend" INTEGER,
    "is_month_start" INTEGER,
    "is_month_end" INTEGER,
    "lag_1d_revenue" DOUBLE PRECISION,
    "lag_7d_revenue" DOUBLE PRECISION,
    "rolling_7d_avg_revenue" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."demand_feature_importance" (
    "feature" TEXT,
    "importance" DOUBLE PRECISION,
    "std" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."festival_analysis" (
    "festival_name" TEXT,
    "sample_size" INTEGER,
    "avg_daily_revenue" DOUBLE PRECISION,
    "avg_daily_orders" DOUBLE PRECISION,
    "total_festival_revenue" DOUBLE PRECISION,
    "vs_non_festival_revenue_pct" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."inventory_recommendations" (
    "recommendation_id" TEXT,
    "merchant_id" TEXT,
    "type" TEXT,
    "priority" DOUBLE PRECISION,
    "priority_band" TEXT,
    "confidence" DOUBLE PRECISION,
    "urgency" DOUBLE PRECISION,
    "expected_impact" DOUBLE PRECISION,
    "entity_type" TEXT,
    "entity_id" TEXT,
    "title" TEXT,
    "action" TEXT,
    "reason" TEXT,
    "created_at" TEXT,
    "status" TEXT
);

CREATE TABLE IF NOT EXISTS public."merchant_action_plan" (
    "recommendation_id" TEXT,
    "merchant_id" TEXT,
    "type" TEXT,
    "priority" DOUBLE PRECISION,
    "priority_band" TEXT,
    "confidence" DOUBLE PRECISION,
    "urgency" DOUBLE PRECISION,
    "expected_impact" DOUBLE PRECISION,
    "entity_type" TEXT,
    "entity_id" TEXT,
    "title" TEXT,
    "action" TEXT,
    "reason" TEXT,
    "created_at" TEXT,
    "status" TEXT
);

CREATE TABLE IF NOT EXISTS public."merchant_benchmarks" (
    "merchant_id" TEXT,
    "merchant_name" TEXT,
    "business_type" TEXT,
    "city" TEXT,
    "merchant_revenue" DOUBLE PRECISION,
    "peer_mean_revenue" DOUBLE PRECISION,
    "revenue_vs_peer_pct" DOUBLE PRECISION,
    "merchant_aov" DOUBLE PRECISION,
    "peer_mean_aov" DOUBLE PRECISION,
    "aov_vs_peer_pct" DOUBLE PRECISION,
    "merchant_orders" INTEGER,
    "peer_mean_orders" DOUBLE PRECISION,
    "orders_vs_peer_pct" DOUBLE PRECISION,
    "revenue_percentile" DOUBLE PRECISION,
    "benchmark_type" TEXT
);

CREATE TABLE IF NOT EXISTS public."merchant_features" (
    "merchant_id" TEXT,
    "merchant_name" TEXT,
    "business_type" TEXT,
    "city" TEXT,
    "state" TEXT,
    "pincode" TEXT,
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION,
    "merchant_total_revenue" DOUBLE PRECISION,
    "merchant_total_orders" INTEGER,
    "average_order_value" DOUBLE PRECISION,
    "unique_customers" INTEGER,
    "unique_products" INTEGER,
    "active_days" INTEGER,
    "revenue_per_day" DOUBLE PRECISION,
    "orders_per_day" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."merchant_summary" (
    "merchant_id" TEXT,
    "merchant_name" TEXT,
    "business_type" TEXT,
    "city" TEXT,
    "state" TEXT,
    "merchant_revenue" DOUBLE PRECISION,
    "merchant_orders" INTEGER,
    "merchant_units" INTEGER,
    "merchant_aov" DOUBLE PRECISION,
    "active_days" INTEGER,
    "unique_customers" INTEGER,
    "unique_products" INTEGER,
    "revenue_per_day" DOUBLE PRECISION,
    "orders_per_day" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."payment_summary" (
    "payment_method" TEXT,
    "payment_method_orders" INTEGER,
    "payment_method_revenue" DOUBLE PRECISION,
    "orders_share" DOUBLE PRECISION,
    "revenue_share" DOUBLE PRECISION,
    "payment_method_aov" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."pricing_recommendations" (
    "recommendation_id" TEXT,
    "merchant_id" TEXT,
    "type" TEXT,
    "priority" DOUBLE PRECISION,
    "priority_band" TEXT,
    "confidence" DOUBLE PRECISION,
    "urgency" DOUBLE PRECISION,
    "expected_impact" DOUBLE PRECISION,
    "entity_type" TEXT,
    "entity_id" TEXT,
    "title" TEXT,
    "action" TEXT,
    "reason" TEXT,
    "created_at" TEXT,
    "status" TEXT
);

CREATE TABLE IF NOT EXISTS public."product_demand_forecast_30d" (
    "forecast_date" TEXT,
    "product_id" TEXT,
    "product_category" TEXT,
    "predicted_units" DOUBLE PRECISION,
    "model_name" TEXT,
    "model_version" TEXT
);

CREATE TABLE IF NOT EXISTS public."product_demand_forecast_7d" (
    "forecast_date" TEXT,
    "product_id" TEXT,
    "product_category" TEXT,
    "predicted_units" DOUBLE PRECISION,
    "model_name" TEXT,
    "model_version" TEXT
);

CREATE TABLE IF NOT EXISTS public."product_features" (
    "product_id" TEXT,
    "product_name" TEXT,
    "product_category" TEXT,
    "unit_cost" DOUBLE PRECISION,
    "selling_price" DOUBLE PRECISION,
    "product_sales" INTEGER,
    "product_revenue" DOUBLE PRECISION,
    "product_order_count" INTEGER,
    "unique_customers" INTEGER,
    "average_quantity" DOUBLE PRECISION,
    "average_selling_price" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."product_rankings" (
    "product_id" TEXT,
    "product_name" TEXT,
    "product_category" TEXT,
    "revenue" DOUBLE PRECISION,
    "units" INTEGER,
    "orders" INTEGER,
    "unique_customers" INTEGER,
    "rank_by_revenue" INTEGER,
    "rank_by_units" INTEGER,
    "rank_by_orders" INTEGER,
    "rank_by_customers" INTEGER
);

CREATE TABLE IF NOT EXISTS public."product_summary" (
    "product_id" TEXT,
    "product_name" TEXT,
    "product_category" TEXT,
    "revenue" DOUBLE PRECISION,
    "units" INTEGER,
    "orders" INTEGER,
    "unique_customers" INTEGER,
    "average_price" DOUBLE PRECISION,
    "revenue_share" DOUBLE PRECISION,
    "unit_share" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."recommendation_evidence" (
    "recommendation_id" TEXT,
    "entity_id" TEXT,
    "metric" TEXT,
    "value" TEXT,
    "source" TEXT,
    "description" TEXT
);

CREATE TABLE IF NOT EXISTS public."sales_daily" (
    "period" TEXT,
    "period_key" TEXT,
    "period_start" TEXT,
    "period_end" TEXT,
    "revenue" DOUBLE PRECISION,
    "orders" INTEGER,
    "units" INTEGER,
    "aov" DOUBLE PRECISION,
    "discount" DOUBLE PRECISION,
    "revenue_change" DOUBLE PRECISION,
    "revenue_growth_pct" DOUBLE PRECISION,
    "orders_change" DOUBLE PRECISION,
    "orders_growth_pct" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."sales_feature_importance" (
    "feature" TEXT,
    "importance" DOUBLE PRECISION,
    "std" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."sales_forecast_30d" (
    "forecast_date" TEXT,
    "predicted_revenue" DOUBLE PRECISION,
    "lower_bound" TEXT,
    "upper_bound" TEXT,
    "model_name" TEXT,
    "model_version" TEXT,
    "generated_at" TEXT
);

CREATE TABLE IF NOT EXISTS public."sales_forecast_7d" (
    "forecast_date" TEXT,
    "predicted_revenue" DOUBLE PRECISION,
    "lower_bound" TEXT,
    "upper_bound" TEXT,
    "model_name" TEXT,
    "model_version" TEXT,
    "generated_at" TEXT
);

CREATE TABLE IF NOT EXISTS public."sales_monthly" (
    "period" TEXT,
    "period_key" TEXT,
    "period_start" TEXT,
    "period_end" TEXT,
    "revenue" DOUBLE PRECISION,
    "orders" INTEGER,
    "units" INTEGER,
    "aov" DOUBLE PRECISION,
    "discount" DOUBLE PRECISION,
    "revenue_change" DOUBLE PRECISION,
    "revenue_growth_pct" DOUBLE PRECISION,
    "orders_change" DOUBLE PRECISION,
    "orders_growth_pct" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."sales_opportunities" (
    "recommendation_id" TEXT,
    "merchant_id" TEXT,
    "type" TEXT,
    "priority" DOUBLE PRECISION,
    "priority_band" TEXT,
    "confidence" DOUBLE PRECISION,
    "urgency" DOUBLE PRECISION,
    "expected_impact" DOUBLE PRECISION,
    "entity_type" TEXT,
    "entity_id" TEXT,
    "title" TEXT,
    "action" TEXT,
    "reason" TEXT,
    "created_at" TEXT,
    "status" TEXT
);

CREATE TABLE IF NOT EXISTS public."sales_summary" (
    "total_revenue" DOUBLE PRECISION,
    "total_orders" INTEGER,
    "total_units" INTEGER,
    "average_order_value" DOUBLE PRECISION,
    "average_units_per_order" DOUBLE PRECISION,
    "discount_total" DOUBLE PRECISION,
    "discount_rate" DOUBLE PRECISION,
    "revenue_per_active_day" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."sales_weekly" (
    "period" TEXT,
    "period_key" TEXT,
    "period_start" TEXT,
    "period_end" TEXT,
    "revenue" DOUBLE PRECISION,
    "orders" INTEGER,
    "units" INTEGER,
    "aov" DOUBLE PRECISION,
    "discount" DOUBLE PRECISION,
    "revenue_change" DOUBLE PRECISION,
    "revenue_growth_pct" DOUBLE PRECISION,
    "orders_change" DOUBLE PRECISION,
    "orders_growth_pct" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."time_hourly" (
    "hour" INTEGER,
    "orders" INTEGER,
    "revenue" DOUBLE PRECISION,
    "units" INTEGER,
    "aov" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."time_monthly" (
    "month_key" TEXT,
    "year" INTEGER,
    "month" INTEGER,
    "revenue" DOUBLE PRECISION,
    "orders" INTEGER,
    "units" INTEGER,
    "aov" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."time_weekday" (
    "day_of_week" INTEGER,
    "day_name" TEXT,
    "orders" INTEGER,
    "revenue" DOUBLE PRECISION,
    "units" INTEGER,
    "aov" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."transaction_features" (
    "transaction_id" TEXT,
    "merchant_id" TEXT,
    "customer_id" TEXT,
    "timestamp" TEXT,
    "product_id" TEXT,
    "product_category" TEXT,
    "quantity" INTEGER,
    "unit_price" DOUBLE PRECISION,
    "discount" DOUBLE PRECISION,
    "payment_method" TEXT,
    "total_amount" DOUBLE PRECISION,
    "discount_amount" DOUBLE PRECISION,
    "net_amount" DOUBLE PRECISION,
    "date" TEXT,
    "day" INTEGER,
    "day_of_week" INTEGER,
    "day_name" TEXT,
    "hour" INTEGER,
    "week" INTEGER,
    "month" INTEGER,
    "quarter" INTEGER,
    "year" INTEGER,
    "is_weekend" INTEGER,
    "is_month_start" INTEGER,
    "is_month_end" INTEGER,
    "festival_name" TEXT,
    "festival_type" TEXT,
    "is_festival" INTEGER,
    "festival_intensity" DOUBLE PRECISION,
    "days_to_festival" INTEGER,
    "days_after_festival" INTEGER,
    "city" TEXT,
    "temperature" DOUBLE PRECISION,
    "humidity" DOUBLE PRECISION,
    "rainfall" DOUBLE PRECISION,
    "weather_condition" TEXT,
    "is_rainy" INTEGER
);

CREATE TABLE IF NOT EXISTS public."trend_analysis" (
    "period" TEXT,
    "period_key" TEXT,
    "metric" TEXT,
    "value" DOUBLE PRECISION,
    "moving_average" DOUBLE PRECISION,
    "absolute_change" DOUBLE PRECISION,
    "percentage_change" DOUBLE PRECISION,
    "trend_classification" TEXT
);

CREATE TABLE IF NOT EXISTS public."trend_feature_importance" (
    "feature" TEXT,
    "importance" DOUBLE PRECISION,
    "std" DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS public."weather_analysis" (
    "weather_condition" TEXT,
    "sample_size" INTEGER,
    "avg_daily_revenue" DOUBLE PRECISION,
    "avg_daily_orders" DOUBLE PRECISION,
    "total_revenue" DOUBLE PRECISION
);

-- --------------------------------------------------------------------
-- 2. Performance & Multi-Tenant Indexes
-- --------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_users_business ON public."users"("business_id");
CREATE INDEX IF NOT EXISTS idx_users_username ON public."users"("username");
CREATE INDEX IF NOT EXISTS idx_users_email ON public."users"("email");
CREATE INDEX IF NOT EXISTS idx_inventory_lookup ON public."inventory"("business_id", "branch_id");
CREATE INDEX IF NOT EXISTS idx_sales_lookup ON public."sales"("business_id", "branch_id", "created_at");
CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON public."sale_items"("sale_id");
CREATE INDEX IF NOT EXISTS idx_customers_business ON public."customers"("business_id");
CREATE INDEX IF NOT EXISTS idx_customer_ledgers ON public."customer_ledgers"("business_id", "customer_id");
CREATE INDEX IF NOT EXISTS idx_expenses_lookup ON public."expenses"("business_id", "branch_id", "created_at");
CREATE INDEX IF NOT EXISTS idx_audit_logs_lookup ON public."audit_logs"("business_id", "timestamp");
CREATE INDEX IF NOT EXISTS idx_agent_approvals_lookup ON public."agent_approvals"("business_id", "status");
CREATE INDEX IF NOT EXISTS idx_otps_lookup ON public."otps"("identifier", "is_used", "expires_at");

-- --------------------------------------------------------------------
-- 3. Core Baseline Seed Data (Businesses, Branches, Users, Inventory)
-- --------------------------------------------------------------------
INSERT INTO public."businesses" ("id", "name", "business_type", "gstin", "phone", "email", "address", "city", "state", "created_at")
VALUES
  ('M015', 'Merchant_015 Bakery & Retail', 'Bakery', '07AAAAA0000A1Z5', '+919876543210', 'contact@merchant015.com', 'Shop 12, Sector 18 Market', 'Noida', 'Uttar Pradesh', '2026-11-09T08:53:22.782391+00:00'),
  ('BIZ_6DE2CDC8', 'Sharma Supermarket', 'Grocery', '07AAAAA1111A1Z1', '+919876500999', 'owner999@testbiz.com', 'Shop 4, Raj Nagar', 'Ghaziabad', 'Uttar Pradesh', '2026-11-09T08:59:14.005586+00:00'),
  ('BIZ_7DC5D141', 'Agrawal Sweets', 'Confectionery', NULL, '+919811991122', 'agrawal@sweets.com', NULL, 'Mathura', 'Uttar Pradesh', '2026-11-09T09:02:30.184284+00:00'),
  ('BIZ_F6C63F02', 'Gupta Medical', 'Pharmacy', NULL, '+919811993344', 'gupta@med.com', NULL, 'Kanpur', 'Uttar Pradesh', '2026-11-09T09:02:30.350176+00:00'),
  ('BIZ_B8CE6D76', 'Sharma Supermarket', 'Grocery', '07AAAAA1111A1Z1', '+919876500999', 'owner_ff9686@testbiz.com', 'Shop 4, Raj Nagar', 'Ghaziabad', 'Uttar Pradesh', '2026-11-09T09:03:50.164872+00:00'),
  ('BIZ_DA961447', 'Sharma Supermarket', 'Grocery', '07AAAAA1111A1Z1', '+919876500999', 'owner_e526af@testbiz.com', 'Shop 4, Raj Nagar', 'Ghaziabad', 'Uttar Pradesh', '2026-11-09T09:11:41.242408+00:00'),
  ('BIZ_FB2E3DC1', 'Sharma Supermarket', 'Grocery', '07AAAAA1111A1Z1', '+919876500999', 'owner_7a1a5d@testbiz.com', 'Shop 4, Raj Nagar', 'Ghaziabad', 'Uttar Pradesh', '2026-11-09T09:44:34.414057+00:00'),
  ('BIZ_F298D49F', 'Sharma Supermarket', 'Grocery', '07AAAAA1111A1Z1', '+919876500999', 'owner_892461@testbiz.com', 'Shop 4, Raj Nagar', 'Ghaziabad', 'Uttar Pradesh', '2026-11-09T09:45:01.402992+00:00'),
  ('BIZ_98DF1195', 'Sharma Supermarket', 'Grocery', '07AAAAA1111A1Z1', '+919876500999', 'owner_ba3f3a@testbiz.com', 'Shop 4, Raj Nagar', 'Ghaziabad', 'Uttar Pradesh', '2026-11-09T09:45:26.682925+00:00'),
  ('BIZ_AC553922', 'Sharma Supermarket', 'Grocery', '07AAAAA1111A1Z1', '+919876500999', 'owner_7b9836@testbiz.com', 'Shop 4, Raj Nagar', 'Ghaziabad', 'Uttar Pradesh', '2026-11-09T09:46:20.015284+00:00'),
  ('BIZ_4B77C3E4', 'Sharma Supermarket', 'Grocery', '07AAAAA1111A1Z1', '+919876500999', 'owner_f82434@testbiz.com', 'Shop 4, Raj Nagar', 'Ghaziabad', 'Uttar Pradesh', '2026-11-09T09:46:45.512376+00:00'),
  ('BIZ_4BD84C2E', 'Sharma Supermarket', 'Grocery', '07AAAAA1111A1Z1', '+919876500999', 'owner_e216d9@testbiz.com', 'Shop 4, Raj Nagar', 'Ghaziabad', 'Uttar Pradesh', '2026-11-09T09:47:11.193433+00:00'),
  ('BIZ_9DDC2726', 'Sharma Supermarket', 'Grocery', '07AAAAA1111A1Z1', '+919876500999', 'owner_5487d0@testbiz.com', 'Shop 4, Raj Nagar', 'Ghaziabad', 'Uttar Pradesh', '2026-11-09T09:48:04.638196+00:00'),
  ('BIZ_519A659A', 'Sharma Supermarket', 'Grocery', '07AAAAA1111A1Z1', '+919876500999', 'owner_800772@testbiz.com', 'Shop 4, Raj Nagar', 'Ghaziabad', 'Uttar Pradesh', '2026-11-09T11:30:17.797028+00:00')
ON CONFLICT DO NOTHING;

INSERT INTO public."branches" ("id", "business_id", "name", "code", "city", "state", "address", "phone", "is_main", "created_at")
VALUES
  ('BR_M015_MAIN', 'M015', 'Main Branch - Sector 18', 'SEC18', 'Noida', 'Uttar Pradesh', 'Shop 12, Sector 18 Market', '+919876543210', 1, '2026-11-09T08:53:22.782391+00:00'),
  ('BR_M015_SEC62', 'M015', 'Sector 62 Outlet', 'SEC62', 'Noida', 'Uttar Pradesh', 'Plot 45, Sector 62', '+919876543211', 0, '2026-11-09T08:53:22.782391+00:00'),
  ('BR_BIZ_6DE2CDC8_MAIN', 'BIZ_6DE2CDC8', 'Sharma Supermarket - Main Branch', 'MAIN', 'Ghaziabad', 'Uttar Pradesh', 'Shop 4, Raj Nagar', '+919876500999', 1, '2026-11-09T08:59:14.005586+00:00'),
  ('BR_BIZ_7DC5D141_MAIN', 'BIZ_7DC5D141', 'Agrawal Sweets - Main Branch', 'MAIN', 'Mathura', 'Uttar Pradesh', NULL, '+919811991122', 1, '2026-11-09T09:02:30.184284+00:00'),
  ('BR_BIZ_F6C63F02_MAIN', 'BIZ_F6C63F02', 'Gupta Medical - Main Branch', 'MAIN', 'Kanpur', 'Uttar Pradesh', NULL, '+919811993344', 1, '2026-11-09T09:02:30.350176+00:00'),
  ('BR_BIZ_B8CE6D76_MAIN', 'BIZ_B8CE6D76', 'Sharma Supermarket - Main Branch', 'MAIN', 'Ghaziabad', 'Uttar Pradesh', 'Shop 4, Raj Nagar', '+919876500999', 1, '2026-11-09T09:03:50.164872+00:00'),
  ('BR_BIZ_DA961447_MAIN', 'BIZ_DA961447', 'Sharma Supermarket - Main Branch', 'MAIN', 'Ghaziabad', 'Uttar Pradesh', 'Shop 4, Raj Nagar', '+919876500999', 1, '2026-11-09T09:11:41.242408+00:00'),
  ('BR_BIZ_FB2E3DC1_MAIN', 'BIZ_FB2E3DC1', 'Sharma Supermarket - Main Branch', 'MAIN', 'Ghaziabad', 'Uttar Pradesh', 'Shop 4, Raj Nagar', '+919876500999', 1, '2026-11-09T09:44:34.414057+00:00'),
  ('BR_BIZ_F298D49F_MAIN', 'BIZ_F298D49F', 'Sharma Supermarket - Main Branch', 'MAIN', 'Ghaziabad', 'Uttar Pradesh', 'Shop 4, Raj Nagar', '+919876500999', 1, '2026-11-09T09:45:01.402992+00:00'),
  ('BR_BIZ_98DF1195_MAIN', 'BIZ_98DF1195', 'Sharma Supermarket - Main Branch', 'MAIN', 'Ghaziabad', 'Uttar Pradesh', 'Shop 4, Raj Nagar', '+919876500999', 1, '2026-11-09T09:45:26.682925+00:00'),
  ('BR_BIZ_AC553922_MAIN', 'BIZ_AC553922', 'Sharma Supermarket - Main Branch', 'MAIN', 'Ghaziabad', 'Uttar Pradesh', 'Shop 4, Raj Nagar', '+919876500999', 1, '2026-11-09T09:46:20.015284+00:00'),
  ('BR_BIZ_4B77C3E4_MAIN', 'BIZ_4B77C3E4', 'Sharma Supermarket - Main Branch', 'MAIN', 'Ghaziabad', 'Uttar Pradesh', 'Shop 4, Raj Nagar', '+919876500999', 1, '2026-11-09T09:46:45.512376+00:00'),
  ('BR_BIZ_4BD84C2E_MAIN', 'BIZ_4BD84C2E', 'Sharma Supermarket - Main Branch', 'MAIN', 'Ghaziabad', 'Uttar Pradesh', 'Shop 4, Raj Nagar', '+919876500999', 1, '2026-11-09T09:47:11.193433+00:00'),
  ('BR_BIZ_9DDC2726_MAIN', 'BIZ_9DDC2726', 'Sharma Supermarket - Main Branch', 'MAIN', 'Ghaziabad', 'Uttar Pradesh', 'Shop 4, Raj Nagar', '+919876500999', 1, '2026-11-09T09:48:04.638196+00:00'),
  ('BR_BIZ_519A659A_MAIN', 'BIZ_519A659A', 'Sharma Supermarket - Main Branch', 'MAIN', 'Ghaziabad', 'Uttar Pradesh', 'Shop 4, Raj Nagar', '+919876500999', 1, '2026-11-09T11:30:17.797028+00:00')
ON CONFLICT DO NOTHING;

INSERT INTO public."users" ("id", "business_id", "branch_id", "username", "email", "full_name", "password_hash", "role", "phone", "is_active", "created_at")
VALUES
  ('USR_OWNER_01', 'M015', 'BR_M015_MAIN', 'owner_m015', 'owner@vyaparmitra.com', 'Atul Kumar (Owner)', 'pbkdf2:sha256:100000$c4e7c587eec0f9dbfb64be593ecf4ea9$a707a6e3a37c5d1618a69054477ed87f6726ae4b29df6db873f3bef5afc415b9', 'owner', '+919876543210', 1, '2026-11-09T08:53:22.782391+00:00'),
  ('USR_MGR_01', 'M015', 'BR_M015_MAIN', 'manager_m015', 'manager@vyaparmitra.com', 'Vikram Singh (Manager)', 'pbkdf2:sha256:100000$b8c5d8d71323fa3db7692ea0c2ceeefe$b98d3f34f9da846cfea5e69ac4428af53976eec7d287b1214e96555fd0500d49', 'manager', '+919876543212', 1, '2026-11-09T08:53:22.782391+00:00'),
  ('USR_STAFF_01', 'M015', 'BR_M015_MAIN', 'staff_m015', 'staff@vyaparmitra.com', 'Rohan Sharma (POS Staff)', 'pbkdf2:sha256:100000$505a4dcffb67edcca7101b7cbe9143cf$4ac3d53453cf9054119e9e98ac0f48fd0aeb0985c5dfda1ecc8c682de7a905fc', 'staff', '+919876543213', 1, '2026-11-09T08:53:22.782391+00:00'),
  ('USR_983F6BC9', 'BIZ_6DE2CDC8', 'BR_BIZ_6DE2CDC8_MAIN', 'test_owner_999', 'owner999@testbiz.com', 'Ramesh Sharma', 'pbkdf2:sha256:100000$4bc59706183d366509c55f49cf72b765$65b1e89907fd777e1a4c9d47575ee2b810e097bc991c6cd6cb6f876e7d2910c7', 'owner', '+919876500999', 1, '2026-11-09T08:59:14.005586+00:00'),
  ('USR_BFFA979B', 'M015', 'BR_M015_MAIN', 'sub_mgr_01', 'sub_mgr_01@vyaparmitra.com', 'Sub Manager One', 'pbkdf2:sha256:100000$53a189831313629a1d378f462dcd79f6$ceb021b2e366e30caa63d541270fbc2b8978d98eca7ec038c79d624c5cd9eef3', 'manager', NULL, 1, '2026-11-09T08:59:14.224811+00:00'),
  ('USR_BEEA18F2', 'BIZ_7DC5D141', 'BR_BIZ_7DC5D141_MAIN', 'owner_agrawal', 'agrawal@sweets.com', 'Gopal Agrawal', 'pbkdf2:sha256:100000$b028ed900c2693099180cc447dd5e481$d3632238836e6851d555122eebffa7086e8cb45e19a944ba125f0015532f8e24', 'owner', '+919811991122', 1, '2026-11-09T09:02:30.184284+00:00'),
  ('USR_9C55CB73', 'BIZ_F6C63F02', 'BR_BIZ_F6C63F02_MAIN', 'owner_gupta', 'gupta@med.com', 'Sanjay Gupta', 'pbkdf2:sha256:100000$8ccd4f5680d200b418e41c5c0d17e2d3$09cf34be73fa4382266ba5c3a51c5821aae53ee25c2eb30c3cc5f33887dabb5c', 'owner', '+919811993344', 1, '2026-11-09T09:02:30.350176+00:00'),
  ('USR_1962FCA7', 'BIZ_B8CE6D76', 'BR_BIZ_B8CE6D76_MAIN', 'owner_ff9686', 'owner_ff9686@testbiz.com', 'Ramesh Sharma', 'pbkdf2:sha256:100000$1fbad2b2540d381dd0f1874496abd4ee$3084d23b0a14b42812e1528cb5aeecc824490e9702d06b4abadbd3f24183a6b3', 'owner', '+919876500999', 1, '2026-11-09T09:03:50.164872+00:00'),
  ('USR_01B82C21', 'M015', 'BR_M015_MAIN', 'mgr_2c217b', 'mgr_2c217b@vyaparmitra.com', 'Sub Manager One', 'pbkdf2:sha256:100000$deaf44ef76caea51b1edb2bdd2adaecd$6ccc6a878803fa2f4755aeeea29759f7574117d76328976b57f885c460ff61c5', 'manager', NULL, 1, '2026-11-09T09:03:50.329358+00:00'),
  ('USR_31C31F55', 'BIZ_DA961447', 'BR_BIZ_DA961447_MAIN', 'owner_e526af', 'owner_e526af@testbiz.com', 'Ramesh Sharma', 'pbkdf2:sha256:100000$958add8b21b7ad8b6d3687673b64d485$edafe5ef9292a74692653bf38b7080aa3d2e43ee16b1659cbc977fc9c8392482', 'owner', '+919876500999', 1, '2026-11-09T09:11:41.242408+00:00'),
  ('USR_CE7B94F9', 'M015', 'BR_M015_MAIN', 'mgr_7be3e2', 'mgr_7be3e2@vyaparmitra.com', 'Sub Manager One', 'pbkdf2:sha256:100000$c61c09d89a150bb26ef1b14412a248f9$13dab7f233393aa1fdec10977f257edfd59c3234bf8d851db479c973bb1f257d', 'manager', NULL, 1, '2026-11-09T09:11:41.625949+00:00'),
  ('USR_0328A3EF', 'BIZ_FB2E3DC1', 'BR_BIZ_FB2E3DC1_MAIN', 'owner_7a1a5d', 'owner_7a1a5d@testbiz.com', 'Ramesh Sharma', 'pbkdf2:sha256:100000$c37920f1541fb0b69da48ba9be9c0af9$b1b04b7a1f3b83a2379feee05b7543c13e18080cf405208c8a24580406fe8a42', 'owner', '+919876500999', 1, '2026-11-09T09:44:34.414057+00:00'),
  ('USR_3E457470', 'M015', 'BR_M015_MAIN', 'mgr_071fa6', 'mgr_071fa6@vyaparmitra.com', 'Sub Manager One', 'pbkdf2:sha256:100000$9a8919143a09d5255d20c067fbb076a2$20dc8e75252ee7c9374591b29baa7bb421e63bebac8ab247ee4f7e3e29200040', 'manager', NULL, 1, '2026-11-09T09:44:34.655742+00:00'),
  ('USR_20BD4883', 'BIZ_F298D49F', 'BR_BIZ_F298D49F_MAIN', 'owner_892461', 'owner_892461@testbiz.com', 'Ramesh Sharma', 'pbkdf2:sha256:100000$047f5d498b5817fdd108681d50fa6023$9f06b21d68d2bc48331fc73038f589943bd5ae801f0f81b7bb45731d93be0f1f', 'owner', '+919876500999', 1, '2026-11-09T09:45:01.402992+00:00'),
  ('USR_8DC13CA3', 'M015', 'BR_M015_MAIN', 'mgr_5191ac', 'mgr_5191ac@vyaparmitra.com', 'Sub Manager One', 'pbkdf2:sha256:100000$d95fd1a22d69ea82845e7891130fa743$98699706c1c212b8b0ce5ec3732ad9671d799f3420cda0083ab546b097c47502', 'manager', NULL, 1, '2026-11-09T09:45:01.630060+00:00'),
  ('USR_76F2D2CC', 'BIZ_98DF1195', 'BR_BIZ_98DF1195_MAIN', 'owner_ba3f3a', 'owner_ba3f3a@testbiz.com', 'Ramesh Sharma', 'pbkdf2:sha256:100000$69e93effd728327cc07488d781dac4fc$ab6960d0e4c939b47778e2236ad54462ef08053b43db3918c1c278ac6cce32d7', 'owner', '+919876500999', 1, '2026-11-09T09:45:26.682925+00:00'),
  ('USR_8D7C1C2A', 'M015', 'BR_M015_MAIN', 'mgr_342cc0', 'mgr_342cc0@vyaparmitra.com', 'Sub Manager One', 'pbkdf2:sha256:100000$0790bcfa2ff17093f3eb7993aa942823$7cf2ced7e31b2be3215fd18f4ca978306799e99c4beb42fe8903cc362f3b12ed', 'manager', NULL, 1, '2026-11-09T09:45:26.912158+00:00'),
  ('USR_9DC7CE5D', 'BIZ_AC553922', 'BR_BIZ_AC553922_MAIN', 'owner_7b9836', 'owner_7b9836@testbiz.com', 'Ramesh Sharma', 'pbkdf2:sha256:100000$98705a51ec0459e658df1b0da463ea2f$80376867f812d73d24eaac0d392e557f7797013956cf7fc0484ec511dec5ede8', 'owner', '+919876500999', 1, '2026-11-09T09:46:20.015284+00:00'),
  ('USR_6A860320', 'M015', 'BR_M015_MAIN', 'mgr_1c382a', 'mgr_1c382a@vyaparmitra.com', 'Sub Manager One', 'pbkdf2:sha256:100000$d6aa2427369ffa98d77dba0907bbaff7$8f1cf0b0e64c20a38d0c85f13543b385fefc5dc20e7a71dea310979dc72f562c', 'manager', NULL, 1, '2026-11-09T09:46:20.242721+00:00'),
  ('USR_507ABD93', 'BIZ_4B77C3E4', 'BR_BIZ_4B77C3E4_MAIN', 'owner_f82434', 'owner_f82434@testbiz.com', 'Ramesh Sharma', 'pbkdf2:sha256:100000$011326301f80b1c3e7a860de82f323f1$7890f9532a8354fbf041728c4f8cd25236832ba4e019951e18617541279f6460', 'owner', '+919876500999', 1, '2026-11-09T09:46:45.512376+00:00'),
  ('USR_537F6809', 'M015', 'BR_M015_MAIN', 'mgr_af502a', 'mgr_af502a@vyaparmitra.com', 'Sub Manager One', 'pbkdf2:sha256:100000$9b0790b2bd65db5aa6b5bb2092d3da28$abd68076fcc523e6eb594bb45229ab5303cf4f3639b32a0cb354cfd4f394b865', 'manager', NULL, 1, '2026-11-09T09:46:45.747160+00:00'),
  ('USR_A3FCE092', 'BIZ_4BD84C2E', 'BR_BIZ_4BD84C2E_MAIN', 'owner_e216d9', 'owner_e216d9@testbiz.com', 'Ramesh Sharma', 'pbkdf2:sha256:100000$bc35d04e1301930d04d2491212ce97b9$60cedea1559cc8b93a6fa58faf80e4515511a242e737bfe65fedfae0256004cd', 'owner', '+919876500999', 1, '2026-11-09T09:47:11.193433+00:00'),
  ('USR_BA671F93', 'M015', 'BR_M015_MAIN', 'mgr_5588e8', 'mgr_5588e8@vyaparmitra.com', 'Sub Manager One', 'pbkdf2:sha256:100000$ced5762181696a14dd43d314b4f4ae1a$c3a788cbab95c6c2e114b44dbb05ef61df9d7f162beaf5d535c5fa3bedbd9cf7', 'manager', NULL, 1, '2026-11-09T09:47:11.421031+00:00'),
  ('USR_7E9DDC68', 'BIZ_9DDC2726', 'BR_BIZ_9DDC2726_MAIN', 'owner_5487d0', 'owner_5487d0@testbiz.com', 'Ramesh Sharma', 'pbkdf2:sha256:100000$d1b65ab867dbc62e8132144d9c325595$9b780ffc6edf241d681ed0f4fb607451981269ad549fc4344534b614a76fed4e', 'owner', '+919876500999', 1, '2026-11-09T09:48:04.638196+00:00'),
  ('USR_B5C440F7', 'M015', 'BR_M015_MAIN', 'mgr_c2b1f6', 'mgr_c2b1f6@vyaparmitra.com', 'Sub Manager One', 'pbkdf2:sha256:100000$b687c8a72876d2f4d4b9264af524339f$e4f30c0cd7d2ea6ad8f23eb3dd9dc708daa4474bbdc87fe869f457913bdfae77', 'manager', NULL, 1, '2026-11-09T09:48:04.874037+00:00'),
  ('USR_CF87485F', 'BIZ_519A659A', 'BR_BIZ_519A659A_MAIN', 'owner_800772', 'owner_800772@testbiz.com', 'Ramesh Sharma', 'pbkdf2:sha256:100000$eb8cd5669f09797095dde5625acc890f$6212374a2511c5f1d10df35509e7129f620fb3eaf380f3bb8a4d68dce2abca09', 'owner', '+919876500999', 1, '2026-11-09T11:30:17.797028+00:00'),
  ('USR_2D6CA869', 'M015', 'BR_M015_MAIN', 'mgr_13b554', 'mgr_13b554@vyaparmitra.com', 'Sub Manager One', 'pbkdf2:sha256:100000$d6a1aa38e3270401567e3761fb6fe0f2$6ba3199438d296aec69f035dffc53d43942c8544921f3ba515984e63f52bba02', 'manager', NULL, 1, '2026-11-09T11:30:18.766475+00:00')
ON CONFLICT DO NOTHING;

INSERT INTO public."inventory" ("id", "business_id", "branch_id", "product_id", "product_name", "category", "current_stock", "min_stock_threshold", "unit_cost", "selling_price", "barcode", "unit", "updated_at")
VALUES
  ('INV_BR_M015_MAIN_PRD_ACC_01', 'M015', 'BR_M015_MAIN', 'PRD_ACC_01', 'Leather Wallet', 'Accessories', 75, 15, 250.0, 499.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_ACC_01', 'M015', 'BR_M015_SEC62', 'PRD_ACC_01', 'Leather Wallet', 'Accessories', 75, 15, 250.0, 499.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_ACC_02', 'M015', 'BR_M015_MAIN', 'PRD_ACC_02', 'Fashion Sunglasses', 'Accessories', 92, 15, 320.0, 699.0, NULL, 'pcs', '2026-11-09T09:48:07.717085+00:00'),
  ('INV_BR_M015_SEC62_PRD_ACC_02', 'M015', 'BR_M015_SEC62', 'PRD_ACC_02', 'Fashion Sunglasses', 'Accessories', 75, 15, 320.0, 699.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_ART_01', 'M015', 'BR_M015_MAIN', 'PRD_ART_01', 'Acrylic Color Set 12-Pack', 'Art Supplies', 91, 15, 180.0, 320.0, NULL, 'pcs', '2026-11-09T09:00:40.048090+00:00'),
  ('INV_BR_M015_SEC62_PRD_ART_01', 'M015', 'BR_M015_SEC62', 'PRD_ART_01', 'Acrylic Color Set 12-Pack', 'Art Supplies', 75, 15, 180.0, 320.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_ART_02', 'M015', 'BR_M015_MAIN', 'PRD_ART_02', 'Sketching Canvas Board 10x12', 'Art Supplies', 75, 15, 95.0, 175.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_ART_02', 'M015', 'BR_M015_SEC62', 'PRD_ART_02', 'Sketching Canvas Board 10x12', 'Art Supplies', 75, 15, 95.0, 175.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_BABY_01', 'M015', 'BR_M015_MAIN', 'PRD_BABY_01', 'Baby Diaper Mega Pack (M)', 'Baby Care', 100, 15, 550.0, 799.0, NULL, 'pcs', '2026-11-09T09:11:43.821187+00:00'),
  ('INV_BR_M015_SEC62_PRD_BABY_01', 'M015', 'BR_M015_SEC62', 'PRD_BABY_01', 'Baby Diaper Mega Pack (M)', 'Baby Care', 75, 15, 550.0, 799.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_BABY_02', 'M015', 'BR_M015_MAIN', 'PRD_BABY_02', 'Gentle Baby Wet Wipes 72s', 'Baby Care', 75, 15, 90.0, 160.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_BABY_02', 'M015', 'BR_M015_SEC62', 'PRD_BABY_02', 'Gentle Baby Wet Wipes 72s', 'Baby Care', 75, 15, 90.0, 160.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_BEV_01', 'M015', 'BR_M015_MAIN', 'PRD_BEV_01', 'Fresh Mango Juice 1L', 'Beverages', 75, 15, 65.0, 110.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_BEV_01', 'M015', 'BR_M015_SEC62', 'PRD_BEV_01', 'Fresh Mango Juice 1L', 'Beverages', 75, 15, 65.0, 110.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_BEV_02', 'M015', 'BR_M015_MAIN', 'PRD_BEV_02', 'Cold Pressed Orange Juice 500ml', 'Beverages', 92, 15, 55.0, 95.0, NULL, 'pcs', '2026-11-09T09:45:29.665655+00:00'),
  ('INV_BR_M015_SEC62_PRD_BEV_02', 'M015', 'BR_M015_SEC62', 'PRD_BEV_02', 'Cold Pressed Orange Juice 500ml', 'Beverages', 75, 15, 55.0, 95.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_BRD_01', 'M015', 'BR_M015_MAIN', 'PRD_BRD_01', 'Brown Whole Wheat Bread 400g', 'Bread', 92, 15, 28.0, 50.0, NULL, 'pcs', '2026-11-09T09:44:38.196100+00:00'),
  ('INV_BR_M015_SEC62_PRD_BRD_01', 'M015', 'BR_M015_SEC62', 'PRD_BRD_01', 'Brown Whole Wheat Bread 400g', 'Bread', 75, 15, 28.0, 50.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_BRD_02', 'M015', 'BR_M015_MAIN', 'PRD_BRD_02', 'Artisanal Sourdough Bread Loaf', 'Bread', 100, 15, 75.0, 140.0, NULL, 'pcs', '2026-11-09T09:03:50.799850+00:00'),
  ('INV_BR_M015_SEC62_PRD_BRD_02', 'M015', 'BR_M015_SEC62', 'PRD_BRD_02', 'Artisanal Sourdough Bread Loaf', 'Bread', 75, 15, 75.0, 140.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_CAB_01', 'M015', 'BR_M015_MAIN', 'PRD_CAB_01', 'Braided USB-C to USB-C Cable 1.5m', 'Cables', 99, 15, 120.0, 299.0, NULL, 'pcs', '2026-11-09T09:44:37.073287+00:00'),
  ('INV_BR_M015_SEC62_PRD_CAB_01', 'M015', 'BR_M015_SEC62', 'PRD_CAB_01', 'Braided USB-C to USB-C Cable 1.5m', 'Cables', 75, 15, 120.0, 299.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_CAB_02', 'M015', 'BR_M015_MAIN', 'PRD_CAB_02', 'Lightning Charging Cable 1m', 'Cables', 75, 15, 140.0, 349.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_CAB_02', 'M015', 'BR_M015_SEC62', 'PRD_CAB_02', 'Lightning Charging Cable 1m', 'Cables', 75, 15, 140.0, 349.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_CAK_01', 'M015', 'BR_M015_MAIN', 'PRD_CAK_01', 'Dutch Chocolate Truffle Cake 500g', 'Cakes', 92, 15, 280.0, 550.0, NULL, 'pcs', '2026-11-09T09:46:23.010731+00:00'),
  ('INV_BR_M015_SEC62_PRD_CAK_01', 'M015', 'BR_M015_SEC62', 'PRD_CAK_01', 'Dutch Chocolate Truffle Cake 500g', 'Cakes', 75, 15, 280.0, 550.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_CAK_02', 'M015', 'BR_M015_MAIN', 'PRD_CAK_02', 'Eggless Pineapple Cake 500g', 'Cakes', 99, 15, 220.0, 450.0, NULL, 'pcs', '2026-11-09T09:46:47.817863+00:00'),
  ('INV_BR_M015_SEC62_PRD_CAK_02', 'M015', 'BR_M015_SEC62', 'PRD_CAK_02', 'Eggless Pineapple Cake 500g', 'Cakes', 75, 15, 220.0, 450.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_CAS_01', 'M015', 'BR_M015_MAIN', 'PRD_CAS_01', 'Shockproof Matte Phone Case', 'Cases', 75, 15, 90.0, 249.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_CAS_01', 'M015', 'BR_M015_SEC62', 'PRD_CAS_01', 'Shockproof Matte Phone Case', 'Cases', 75, 15, 90.0, 249.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_CAS_02', 'M015', 'BR_M015_MAIN', 'PRD_CAS_02', 'Premium Leather Back Case', 'Cases', 75, 15, 180.0, 450.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_CAS_02', 'M015', 'BR_M015_SEC62', 'PRD_CAS_02', 'Premium Leather Back Case', 'Cases', 75, 15, 180.0, 450.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_CHG_01', 'M015', 'BR_M015_MAIN', 'PRD_CHG_01', 'Fast Charger 33W USB-C Adapter', 'Chargers', 75, 15, 320.0, 699.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_CHG_01', 'M015', 'BR_M015_SEC62', 'PRD_CHG_01', 'Fast Charger 33W USB-C Adapter', 'Chargers', 75, 15, 320.0, 699.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_CHG_02', 'M015', 'BR_M015_MAIN', 'PRD_CHG_02', 'Wireless Charging Pad 15W', 'Chargers', 75, 15, 450.0, 999.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_CHG_02', 'M015', 'BR_M015_SEC62', 'PRD_CHG_02', 'Wireless Charging Pad 15W', 'Chargers', 75, 15, 450.0, 999.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_COF_01', 'M015', 'BR_M015_MAIN', 'PRD_COF_01', 'Arabica Roast Ground Coffee 250g', 'Coffee', 100, 15, 210.0, 380.0, NULL, 'pcs', '2026-11-09T09:03:00.334541+00:00'),
  ('INV_BR_M015_SEC62_PRD_COF_01', 'M015', 'BR_M015_SEC62', 'PRD_COF_01', 'Arabica Roast Ground Coffee 250g', 'Coffee', 75, 15, 210.0, 380.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_COF_02', 'M015', 'BR_M015_MAIN', 'PRD_COF_02', 'Instant Cold Brew Premix 200g', 'Coffee', 75, 15, 150.0, 280.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_COF_02', 'M015', 'BR_M015_SEC62', 'PRD_COF_02', 'Instant Cold Brew Premix 200g', 'Coffee', 75, 15, 150.0, 280.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_ESS_01', 'M015', 'BR_M015_MAIN', 'PRD_ESS_01', 'Organic Hand Wash 500ml', 'Daily Essentials', 75, 15, 75.0, 145.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_ESS_01', 'M015', 'BR_M015_SEC62', 'PRD_ESS_01', 'Organic Hand Wash 500ml', 'Daily Essentials', 75, 15, 75.0, 145.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_ESS_02', 'M015', 'BR_M015_MAIN', 'PRD_ESS_02', 'Antibacterial Floor Cleaner 1L', 'Daily Essentials', 95, 15, 85.0, 160.0, NULL, 'pcs', '2026-11-09T09:02:00.872488+00:00'),
  ('INV_BR_M015_SEC62_PRD_ESS_02', 'M015', 'BR_M015_SEC62', 'PRD_ESS_02', 'Antibacterial Floor Cleaner 1L', 'Daily Essentials', 75, 15, 85.0, 160.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_DAI_01', 'M015', 'BR_M015_MAIN', 'PRD_DAI_01', 'Fresh Cow Milk Pouch 1L', 'Dairy', 75, 15, 48.0, 66.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_DAI_01', 'M015', 'BR_M015_SEC62', 'PRD_DAI_01', 'Fresh Cow Milk Pouch 1L', 'Dairy', 75, 15, 48.0, 66.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_DAI_02', 'M015', 'BR_M015_MAIN', 'PRD_DAI_02', 'Fresh Malai Paneer 200g', 'Dairy', 75, 15, 65.0, 95.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_DAI_02', 'M015', 'BR_M015_SEC62', 'PRD_DAI_02', 'Fresh Malai Paneer 200g', 'Dairy', 75, 15, 65.0, 95.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_DES_01', 'M015', 'BR_M015_MAIN', 'PRD_DES_01', 'Gulab Jamun Box 500g', 'Desserts', 75, 15, 120.0, 220.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_DES_01', 'M015', 'BR_M015_SEC62', 'PRD_DES_01', 'Gulab Jamun Box 500g', 'Desserts', 75, 15, 120.0, 220.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_DES_02', 'M015', 'BR_M015_MAIN', 'PRD_DES_02', 'Belgian Waffle with Syrup', 'Desserts', 91, 15, 90.0, 180.0, NULL, 'pcs', '2026-11-09T09:11:47.447152+00:00'),
  ('INV_BR_M015_SEC62_PRD_DES_02', 'M015', 'BR_M015_SEC62', 'PRD_DES_02', 'Belgian Waffle with Syrup', 'Desserts', 75, 15, 90.0, 180.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_EAR_01', 'M015', 'BR_M015_MAIN', 'PRD_EAR_01', 'TWS True Wireless Earbuds', 'Earphones', 75, 15, 650.0, 1299.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_EAR_01', 'M015', 'BR_M015_SEC62', 'PRD_EAR_01', 'TWS True Wireless Earbuds', 'Earphones', 75, 15, 650.0, 1299.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_EAR_02', 'M015', 'BR_M015_MAIN', 'PRD_EAR_02', 'Deep Bass Wired Earphones 3.5mm', 'Earphones', 99, 15, 140.0, 349.0, NULL, 'pcs', '2026-11-09T09:46:22.283768+00:00'),
  ('INV_BR_M015_SEC62_PRD_EAR_02', 'M015', 'BR_M015_SEC62', 'PRD_EAR_02', 'Deep Bass Wired Earphones 3.5mm', 'Earphones', 75, 15, 140.0, 349.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_ELE_01', 'M015', 'BR_M015_MAIN', 'PRD_ELE_01', 'Smart LED Desk Lamp 10W', 'Home Electronics', 75, 15, 450.0, 899.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_ELE_01', 'M015', 'BR_M015_SEC62', 'PRD_ELE_01', 'Smart LED Desk Lamp 10W', 'Home Electronics', 75, 15, 450.0, 899.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_ELE_02', 'M015', 'BR_M015_MAIN', 'PRD_ELE_02', 'Electric Kettle 1.5L Stainless Steel', 'Home Electronics', 92, 15, 550.0, 1099.0, NULL, 'pcs', '2026-11-09T09:46:48.549095+00:00'),
  ('INV_BR_M015_SEC62_PRD_ELE_02', 'M015', 'BR_M015_SEC62', 'PRD_ELE_02', 'Electric Kettle 1.5L Stainless Steel', 'Home Electronics', 75, 15, 550.0, 1099.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_HOU_01', 'M015', 'BR_M015_MAIN', 'PRD_HOU_01', 'Microfiber Cleaning Cloth 4-Pack', 'Household', 75, 15, 80.0, 180.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_HOU_01', 'M015', 'BR_M015_SEC62', 'PRD_HOU_01', 'Microfiber Cleaning Cloth 4-Pack', 'Household', 75, 15, 80.0, 180.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_HOU_02', 'M015', 'BR_M015_MAIN', 'PRD_HOU_02', 'Aromatherapy Reed Diffuser 100ml', 'Household', 91, 15, 160.0, 320.0, NULL, 'pcs', '2026-11-09T09:03:01.869916+00:00'),
  ('INV_BR_M015_SEC62_PRD_HOU_02', 'M015', 'BR_M015_SEC62', 'PRD_HOU_02', 'Aromatherapy Reed Diffuser 100ml', 'Household', 75, 15, 160.0, 320.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_KID_01', 'M015', 'BR_M015_MAIN', 'PRD_KID_01', 'Kids Cotton Graphic T-Shirt', 'Kids', 75, 15, 160.0, 349.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_KID_01', 'M015', 'BR_M015_SEC62', 'PRD_KID_01', 'Kids Cotton Graphic T-Shirt', 'Kids', 75, 15, 160.0, 349.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_KID_02', 'M015', 'BR_M015_MAIN', 'PRD_KID_02', 'Children Educational Puzzle Game', 'Kids', 92, 15, 130.0, 275.0, NULL, 'pcs', '2026-11-09T09:45:04.758736+00:00'),
  ('INV_BR_M015_SEC62_PRD_KID_02', 'M015', 'BR_M015_SEC62', 'PRD_KID_02', 'Children Educational Puzzle Game', 'Kids', 75, 15, 130.0, 275.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_LAP_01', 'M015', 'BR_M015_MAIN', 'PRD_LAP_01', 'Laptop Stand Aluminum Ergonomic', 'Laptops', 75, 15, 420.0, 899.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_LAP_01', 'M015', 'BR_M015_SEC62', 'PRD_LAP_01', 'Laptop Stand Aluminum Ergonomic', 'Laptops', 75, 15, 420.0, 899.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_LAP_02', 'M015', 'BR_M015_MAIN', 'PRD_LAP_02', 'Wireless Optical Mouse 2.4GHz', 'Laptops', 75, 15, 210.0, 499.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_LAP_02', 'M015', 'BR_M015_SEC62', 'PRD_LAP_02', 'Wireless Optical Mouse 2.4GHz', 'Laptops', 75, 15, 210.0, 499.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_MEA_01', 'M015', 'BR_M015_MAIN', 'PRD_MEA_01', 'Special North Indian Thali Combo', 'Meals', 75, 15, 110.0, 220.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_MEA_01', 'M015', 'BR_M015_SEC62', 'PRD_MEA_01', 'Special North Indian Thali Combo', 'Meals', 75, 15, 110.0, 220.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_MEA_02', 'M015', 'BR_M015_MAIN', 'PRD_MEA_02', 'Paneer Butter Masala Meal Box', 'Meals', 75, 15, 125.0, 250.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_MEA_02', 'M015', 'BR_M015_SEC62', 'PRD_MEA_02', 'Paneer Butter Masala Meal Box', 'Meals', 75, 15, 125.0, 250.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_MED_01', 'M015', 'BR_M015_MAIN', 'PRD_MED_01', 'Paracetamol 650mg Strip of 15', 'Medicine', 75, 15, 18.0, 35.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_MED_01', 'M015', 'BR_M015_SEC62', 'PRD_MED_01', 'Paracetamol 650mg Strip of 15', 'Medicine', 75, 15, 18.0, 35.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_MED_02', 'M015', 'BR_M015_MAIN', 'PRD_MED_02', 'Multivitamin & Minerals 30 Tablets', 'Medicine', 75, 15, 120.0, 240.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_MED_02', 'M015', 'BR_M015_SEC62', 'PRD_MED_02', 'Multivitamin & Minerals 30 Tablets', 'Medicine', 75, 15, 120.0, 240.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_MEN_01', 'M015', 'BR_M015_MAIN', 'PRD_MEN_01', 'Men Casual Slim-Fit Cotton Shirt', 'Men', 75, 15, 380.0, 799.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_MEN_01', 'M015', 'BR_M015_SEC62', 'PRD_MEN_01', 'Men Casual Slim-Fit Cotton Shirt', 'Men', 75, 15, 380.0, 799.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_MEN_02', 'M015', 'BR_M015_MAIN', 'PRD_MEN_02', 'Men Comfort Stretch Denim Jeans', 'Men', 75, 15, 550.0, 1199.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_MEN_02', 'M015', 'BR_M015_SEC62', 'PRD_MEN_02', 'Men Comfort Stretch Denim Jeans', 'Men', 75, 15, 550.0, 1199.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_MOB_01', 'M015', 'BR_M015_MAIN', 'PRD_MOB_01', 'Entry-level 4G Smartphone 32GB', 'Mobiles', 92, 15, 4800.0, 6499.0, NULL, 'pcs', '2026-11-09T09:47:14.197733+00:00'),
  ('INV_BR_M015_SEC62_PRD_MOB_01', 'M015', 'BR_M015_SEC62', 'PRD_MOB_01', 'Entry-level 4G Smartphone 32GB', 'Mobiles', 75, 15, 4800.0, 6499.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_MOB_02', 'M015', 'BR_M015_MAIN', 'PRD_MOB_02', 'Budget 5G Smartphone 128GB', 'Mobiles', 100, 15, 8800.0, 11999.0, NULL, 'pcs', '2026-11-09T09:45:03.612745+00:00'),
  ('INV_BR_M015_SEC62_PRD_MOB_02', 'M015', 'BR_M015_SEC62', 'PRD_MOB_02', 'Budget 5G Smartphone 128GB', 'Mobiles', 75, 15, 8800.0, 11999.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_NOT_01', 'M015', 'BR_M015_MAIN', 'PRD_NOT_01', 'Spiral Hardcover Journal 200 Pages', 'Notebooks', 75, 15, 85.0, 160.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_NOT_01', 'M015', 'BR_M015_SEC62', 'PRD_NOT_01', 'Spiral Hardcover Journal 200 Pages', 'Notebooks', 75, 15, 85.0, 160.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_NOT_02', 'M015', 'BR_M015_MAIN', 'PRD_NOT_02', 'Executive PU Leather Diary', 'Notebooks', 99, 15, 130.0, 260.0, NULL, 'pcs', '2026-11-09T09:48:06.976592+00:00'),
  ('INV_BR_M015_SEC62_PRD_NOT_02', 'M015', 'BR_M015_SEC62', 'PRD_NOT_02', 'Executive PU Leather Diary', 'Notebooks', 75, 15, 130.0, 260.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_OFF_01', 'M015', 'BR_M015_MAIN', 'PRD_OFF_01', 'Heavy Duty Desktop Stapler Set', 'Office Supplies', 75, 15, 90.0, 175.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_OFF_01', 'M015', 'BR_M015_SEC62', 'PRD_OFF_01', 'Heavy Duty Desktop Stapler Set', 'Office Supplies', 75, 15, 90.0, 175.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_OFF_02', 'M015', 'BR_M015_MAIN', 'PRD_OFF_02', 'A4 Copier Paper Ream 500 Sheets', 'Office Supplies', 100, 15, 190.0, 310.0, NULL, 'pcs', '2026-11-09T08:59:47.501024+00:00'),
  ('INV_BR_M015_SEC62_PRD_OFF_02', 'M015', 'BR_M015_SEC62', 'PRD_OFF_02', 'A4 Copier Paper Ream 500 Sheets', 'Office Supplies', 75, 15, 190.0, 310.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_PAS_01', 'M015', 'BR_M015_MAIN', 'PRD_PAS_01', 'Red Velvet Pastry Slice', 'Pastries', 75, 15, 45.0, 95.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_SEC62_PRD_PAS_01', 'M015', 'BR_M015_SEC62', 'PRD_PAS_01', 'Red Velvet Pastry Slice', 'Pastries', 75, 15, 45.0, 95.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00'),
  ('INV_BR_M015_MAIN_PRD_PAS_02', 'M015', 'BR_M015_MAIN', 'PRD_PAS_02', 'Choco Lava Lava Cake Single', 'Pastries', 99, 15, 50.0, 110.0, NULL, 'pcs', '2026-11-09T09:45:28.929258+00:00'),
  ('INV_BR_M015_SEC62_PRD_PAS_02', 'M015', 'BR_M015_SEC62', 'PRD_PAS_02', 'Choco Lava Lava Cake Single', 'Pastries', 75, 15, 50.0, 110.0, NULL, 'pcs', '2026-11-09T08:53:22.782391+00:00')
ON CONFLICT DO NOTHING;

INSERT INTO public."clean_products" ("product_id", "product_name", "product_category", "unit_cost", "selling_price")
VALUES
  ('PRD_ACC_01', 'Leather Wallet', 'Accessories', 250.0, 499.0),
  ('PRD_ACC_02', 'Fashion Sunglasses', 'Accessories', 320.0, 699.0),
  ('PRD_ART_01', 'Acrylic Color Set 12-Pack', 'Art Supplies', 180.0, 320.0),
  ('PRD_ART_02', 'Sketching Canvas Board 10x12', 'Art Supplies', 95.0, 175.0),
  ('PRD_BABY_01', 'Baby Diaper Mega Pack (M)', 'Baby Care', 550.0, 799.0),
  ('PRD_BABY_02', 'Gentle Baby Wet Wipes 72s', 'Baby Care', 90.0, 160.0),
  ('PRD_BEV_01', 'Fresh Mango Juice 1L', 'Beverages', 65.0, 110.0),
  ('PRD_BEV_02', 'Cold Pressed Orange Juice 500ml', 'Beverages', 55.0, 95.0),
  ('PRD_BRD_01', 'Brown Whole Wheat Bread 400g', 'Bread', 28.0, 50.0),
  ('PRD_BRD_02', 'Artisanal Sourdough Bread Loaf', 'Bread', 75.0, 140.0),
  ('PRD_CAB_01', 'Braided USB-C to USB-C Cable 1.5m', 'Cables', 120.0, 299.0),
  ('PRD_CAB_02', 'Lightning Charging Cable 1m', 'Cables', 140.0, 349.0),
  ('PRD_CAK_01', 'Dutch Chocolate Truffle Cake 500g', 'Cakes', 280.0, 550.0),
  ('PRD_CAK_02', 'Eggless Pineapple Cake 500g', 'Cakes', 220.0, 450.0),
  ('PRD_CAS_01', 'Shockproof Matte Phone Case', 'Cases', 90.0, 249.0),
  ('PRD_CAS_02', 'Premium Leather Back Case', 'Cases', 180.0, 450.0),
  ('PRD_CHG_01', 'Fast Charger 33W USB-C Adapter', 'Chargers', 320.0, 699.0),
  ('PRD_CHG_02', 'Wireless Charging Pad 15W', 'Chargers', 450.0, 999.0),
  ('PRD_COF_01', 'Arabica Roast Ground Coffee 250g', 'Coffee', 210.0, 380.0),
  ('PRD_COF_02', 'Instant Cold Brew Premix 200g', 'Coffee', 150.0, 280.0),
  ('PRD_ESS_01', 'Organic Hand Wash 500ml', 'Daily Essentials', 75.0, 145.0),
  ('PRD_ESS_02', 'Antibacterial Floor Cleaner 1L', 'Daily Essentials', 85.0, 160.0),
  ('PRD_DAI_01', 'Fresh Cow Milk Pouch 1L', 'Dairy', 48.0, 66.0),
  ('PRD_DAI_02', 'Fresh Malai Paneer 200g', 'Dairy', 65.0, 95.0),
  ('PRD_DES_01', 'Gulab Jamun Box 500g', 'Desserts', 120.0, 220.0),
  ('PRD_DES_02', 'Belgian Waffle with Syrup', 'Desserts', 90.0, 180.0),
  ('PRD_EAR_01', 'TWS True Wireless Earbuds', 'Earphones', 650.0, 1299.0),
  ('PRD_EAR_02', 'Deep Bass Wired Earphones 3.5mm', 'Earphones', 140.0, 349.0),
  ('PRD_ELE_01', 'Smart LED Desk Lamp 10W', 'Home Electronics', 450.0, 899.0),
  ('PRD_ELE_02', 'Electric Kettle 1.5L Stainless Steel', 'Home Electronics', 550.0, 1099.0),
  ('PRD_HOU_01', 'Microfiber Cleaning Cloth 4-Pack', 'Household', 80.0, 180.0),
  ('PRD_HOU_02', 'Aromatherapy Reed Diffuser 100ml', 'Household', 160.0, 320.0),
  ('PRD_KID_01', 'Kids Cotton Graphic T-Shirt', 'Kids', 160.0, 349.0),
  ('PRD_KID_02', 'Children Educational Puzzle Game', 'Kids', 130.0, 275.0),
  ('PRD_LAP_01', 'Laptop Stand Aluminum Ergonomic', 'Laptops', 420.0, 899.0),
  ('PRD_LAP_02', 'Wireless Optical Mouse 2.4GHz', 'Laptops', 210.0, 499.0),
  ('PRD_MEA_01', 'Special North Indian Thali Combo', 'Meals', 110.0, 220.0),
  ('PRD_MEA_02', 'Paneer Butter Masala Meal Box', 'Meals', 125.0, 250.0),
  ('PRD_MED_01', 'Paracetamol 650mg Strip of 15', 'Medicine', 18.0, 35.0),
  ('PRD_MED_02', 'Multivitamin & Minerals 30 Tablets', 'Medicine', 120.0, 240.0),
  ('PRD_MEN_01', 'Men Casual Slim-Fit Cotton Shirt', 'Men', 380.0, 799.0),
  ('PRD_MEN_02', 'Men Comfort Stretch Denim Jeans', 'Men', 550.0, 1199.0),
  ('PRD_MOB_01', 'Entry-level 4G Smartphone 32GB', 'Mobiles', 4800.0, 6499.0),
  ('PRD_MOB_02', 'Budget 5G Smartphone 128GB', 'Mobiles', 8800.0, 11999.0),
  ('PRD_NOT_01', 'Spiral Hardcover Journal 200 Pages', 'Notebooks', 85.0, 160.0),
  ('PRD_NOT_02', 'Executive PU Leather Diary', 'Notebooks', 130.0, 260.0),
  ('PRD_OFF_01', 'Heavy Duty Desktop Stapler Set', 'Office Supplies', 90.0, 175.0),
  ('PRD_OFF_02', 'A4 Copier Paper Ream 500 Sheets', 'Office Supplies', 190.0, 310.0),
  ('PRD_PAS_01', 'Red Velvet Pastry Slice', 'Pastries', 45.0, 95.0),
  ('PRD_PAS_02', 'Choco Lava Lava Cake Single', 'Pastries', 50.0, 110.0),
  ('PRD_PER_01', 'Herbal Aloe Vera Face Wash 150ml', 'Personal Care', 80.0, 155.0),
  ('PRD_PER_02', 'Moisturizing Shea Body Lotion 250ml', 'Personal Care', 120.0, 235.0),
  ('PRD_SNK_01', 'Spicy Masala Potato Chips 150g', 'Snacks', 22.0, 45.0),
  ('PRD_SNK_02', 'Roasted Salted Almonds 200g', 'Snacks', 130.0, 225.0),
  ('PRD_STA_01', 'Premium Basmati Rice 5kg', 'Staples', 380.0, 540.0),
  ('PRD_STA_02', 'Sharbati Whole Wheat Atta 5kg', 'Staples', 160.0, 245.0),
  ('PRD_TEA_01', 'Assam Masala CTC Chai 500g', 'Tea', 130.0, 240.0),
  ('PRD_TEA_02', 'Organic Darjeeling Green Tea 100g', 'Tea', 110.0, 210.0),
  ('PRD_WEL_01', 'Immunity Booster Chyawanprash 1kg', 'Wellness', 220.0, 375.0),
  ('PRD_WEL_02', 'Pure Apple Cider Vinegar 500ml', 'Wellness', 140.0, 280.0),
  ('PRD_WOM_01', 'Women Pure Cotton Printed Kurti', 'Women', 310.0, 699.0),
  ('PRD_WOM_02', 'Embroidered Rayon Anarkali Suit', 'Women', 650.0, 1499.0),
  ('PRD_WRI_01', 'Gel Roller Pen Blue Pack of 5', 'Writing', 45.0, 90.0),
  ('PRD_WRI_02', 'Permanent Whiteboard Marker Set 4s', 'Writing', 55.0, 115.0)
ON CONFLICT DO NOTHING;

INSERT INTO public."clean_merchants" ("merchant_id", "merchant_name", "business_type", "city", "state", "pincode", "latitude", "longitude")
VALUES
  ('M015', 'Merchant_015', 'Bakery', 'Noida', 'Uttar Pradesh', '201301', 28.5355, 77.391),
  ('M045', 'Merchant_045', 'Grocery', 'Prayagraj', 'Uttar Pradesh', '211001', 25.4358, 81.8463),
  ('M040', 'Merchant_040', 'Cafe', 'Noida', 'Uttar Pradesh', '201301', 28.5355, 77.391),
  ('M044', 'Merchant_044', 'Clothing', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M007', 'Merchant_007', 'Grocery', 'Patna', 'Bihar', '800001', 25.5941, 85.1376),
  ('M046', 'Merchant_046', 'General Store', 'Kanpur', 'Uttar Pradesh', '208001', 26.4499, 80.3319),
  ('M023', 'Merchant_023', 'Restaurant', 'Kanpur', 'Uttar Pradesh', '208001', 26.4499, 80.3319),
  ('M033', 'Merchant_033', 'Grocery', 'Agra', 'Uttar Pradesh', '282001', 27.1767, 78.0081),
  ('M021', 'Merchant_021', 'Stationery', 'Jaipur', 'Rajasthan', '302001', 26.9124, 75.7873),
  ('M012', 'Merchant_012', 'General Store', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M041', 'Merchant_041', 'Restaurant', 'Agra', 'Uttar Pradesh', '282001', 27.1767, 78.0081),
  ('M038', 'Merchant_038', 'Mobile Accessories', 'Agra', 'Uttar Pradesh', '282001', 27.1767, 78.0081),
  ('M047', 'Merchant_047', 'Electronics', 'Varanasi', 'Uttar Pradesh', '221001', 25.3176, 82.9739),
  ('M025', 'Merchant_025', 'Bakery', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M029', 'Merchant_029', 'Stationery', 'Noida', 'Uttar Pradesh', '201301', 28.5355, 77.391),
  ('M005', 'Merchant_005', 'Electronics', 'Noida', 'Uttar Pradesh', '201301', 28.5355, 77.391),
  ('M008', 'Merchant_008', 'Cafe', 'Varanasi', 'Uttar Pradesh', '221001', 25.3176, 82.9739),
  ('M024', 'Merchant_024', 'General Store', 'Noida', 'Uttar Pradesh', '201301', 28.5355, 77.391),
  ('M017', 'Merchant_017', 'Stationery', 'Jaipur', 'Rajasthan', '302001', 26.9124, 75.7873),
  ('M003', 'Merchant_003', 'Cafe', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M026', 'Merchant_026', 'Cafe', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M002', 'Merchant_002', 'Bakery', 'Prayagraj', 'Uttar Pradesh', '211001', 25.4358, 81.8463),
  ('M022', 'Merchant_022', 'Clothing', 'Varanasi', 'Uttar Pradesh', '221001', 25.3176, 82.9739),
  ('M039', 'Merchant_039', 'Pharmacy', 'Gorakhpur', 'Uttar Pradesh', '273001', 26.7606, 83.3732),
  ('M001', 'Merchant_001', 'Grocery', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M048', 'Merchant_048', 'Mobile Accessories', 'Delhi', 'Delhi', '110001', 28.6139, 77.209),
  ('M042', 'Merchant_042', 'Bakery', 'Agra', 'Uttar Pradesh', '282001', 27.1767, 78.0081),
  ('M010', 'Merchant_010', 'Grocery', 'Prayagraj', 'Uttar Pradesh', '211001', 25.4358, 81.8463),
  ('M049', 'Merchant_049', 'Cafe', 'Kanpur', 'Uttar Pradesh', '208001', 26.4499, 80.3319),
  ('M006', 'Merchant_006', 'Mobile Accessories', 'Gorakhpur', 'Uttar Pradesh', '273001', 26.7606, 83.3732),
  ('M009', 'Merchant_009', 'Pharmacy', 'Varanasi', 'Uttar Pradesh', '221001', 25.3176, 82.9739),
  ('M011', 'Merchant_011', 'Stationery', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M035', 'Merchant_035', 'Mobile Accessories', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M016', 'Merchant_016', 'Bakery', 'Prayagraj', 'Uttar Pradesh', '211001', 25.4358, 81.8463),
  ('M014', 'Merchant_014', 'Bakery', 'Kanpur', 'Uttar Pradesh', '208001', 26.4499, 80.3319),
  ('M034', 'Merchant_034', 'Stationery', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M019', 'Merchant_019', 'Mobile Accessories', 'Kanpur', 'Uttar Pradesh', '208001', 26.4499, 80.3319),
  ('M030', 'Merchant_030', 'Electronics', 'Noida', 'Uttar Pradesh', '201301', 28.5355, 77.391),
  ('M004', 'Merchant_004', 'Electronics', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M043', 'Merchant_043', 'Bakery', 'Kanpur', 'Uttar Pradesh', '208001', 26.4499, 80.3319),
  ('M036', 'Merchant_036', 'Grocery', 'Noida', 'Uttar Pradesh', '201301', 28.5355, 77.391),
  ('M050', 'Merchant_050', 'Bakery', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M031', 'Merchant_031', 'Electronics', 'Gorakhpur', 'Uttar Pradesh', '273001', 26.7606, 83.3732),
  ('M013', 'Merchant_013', 'Bakery', 'Prayagraj', 'Uttar Pradesh', '211001', 25.4358, 81.8463),
  ('M027', 'Merchant_027', 'Electronics', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
  ('M028', 'Merchant_028', 'Mobile Accessories', 'Gorakhpur', 'Uttar Pradesh', '273001', 26.7606, 83.3732),
  ('M018', 'Merchant_018', 'Restaurant', 'Noida', 'Uttar Pradesh', '201301', 28.5355, 77.391),
  ('M032', 'Merchant_032', 'Pharmacy', 'Prayagraj', 'Uttar Pradesh', '211001', 25.4358, 81.8463),
  ('M037', 'Merchant_037', 'Mobile Accessories', 'Prayagraj', 'Uttar Pradesh', '211001', 25.4358, 81.8463),
  ('M020', 'Merchant_020', 'Electronics', 'Jaipur', 'Rajasthan', '302001', 26.9124, 75.7873)
ON CONFLICT DO NOTHING;

INSERT INTO public."sales_forecast_7d" ("forecast_date", "predicted_revenue", "lower_bound", "upper_bound", "model_name", "model_version", "generated_at")
VALUES
  ('2026-09-24', 38340.83, NULL, NULL, 'RandomForestRegressor', 'v1.0', '2026-09-25 17:21:56'),
  ('2026-09-25', 38261.28, NULL, NULL, 'RandomForestRegressor', 'v1.0', '2026-09-25 17:21:56'),
  ('2026-09-26', 41177.99, NULL, NULL, 'RandomForestRegressor', 'v1.0', '2026-09-25 17:21:56'),
  ('2026-09-27', 48672.93, NULL, NULL, 'RandomForestRegressor', 'v1.0', '2026-09-25 17:21:56'),
  ('2026-09-28', 39463.73, NULL, NULL, 'RandomForestRegressor', 'v1.0', '2026-09-25 17:21:56'),
  ('2026-09-29', 37904.18, NULL, NULL, 'RandomForestRegressor', 'v1.0', '2026-09-25 17:21:56'),
  ('2026-09-30', 40411.52, NULL, NULL, 'RandomForestRegressor', 'v1.0', '2026-09-25 17:21:57')
ON CONFLICT DO NOTHING;

INSERT INTO public."business_trend_predictions" ("prediction_date", "horizon_days", "predicted_trend", "confidence", "model_name", "model_version")
VALUES
  ('2026-09-16', 7, 'DECREASING', 0.8945, 'HistGradientBoostingClassifier_Trend', 'v1.0')
ON CONFLICT DO NOTHING;

INSERT INTO public."all_recommendations" ("recommendation_id", "merchant_id", "type", "priority", "priority_band", "confidence", "urgency", "expected_impact", "entity_type", "entity_id", "title", "action", "reason", "created_at", "status")
VALUES
  ('REC_CUST_C03388', NULL, 'RETENTION', 0.8009, 'CRITICAL', 0.8105, 0.8435299999999999, 0.7515, 'customer', 'C03388', 'High-Value Customer Retention: Customer_C03388 (C03388)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹16,767.84, 3 orders), but has been inactive for 112 days with an estimated churn/inactivity risk of 69.6%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01719', NULL, 'RETENTION', 0.7972, 'CRITICAL', 0.8061, 0.8373349999999999, 0.7506, 'customer', 'C01719', 'High-Value Customer Retention: Customer_C01719 (C01719)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹7,575.64, 2 orders), but has been inactive for 78 days with an estimated churn/inactivity risk of 67.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01750', NULL, 'RETENTION', 0.7965, 'CRITICAL', 0.8053, 0.8361099999999999, 0.7504, 'customer', 'C01750', 'High-Value Customer Retention: Customer_C01750 (C01750)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹12,311.86, 4 orders), but has been inactive for 152 days with an estimated churn/inactivity risk of 67.5%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02719', NULL, 'RETENTION', 0.7958, 'CRITICAL', 0.8045, 0.8350599999999999, 0.7503, 'customer', 'C02719', 'High-Value Customer Retention: Customer_C02719 (C02719)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹12,387.47, 4 orders), but has been inactive for 32 days with an estimated churn/inactivity risk of 67.2%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C03457', NULL, 'RETENTION', 0.7953, 'CRITICAL', 0.804, 0.83422, 0.7501, 'customer', 'C03457', 'High-Value Customer Retention: Customer_C03457 (C03457)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹29,573.55, 6 orders), but has been inactive for 17 days with an estimated churn/inactivity risk of 66.9%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02004', NULL, 'RETENTION', 0.7951, 'CRITICAL', 0.8037, 0.83387, 0.7501, 'customer', 'C02004', 'High-Value Customer Retention: Customer_C02004 (C02004)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹9,413.47, 3 orders), but has been inactive for 98 days with an estimated churn/inactivity risk of 66.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02137', NULL, 'RETENTION', 0.7944, 'CRITICAL', 0.8029, 0.832785, 0.7499, 'customer', 'C02137', 'High-Value Customer Retention: Customer_C02137 (C02137)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹16,991.95, 6 orders), but has been inactive for 97 days with an estimated churn/inactivity risk of 66.5%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02312', NULL, 'RETENTION', 0.7938, 'CRITICAL', 0.8022, 0.8317, 0.7498, 'customer', 'C02312', 'High-Value Customer Retention: Customer_C02312 (C02312)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹17,306.04, 3 orders), but has been inactive for 83 days with an estimated churn/inactivity risk of 66.2%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00617', NULL, 'RETENTION', 0.7931, 'CRITICAL', 0.8013, 0.830475, 0.7496, 'customer', 'C00617', 'High-Value Customer Retention: Customer_C00617 (C00617)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹15,425.43, 2 orders), but has been inactive for 74 days with an estimated churn/inactivity risk of 65.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00305', NULL, 'RETENTION', 0.793, 'CRITICAL', 0.8013, 0.8303699999999999, 0.7496, 'customer', 'C00305', 'High-Value Customer Retention: Customer_C00305 (C00305)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹13,112.03, 2 orders), but has been inactive for 155 days with an estimated churn/inactivity risk of 65.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02142', NULL, 'RETENTION', 0.793, 'CRITICAL', 0.8039, 0.8341149999999999, 0.7438, 'customer', 'C02142', 'High-Value Customer Retention: Customer_C02142 (C02142)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹10,549.19, 4 orders), but has been inactive for 73 days with an estimated churn/inactivity risk of 66.9%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01225', NULL, 'RETENTION', 0.7927, 'CRITICAL', 0.8009, 0.82988, 0.7494, 'customer', 'C01225', 'High-Value Customer Retention: Customer_C01225 (C01225)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹10,798.26, 4 orders), but has been inactive for 90 days with an estimated churn/inactivity risk of 65.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C03276', NULL, 'RETENTION', 0.7926, 'CRITICAL', 0.8008, 0.8297399999999999, 0.7495, 'customer', 'C03276', 'High-Value Customer Retention: Customer_C03276 (C03276)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹7,384.11, 2 orders), but has been inactive for 165 days with an estimated churn/inactivity risk of 65.6%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02038', NULL, 'RETENTION', 0.7921, 'CRITICAL', 0.8002, 0.8289, 0.7493, 'customer', 'C02038', 'High-Value Customer Retention: Customer_C02038 (C02038)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹14,661.69, 4 orders), but has been inactive for 145 days with an estimated churn/inactivity risk of 65.4%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C03372', NULL, 'RETENTION', 0.792, 'CRITICAL', 0.8001, 0.8287599999999999, 0.7493, 'customer', 'C03372', 'High-Value Customer Retention: Customer_C03372 (C03372)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹15,230.88, 4 orders), but has been inactive for 4 days with an estimated churn/inactivity risk of 65.4%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02795', NULL, 'RETENTION', 0.7918, 'CRITICAL', 0.7999, 0.828375, 0.7491, 'customer', 'C02795', 'High-Value Customer Retention: Customer_C02795 (C02795)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹18,887.56, 7 orders), but has been inactive for 98 days with an estimated churn/inactivity risk of 65.2%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00035', NULL, 'RETENTION', 0.7914, 'CRITICAL', 0.7994, 0.827745, 0.7492, 'customer', 'C00035', 'High-Value Customer Retention: Customer_C00035 (C00035)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹16,500.00, 1 orders), but has been inactive for 312 days with an estimated churn/inactivity risk of 65.1%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01204', NULL, 'RETENTION', 0.7914, 'CRITICAL', 0.7994, 0.8276749999999999, 0.7492, 'customer', 'C01204', 'High-Value Customer Retention: Customer_C01204 (C01204)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹6,690.58, 2 orders), but has been inactive for 75 days with an estimated churn/inactivity risk of 65.0%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02701', NULL, 'RETENTION', 0.7914, 'CRITICAL', 0.7994, 0.827745, 0.7492, 'customer', 'C02701', 'High-Value Customer Retention: Customer_C02701 (C02701)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹16,500.00, 1 orders), but has been inactive for 312 days with an estimated churn/inactivity risk of 65.1%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C03212', NULL, 'RETENTION', 0.7908, 'CRITICAL', 0.7987, 0.826695, 0.749, 'customer', 'C03212', 'High-Value Customer Retention: Customer_C03212 (C03212)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹11,827.88, 4 orders), but has been inactive for 276 days with an estimated churn/inactivity risk of 64.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01545', NULL, 'RETENTION', 0.7907, 'CRITICAL', 0.7985, 0.8264849999999999, 0.749, 'customer', 'C01545', 'High-Value Customer Retention: Customer_C01545 (C01545)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹7,685.19, 2 orders), but has been inactive for 97 days with an estimated churn/inactivity risk of 64.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00971', NULL, 'RETENTION', 0.7906, 'CRITICAL', 0.7985, 0.82638, 0.749, 'customer', 'C00971', 'High-Value Customer Retention: Customer_C00971 (C00971)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹21,119.35, 7 orders), but has been inactive for 58 days with an estimated churn/inactivity risk of 64.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02546', NULL, 'RETENTION', 0.7905, 'CRITICAL', 0.7984, 0.8263099999999999, 0.7489, 'customer', 'C02546', 'High-Value Customer Retention: Customer_C02546 (C02546)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹19,467.39, 6 orders), but has been inactive for 19 days with an estimated churn/inactivity risk of 64.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02078', NULL, 'RETENTION', 0.7894, 'HIGH', 0.7971, 0.8244199999999999, 0.7487, 'customer', 'C02078', 'High-Value Customer Retention: Customer_C02078 (C02078)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹14,580.24, 4 orders), but has been inactive for 143 days with an estimated churn/inactivity risk of 64.1%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00548', NULL, 'RETENTION', 0.7891, 'HIGH', 0.7967, 0.823895, 0.7486, 'customer', 'C00548', 'High-Value Customer Retention: Customer_C00548 (C00548)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹26,934.81, 3 orders), but has been inactive for 29 days with an estimated churn/inactivity risk of 64.0%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02528', NULL, 'RETENTION', 0.7891, 'HIGH', 0.7967, 0.8237899999999999, 0.7486, 'customer', 'C02528', 'High-Value Customer Retention: Customer_C02528 (C02528)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹8,174.23, 2 orders), but has been inactive for 15 days with an estimated churn/inactivity risk of 63.9%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01296', NULL, 'RETENTION', 0.7888, 'HIGH', 0.7964, 0.8234049999999999, 0.7485, 'customer', 'C01296', 'High-Value Customer Retention: Customer_C01296 (C01296)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹14,810.50, 5 orders), but has been inactive for 42 days with an estimated churn/inactivity risk of 63.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00472', NULL, 'RETENTION', 0.7887, 'HIGH', 0.7962, 0.823195, 0.7485, 'customer', 'C00472', 'High-Value Customer Retention: Customer_C00472 (C00472)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹8,659.31, 3 orders), but has been inactive for 84 days with an estimated churn/inactivity risk of 63.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00724', NULL, 'RETENTION', 0.7885, 'HIGH', 0.796, 0.82281, 0.7484, 'customer', 'C00724', 'High-Value Customer Retention: Customer_C00724 (C00724)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹9,080.17, 3 orders), but has been inactive for 172 days with an estimated churn/inactivity risk of 63.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00012', NULL, 'RETENTION', 0.7883, 'HIGH', 0.8017, 0.83107, 0.7351, 'customer', 'C00012', 'High-Value Customer Retention: Customer_C00012 (C00012)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹7,661.75, 3 orders), but has been inactive for 58 days with an estimated churn/inactivity risk of 66.0%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02566', NULL, 'RETENTION', 0.7882, 'HIGH', 0.7957, 0.82239, 0.7484, 'customer', 'C02566', 'High-Value Customer Retention: Customer_C02566 (C02566)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹14,241.53, 5 orders), but has been inactive for 25 days with an estimated churn/inactivity risk of 63.5%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01279', NULL, 'RETENTION', 0.788, 'HIGH', 0.7955, 0.8220749999999999, 0.7483, 'customer', 'C01279', 'High-Value Customer Retention: Customer_C01279 (C01279)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹20,478.75, 3 orders), but has been inactive for 27 days with an estimated churn/inactivity risk of 63.4%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02441', NULL, 'RETENTION', 0.788, 'HIGH', 0.7954, 0.822005, 0.7483, 'customer', 'C02441', 'High-Value Customer Retention: Customer_C02441 (C02441)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹17,662.96, 2 orders), but has been inactive for 86 days with an estimated churn/inactivity risk of 63.4%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C03100', NULL, 'RETENTION', 0.7879, 'HIGH', 0.7953, 0.82183, 0.7483, 'customer', 'C03100', 'High-Value Customer Retention: Customer_C03100 (C03100)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹12,168.01, 4 orders), but has been inactive for 162 days with an estimated churn/inactivity risk of 63.4%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00463', NULL, 'RETENTION', 0.7876, 'HIGH', 0.795, 0.821375, 0.7482, 'customer', 'C00463', 'High-Value Customer Retention: Customer_C00463 (C00463)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹7,503.84, 2 orders), but has been inactive for 86 days with an estimated churn/inactivity risk of 63.2%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01846', NULL, 'RETENTION', 0.7876, 'HIGH', 0.7949, 0.821305, 0.7482, 'customer', 'C01846', 'High-Value Customer Retention: Customer_C01846 (C01846)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹13,903.75, 4 orders), but has been inactive for 0 days with an estimated churn/inactivity risk of 63.2%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02720', NULL, 'RETENTION', 0.7876, 'HIGH', 0.795, 0.82148, 0.7482, 'customer', 'C02720', 'High-Value Customer Retention: Customer_C02720 (C02720)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹15,900.00, 1 orders), but has been inactive for 295 days with an estimated churn/inactivity risk of 63.3%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00727', NULL, 'RETENTION', 0.7873, 'HIGH', 0.7946, 0.82085, 0.7481, 'customer', 'C00727', 'High-Value Customer Retention: Customer_C00727 (C00727)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹14,555.58, 4 orders), but has been inactive for 28 days with an estimated churn/inactivity risk of 63.1%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00516', NULL, 'RETENTION', 0.7872, 'HIGH', 0.7945, 0.8206749999999999, 0.7481, 'customer', 'C00516', 'High-Value Customer Retention: Customer_C00516 (C00516)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹19,030.17, 2 orders), but has been inactive for 232 days with an estimated churn/inactivity risk of 63.0%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01950', NULL, 'RETENTION', 0.7871, 'HIGH', 0.7944, 0.820535, 0.7481, 'customer', 'C01950', 'High-Value Customer Retention: Customer_C01950 (C01950)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹15,130.95, 3 orders), but has been inactive for 47 days with an estimated churn/inactivity risk of 63.0%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00740', NULL, 'RETENTION', 0.7868, 'HIGH', 0.7941, 0.8201499999999999, 0.748, 'customer', 'C00740', 'High-Value Customer Retention: Customer_C00740 (C00740)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹11,001.96, 3 orders), but has been inactive for 28 days with an estimated churn/inactivity risk of 62.9%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00148', NULL, 'RETENTION', 0.7867, 'HIGH', 0.794, 0.8199399999999999, 0.748, 'customer', 'C00148', 'High-Value Customer Retention: Customer_C00148 (C00148)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹10,172.04, 3 orders), but has been inactive for 76 days with an estimated churn/inactivity risk of 62.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02642', NULL, 'RETENTION', 0.7867, 'HIGH', 0.7939, 0.81987, 0.748, 'customer', 'C02642', 'High-Value Customer Retention: Customer_C02642 (C02642)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹24,782.17, 5 orders), but has been inactive for 40 days with an estimated churn/inactivity risk of 62.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02549', NULL, 'RETENTION', 0.7866, 'HIGH', 0.7938, 0.8196599999999999, 0.7479, 'customer', 'C02549', 'High-Value Customer Retention: Customer_C02549 (C02549)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹13,214.00, 3 orders), but has been inactive for 27 days with an estimated churn/inactivity risk of 62.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00369', NULL, 'RETENTION', 0.7865, 'HIGH', 0.8072, 0.8388749999999999, 0.7186, 'customer', 'C00369', 'High-Value Customer Retention: Customer_C00369 (C00369)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹16,643.32, 7 orders), but has been inactive for 26 days with an estimated churn/inactivity risk of 68.2%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01745', NULL, 'RETENTION', 0.7863, 'HIGH', 0.7934, 0.81917, 0.7479, 'customer', 'C01745', 'High-Value Customer Retention: Customer_C01745 (C01745)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹10,852.04, 2 orders), but has been inactive for 79 days with an estimated churn/inactivity risk of 62.6%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02132', NULL, 'RETENTION', 0.7861, 'HIGH', 0.7932, 0.8188899999999999, 0.7478, 'customer', 'C02132', 'High-Value Customer Retention: Customer_C02132 (C02132)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹11,356.84, 2 orders), but has been inactive for 227 days with an estimated churn/inactivity risk of 62.5%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01126', NULL, 'RETENTION', 0.786, 'HIGH', 0.7938, 0.8196599999999999, 0.7462, 'customer', 'C01126', 'High-Value Customer Retention: Customer_C01126 (C01126)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹10,728.87, 4 orders), but has been inactive for 90 days with an estimated churn/inactivity risk of 62.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00591', NULL, 'RETENTION', 0.7858, 'HIGH', 0.7929, 0.818365, 0.7478, 'customer', 'C00591', 'High-Value Customer Retention: Customer_C00591 (C00591)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹17,308.23, 3 orders), but has been inactive for 36 days with an estimated churn/inactivity risk of 62.4%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01157', NULL, 'RETENTION', 0.7857, 'HIGH', 0.7928, 0.818225, 0.7477, 'customer', 'C01157', 'High-Value Customer Retention: Customer_C01157 (C01157)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹14,442.29, 5 orders), but has been inactive for 95 days with an estimated churn/inactivity risk of 62.4%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01651', NULL, 'RETENTION', 0.7856, 'HIGH', 0.7926, 0.8180149999999999, 0.7477, 'customer', 'C01651', 'High-Value Customer Retention: Customer_C01651 (C01651)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹9,029.60, 3 orders), but has been inactive for 13 days with an estimated churn/inactivity risk of 62.3%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00713', NULL, 'RETENTION', 0.7853, 'HIGH', 0.7924, 0.817665, 0.7476, 'customer', 'C00713', 'High-Value Customer Retention: Customer_C00713 (C00713)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹11,885.88, 2 orders), but has been inactive for 240 days with an estimated churn/inactivity risk of 62.2%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00289', NULL, 'RETENTION', 0.7852, 'HIGH', 0.7922, 0.8174199999999999, 0.7476, 'customer', 'C00289', 'High-Value Customer Retention: Customer_C00289 (C00289)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹12,423.53, 3 orders), but has been inactive for 10 days with an estimated churn/inactivity risk of 62.1%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00450', NULL, 'RETENTION', 0.7851, 'HIGH', 0.792, 0.817175, 0.7476, 'customer', 'C00450', 'High-Value Customer Retention: Customer_C00450 (C00450)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹11,348.98, 4 orders), but has been inactive for 91 days with an estimated churn/inactivity risk of 62.1%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01328', NULL, 'RETENTION', 0.7851, 'HIGH', 0.7985, 0.8264849999999999, 0.7332, 'customer', 'C01328', 'High-Value Customer Retention: Customer_C01328 (C01328)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹12,711.98, 5 orders), but has been inactive for 56 days with an estimated churn/inactivity risk of 64.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02917', NULL, 'RETENTION', 0.785, 'HIGH', 0.792, 0.817105, 0.7476, 'customer', 'C02917', 'High-Value Customer Retention: Customer_C02917 (C02917)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹6,830.77, 1 orders), but has been inactive for 99 days with an estimated churn/inactivity risk of 62.0%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C03289', NULL, 'RETENTION', 0.785, 'HIGH', 0.7919, 0.817, 0.7476, 'customer', 'C03289', 'High-Value Customer Retention: Customer_C03289 (C03289)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹8,511.25, 3 orders), but has been inactive for 82 days with an estimated churn/inactivity risk of 62.0%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01554', NULL, 'RETENTION', 0.7848, 'HIGH', 0.7917, 0.8167199999999999, 0.7475, 'customer', 'C01554', 'High-Value Customer Retention: Customer_C01554 (C01554)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹15,815.15, 5 orders), but has been inactive for 64 days with an estimated churn/inactivity risk of 61.9%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00567', NULL, 'RETENTION', 0.7847, 'HIGH', 0.7916, 0.816545, 0.7475, 'customer', 'C00567', 'High-Value Customer Retention: Customer_C00567 (C00567)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹12,595.46, 4 orders), but has been inactive for 78 days with an estimated churn/inactivity risk of 61.9%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00058', NULL, 'RETENTION', 0.7846, 'HIGH', 0.7914, 0.8163349999999999, 0.7475, 'customer', 'C00058', 'High-Value Customer Retention: Customer_C00058 (C00058)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹17,105.42, 4 orders), but has been inactive for 170 days with an estimated churn/inactivity risk of 61.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02429', NULL, 'RETENTION', 0.7846, 'HIGH', 0.7915, 0.816475, 0.7475, 'customer', 'C02429', 'High-Value Customer Retention: Customer_C02429 (C02429)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹13,525.64, 4 orders), but has been inactive for 26 days with an estimated churn/inactivity risk of 61.9%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00955', NULL, 'RETENTION', 0.7844, 'HIGH', 0.7913, 0.81609, 0.7474, 'customer', 'C00955', 'High-Value Customer Retention: Customer_C00955 (C00955)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹18,368.68, 2 orders), but has been inactive for 277 days with an estimated churn/inactivity risk of 61.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01998', NULL, 'RETENTION', 0.7844, 'HIGH', 0.7913, 0.816195, 0.7474, 'customer', 'C01998', 'High-Value Customer Retention: Customer_C01998 (C01998)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹12,138.39, 3 orders), but has been inactive for 19 days with an estimated churn/inactivity risk of 61.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02848', NULL, 'RETENTION', 0.7844, 'HIGH', 0.7912, 0.816055, 0.7474, 'customer', 'C02848', 'High-Value Customer Retention: Customer_C02848 (C02848)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹9,512.78, 2 orders), but has been inactive for 99 days with an estimated churn/inactivity risk of 61.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C03199', NULL, 'RETENTION', 0.7843, 'HIGH', 0.7911, 0.8158799999999999, 0.7474, 'customer', 'C03199', 'High-Value Customer Retention: Customer_C03199 (C03199)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹13,590.05, 5 orders), but has been inactive for 140 days with an estimated churn/inactivity risk of 61.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01707', NULL, 'RETENTION', 0.7842, 'HIGH', 0.791, 0.8157749999999999, 0.7474, 'customer', 'C01707', 'High-Value Customer Retention: Customer_C01707 (C01707)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹11,623.61, 3 orders), but has been inactive for 121 days with an estimated churn/inactivity risk of 61.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01588', NULL, 'RETENTION', 0.7841, 'HIGH', 0.7932, 0.8188549999999999, 0.7421, 'customer', 'C01588', 'High-Value Customer Retention: Customer_C01588 (C01588)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹13,215.61, 5 orders), but has been inactive for 12 days with an estimated churn/inactivity risk of 62.5%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00949', NULL, 'RETENTION', 0.7839, 'HIGH', 0.7907, 0.8152849999999999, 0.7473, 'customer', 'C00949', 'High-Value Customer Retention: Customer_C00949 (C00949)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹16,282.38, 4 orders), but has been inactive for 148 days with an estimated churn/inactivity risk of 61.5%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02922', NULL, 'RETENTION', 0.7838, 'HIGH', 0.7906, 0.815145, 0.7473, 'customer', 'C02922', 'High-Value Customer Retention: Customer_C02922 (C02922)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹16,500.00, 1 orders), but has been inactive for 320 days with an estimated churn/inactivity risk of 61.5%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C03139', NULL, 'RETENTION', 0.7838, 'HIGH', 0.7906, 0.815145, 0.7473, 'customer', 'C03139', 'High-Value Customer Retention: Customer_C03139 (C03139)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹13,713.51, 2 orders), but has been inactive for 130 days with an estimated churn/inactivity risk of 61.5%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C03279', NULL, 'RETENTION', 0.7838, 'HIGH', 0.7906, 0.815075, 0.7473, 'customer', 'C03279', 'High-Value Customer Retention: Customer_C03279 (C03279)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹7,072.57, 1 orders), but has been inactive for 153 days with an estimated churn/inactivity risk of 61.5%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C03375', NULL, 'RETENTION', 0.7837, 'HIGH', 0.7905, 0.814935, 0.7472, 'customer', 'C03375', 'High-Value Customer Retention: Customer_C03375 (C03375)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹13,842.40, 5 orders), but has been inactive for 115 days with an estimated churn/inactivity risk of 61.4%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01160', NULL, 'RETENTION', 0.7836, 'HIGH', 0.7904, 0.8148299999999999, 0.7472, 'customer', 'C01160', 'High-Value Customer Retention: Customer_C01160 (C01160)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹11,457.48, 2 orders), but has been inactive for 215 days with an estimated churn/inactivity risk of 61.4%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01679', NULL, 'RETENTION', 0.7836, 'HIGH', 0.7903, 0.8147599999999999, 0.7472, 'customer', 'C01679', 'High-Value Customer Retention: Customer_C01679 (C01679)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹24,728.52, 5 orders), but has been inactive for 75 days with an estimated churn/inactivity risk of 61.4%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C03410', NULL, 'RETENTION', 0.7836, 'HIGH', 0.7904, 0.8147949999999999, 0.7472, 'customer', 'C03410', 'High-Value Customer Retention: Customer_C03410 (C03410)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹10,055.15, 2 orders), but has been inactive for 266 days with an estimated churn/inactivity risk of 61.4%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00671', NULL, 'RETENTION', 0.7834, 'HIGH', 0.79, 0.81434, 0.7472, 'customer', 'C00671', 'High-Value Customer Retention: Customer_C00671 (C00671)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹10,281.83, 3 orders), but has been inactive for 155 days with an estimated churn/inactivity risk of 61.2%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01891', NULL, 'RETENTION', 0.7834, 'HIGH', 0.7901, 0.814375, 0.7472, 'customer', 'C01891', 'High-Value Customer Retention: Customer_C01891 (C01891)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹12,038.32, 3 orders), but has been inactive for 300 days with an estimated churn/inactivity risk of 61.3%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01099', NULL, 'RETENTION', 0.7831, 'HIGH', 0.7897, 0.81385, 0.7471, 'customer', 'C01099', 'High-Value Customer Retention: Customer_C01099 (C01099)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹15,078.10, 2 orders), but has been inactive for 162 days with an estimated churn/inactivity risk of 61.1%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02332', NULL, 'RETENTION', 0.7831, 'HIGH', 0.7897, 0.81392, 0.7471, 'customer', 'C02332', 'High-Value Customer Retention: Customer_C02332 (C02332)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹11,572.49, 4 orders), but has been inactive for 159 days with an estimated churn/inactivity risk of 61.1%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01070', NULL, 'RETENTION', 0.783, 'HIGH', 0.7896, 0.81378, 0.7471, 'customer', 'C01070', 'High-Value Customer Retention: Customer_C01070 (C01070)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹17,067.60, 4 orders), but has been inactive for 208 days with an estimated churn/inactivity risk of 61.1%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02770', NULL, 'RETENTION', 0.783, 'HIGH', 0.7896, 0.8137449999999999, 0.7471, 'customer', 'C02770', 'High-Value Customer Retention: Customer_C02770 (C02770)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹12,801.74, 4 orders), but has been inactive for 102 days with an estimated churn/inactivity risk of 61.1%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00475', NULL, 'RETENTION', 0.7829, 'HIGH', 0.7895, 0.8135699999999999, 0.747, 'customer', 'C00475', 'High-Value Customer Retention: Customer_C00475 (C00475)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹17,693.31, 2 orders), but has been inactive for 306 days with an estimated churn/inactivity risk of 61.0%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02705', NULL, 'RETENTION', 0.7829, 'HIGH', 0.7895, 0.8136049999999999, 0.747, 'customer', 'C02705', 'High-Value Customer Retention: Customer_C02705 (C02705)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹9,019.40, 2 orders), but has been inactive for 125 days with an estimated churn/inactivity risk of 61.0%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01370', NULL, 'RETENTION', 0.7828, 'HIGH', 0.7894, 0.813465, 0.747, 'customer', 'C01370', 'High-Value Customer Retention: Customer_C01370 (C01370)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹14,739.47, 5 orders), but has been inactive for 116 days with an estimated churn/inactivity risk of 61.0%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01812', NULL, 'RETENTION', 0.7828, 'HIGH', 0.7894, 0.81343, 0.747, 'customer', 'C01812', 'High-Value Customer Retention: Customer_C01812 (C01812)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹8,130.83, 2 orders), but has been inactive for 90 days with an estimated churn/inactivity risk of 61.0%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00436', NULL, 'RETENTION', 0.7827, 'HIGH', 0.7893, 0.81329, 0.747, 'customer', 'C00436', 'High-Value Customer Retention: Customer_C00436 (C00436)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹18,375.99, 6 orders), but has been inactive for 8 days with an estimated churn/inactivity risk of 60.9%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00550', NULL, 'RETENTION', 0.7827, 'HIGH', 0.795, 0.82141, 0.7343, 'customer', 'C00550', 'High-Value Customer Retention: Customer_C00550 (C00550)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹12,806.59, 5 orders), but has been inactive for 170 days with an estimated churn/inactivity risk of 63.3%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01300', NULL, 'RETENTION', 0.7826, 'HIGH', 0.7997, 0.828165, 0.7238, 'customer', 'C01300', 'High-Value Customer Retention: Customer_C01300 (C01300)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹14,672.81, 6 orders), but has been inactive for 113 days with an estimated churn/inactivity risk of 65.2%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01576', NULL, 'RETENTION', 0.7826, 'HIGH', 0.7891, 0.813045, 0.747, 'customer', 'C01576', 'High-Value Customer Retention: Customer_C01576 (C01576)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹17,145.62, 6 orders), but has been inactive for 19 days with an estimated churn/inactivity risk of 60.9%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01743', NULL, 'RETENTION', 0.7826, 'HIGH', 0.7892, 0.813115, 0.747, 'customer', 'C01743', 'High-Value Customer Retention: Customer_C01743 (C01743)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹17,689.40, 4 orders), but has been inactive for 246 days with an estimated churn/inactivity risk of 60.9%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02892', NULL, 'RETENTION', 0.7826, 'HIGH', 0.7891, 0.81301, 0.747, 'customer', 'C02892', 'High-Value Customer Retention: Customer_C02892 (C02892)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹16,871.32, 2 orders), but has been inactive for 184 days with an estimated churn/inactivity risk of 60.9%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01309', NULL, 'RETENTION', 0.7825, 'HIGH', 0.8006, 0.82939, 0.7215, 'customer', 'C01309', 'High-Value Customer Retention: Customer_C01309 (C01309)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹7,262.58, 3 orders), but has been inactive for 90 days with an estimated churn/inactivity risk of 65.5%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01454', NULL, 'RETENTION', 0.7824, 'HIGH', 0.7889, 0.812695, 0.7469, 'customer', 'C01454', 'High-Value Customer Retention: Customer_C01454 (C01454)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹9,224.40, 2 orders), but has been inactive for 140 days with an estimated churn/inactivity risk of 60.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02190', NULL, 'RETENTION', 0.7824, 'HIGH', 0.789, 0.8128, 0.7469, 'customer', 'C02190', 'High-Value Customer Retention: Customer_C02190 (C02190)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹15,724.34, 4 orders), but has been inactive for 237 days with an estimated churn/inactivity risk of 60.8%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00420', NULL, 'RETENTION', 0.7822, 'HIGH', 0.7887, 0.8124849999999999, 0.7469, 'customer', 'C00420', 'High-Value Customer Retention: Customer_C00420 (C00420)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹11,754.30, 3 orders), but has been inactive for 214 days with an estimated churn/inactivity risk of 60.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C02952', NULL, 'RETENTION', 0.7822, 'HIGH', 0.7887, 0.8124849999999999, 0.7469, 'customer', 'C02952', 'High-Value Customer Retention: Customer_C02952 (C02952)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹15,444.38, 2 orders), but has been inactive for 100 days with an estimated churn/inactivity risk of 60.7%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01584', NULL, 'RETENTION', 0.782, 'HIGH', 0.7885, 0.8120999999999999, 0.7468, 'customer', 'C01584', 'High-Value Customer Retention: Customer_C01584 (C01584)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹16,663.00, 2 orders), but has been inactive for 265 days with an estimated churn/inactivity risk of 60.6%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01841', NULL, 'RETENTION', 0.782, 'HIGH', 0.7885, 0.8121349999999999, 0.7468, 'customer', 'C01841', 'High-Value Customer Retention: Customer_C01841 (C01841)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹12,901.89, 4 orders), but has been inactive for 3 days with an estimated churn/inactivity risk of 60.6%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C00797', NULL, 'RETENTION', 0.7819, 'HIGH', 0.7884, 0.81203, 0.7468, 'customer', 'C00797', 'High-Value Customer Retention: Customer_C00797 (C00797)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹17,266.01, 3 orders), but has been inactive for 278 days with an estimated churn/inactivity risk of 60.6%.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_CUST_C01067', NULL, 'RETENTION', 0.7819, 'HIGH', 0.7883, 0.811925, 0.7468, 'customer', 'C01067', 'High-Value Customer Retention: Customer_C01067 (C01067)', 'Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer.', 'Customer is in the top 25% of spenders (Total: ₹17,477.37, 5 orders), but has been inactive for 11 days with an estimated churn/inactivity risk of 60.6%.', '2026-09-26 08:43:05', 'GENERATED')
ON CONFLICT DO NOTHING;

INSERT INTO public."pricing_recommendations" ("recommendation_id", "merchant_id", "type", "priority", "priority_band", "confidence", "urgency", "expected_impact", "entity_type", "entity_id", "title", "action", "reason", "created_at", "status")
VALUES
  ('REC_PRICE_PRD_ACC_01', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_ACC_01', 'Protect Pricing Power: Leather Wallet', 'Avoid promotional price-cutting; preserve current price point of ₹499.00.', 'Strong forward demand (6 units/week) paired with healthy 49.9% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_BEV_01', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_BEV_01', 'Protect Pricing Power: Fresh Mango Juice 1L', 'Avoid promotional price-cutting; preserve current price point of ₹110.00.', 'Strong forward demand (6 units/week) paired with healthy 40.9% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_BEV_02', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_BEV_02', 'Protect Pricing Power: Cold Pressed Orange Juice 500ml', 'Avoid promotional price-cutting; preserve current price point of ₹95.00.', 'Strong forward demand (5 units/week) paired with healthy 42.1% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_BRD_02', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_BRD_02', 'Protect Pricing Power: Artisanal Sourdough Bread Loaf', 'Avoid promotional price-cutting; preserve current price point of ₹140.00.', 'Strong forward demand (5 units/week) paired with healthy 46.4% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_EAR_02', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_EAR_02', 'Protect Pricing Power: Deep Bass Wired Earphones 3.5mm', 'Avoid promotional price-cutting; preserve current price point of ₹349.00.', 'Strong forward demand (5 units/week) paired with healthy 59.9% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_ELE_01', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_ELE_01', 'Protect Pricing Power: Smart LED Desk Lamp 10W', 'Avoid promotional price-cutting; preserve current price point of ₹899.00.', 'Strong forward demand (5 units/week) paired with healthy 49.9% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_HOU_01', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_HOU_01', 'Protect Pricing Power: Microfiber Cleaning Cloth 4-Pack', 'Avoid promotional price-cutting; preserve current price point of ₹180.00.', 'Strong forward demand (5 units/week) paired with healthy 55.6% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_HOU_02', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_HOU_02', 'Protect Pricing Power: Aromatherapy Reed Diffuser 100ml', 'Avoid promotional price-cutting; preserve current price point of ₹320.00.', 'Strong forward demand (6 units/week) paired with healthy 50.0% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_LAP_02', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_LAP_02', 'Protect Pricing Power: Wireless Optical Mouse 2.4GHz', 'Avoid promotional price-cutting; preserve current price point of ₹499.00.', 'Strong forward demand (6 units/week) paired with healthy 57.9% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_PAS_01', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_PAS_01', 'Protect Pricing Power: Red Velvet Pastry Slice', 'Avoid promotional price-cutting; preserve current price point of ₹95.00.', 'Strong forward demand (6 units/week) paired with healthy 52.6% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_PAS_02', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_PAS_02', 'Protect Pricing Power: Choco Lava Lava Cake Single', 'Avoid promotional price-cutting; preserve current price point of ₹110.00.', 'Strong forward demand (5 units/week) paired with healthy 54.5% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_SNK_01', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_SNK_01', 'Protect Pricing Power: Spicy Masala Potato Chips 150g', 'Avoid promotional price-cutting; preserve current price point of ₹45.00.', 'Strong forward demand (16 units/week) paired with healthy 51.1% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_SNK_02', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_SNK_02', 'Protect Pricing Power: Roasted Salted Almonds 200g', 'Avoid promotional price-cutting; preserve current price point of ₹225.00.', 'Strong forward demand (15 units/week) paired with healthy 42.2% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_WEL_01', NULL, 'MAINTAIN_PRICE', 0.7316, 'HIGH', 0.8395, 0.65, 0.7175, 'product', 'PRD_WEL_01', 'Protect Pricing Power: Immunity Booster Chyawanprash 1kg', 'Avoid promotional price-cutting; preserve current price point of ₹375.00.', 'Strong forward demand (5 units/week) paired with healthy 41.3% unit margin. Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_ART_01', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_ART_01', 'Curtail Discount Erosion: Acrylic Color Set 12-Pack', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 24.0%, which erodes the nominal margin of 43.8%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_BABY_01', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_BABY_01', 'Curtail Discount Erosion: Baby Diaper Mega Pack (M)', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 23.0%, which erodes the nominal margin of 31.2%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_CAK_01', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_CAK_01', 'Curtail Discount Erosion: Dutch Chocolate Truffle Cake 500g', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 33.9%, which erodes the nominal margin of 49.1%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_CAK_02', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_CAK_02', 'Curtail Discount Erosion: Eggless Pineapple Cake 500g', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 29.4%, which erodes the nominal margin of 51.1%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_CHG_01', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_CHG_01', 'Curtail Discount Erosion: Fast Charger 33W USB-C Adapter', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 15.8%, which erodes the nominal margin of 54.2%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_CHG_02', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_CHG_02', 'Curtail Discount Erosion: Wireless Charging Pad 15W', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 23.1%, which erodes the nominal margin of 54.9%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_COF_01', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_COF_01', 'Curtail Discount Erosion: Arabica Roast Ground Coffee 250g', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 32.5%, which erodes the nominal margin of 44.7%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_COF_02', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_COF_02', 'Curtail Discount Erosion: Instant Cold Brew Premix 200g', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 28.0%, which erodes the nominal margin of 46.4%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_DES_01', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_DES_01', 'Curtail Discount Erosion: Gulab Jamun Box 500g', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 18.4%, which erodes the nominal margin of 45.5%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_DES_02', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_DES_02', 'Curtail Discount Erosion: Belgian Waffle with Syrup', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 15.2%, which erodes the nominal margin of 50.0%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_EAR_01', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_EAR_01', 'Curtail Discount Erosion: TWS True Wireless Earbuds', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 32.2%, which erodes the nominal margin of 50.0%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_MEA_02', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_MEA_02', 'Curtail Discount Erosion: Paneer Butter Masala Meal Box', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 17.0%, which erodes the nominal margin of 50.0%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_MEN_02', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_MEN_02', 'Curtail Discount Erosion: Men Comfort Stretch Denim Jeans', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 21.9%, which erodes the nominal margin of 54.1%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_MOB_01', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_MOB_01', 'Curtail Discount Erosion: Entry-level 4G Smartphone 32GB', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 31.4%, which erodes the nominal margin of 26.1%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_MOB_02', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_MOB_02', 'Curtail Discount Erosion: Budget 5G Smartphone 128GB', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 54.1%, which erodes the nominal margin of 26.7%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_NOT_02', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_NOT_02', 'Curtail Discount Erosion: Executive PU Leather Diary', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 24.8%, which erodes the nominal margin of 50.0%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_OFF_02', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_OFF_02', 'Curtail Discount Erosion: A4 Copier Paper Ream 500 Sheets', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 30.4%, which erodes the nominal margin of 38.7%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_STA_01', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_STA_01', 'Curtail Discount Erosion: Premium Basmati Rice 5kg', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 25.1%, which erodes the nominal margin of 29.6%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_TEA_01', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_TEA_01', 'Curtail Discount Erosion: Assam Masala CTC Chai 500g', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 23.1%, which erodes the nominal margin of 45.8%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_TEA_02', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_TEA_02', 'Curtail Discount Erosion: Organic Darjeeling Green Tea 100g', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 17.5%, which erodes the nominal margin of 47.6%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_WOM_02', NULL, 'LIMIT_DISCOUNT', 0.7265, 'HIGH', 0.8395, 0.7, 0.6525, 'product', 'PRD_WOM_02', 'Curtail Discount Erosion: Embroidered Rayon Anarkali Suit', 'Cap transaction discounts at 5% to preserve realized unit margins.', 'Product has an average historical discount rate of 20.4%, which erodes the nominal margin of 56.6%. Restricting ad-hoc discounts recovers bottom-line profit.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_BABY_02', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_BABY_02', 'Promotional Discount Candidate: Gentle Baby Wet Wipes 72s', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (3.4 units) but healthy margin room (43.8%, ₹70.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_CAS_01', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_CAS_01', 'Promotional Discount Candidate: Shockproof Matte Phone Case', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (3.4 units) but healthy margin room (63.9%, ₹159.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_ESS_01', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_ESS_01', 'Promotional Discount Candidate: Organic Hand Wash 500ml', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (2.7 units) but healthy margin room (48.3%, ₹70.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_ESS_02', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_ESS_02', 'Promotional Discount Candidate: Antibacterial Floor Cleaner 1L', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (3.1 units) but healthy margin room (46.9%, ₹75.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_DAI_02', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_DAI_02', 'Promotional Discount Candidate: Fresh Malai Paneer 200g', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (3.2 units) but healthy margin room (31.6%, ₹30.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_KID_01', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_KID_01', 'Promotional Discount Candidate: Kids Cotton Graphic T-Shirt', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (2.9 units) but healthy margin room (54.1%, ₹189.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_KID_02', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_KID_02', 'Promotional Discount Candidate: Children Educational Puzzle Game', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (2.7 units) but healthy margin room (52.7%, ₹145.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_MED_01', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_MED_01', 'Promotional Discount Candidate: Paracetamol 650mg Strip of 15', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (3.5 units) but healthy margin room (48.6%, ₹17.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_MED_02', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_MED_02', 'Promotional Discount Candidate: Multivitamin & Minerals 30 Tablets', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (2.7 units) but healthy margin room (50.0%, ₹120.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_MEN_01', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_MEN_01', 'Promotional Discount Candidate: Men Casual Slim-Fit Cotton Shirt', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (3.5 units) but healthy margin room (52.4%, ₹419.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_PER_01', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_PER_01', 'Promotional Discount Candidate: Herbal Aloe Vera Face Wash 150ml', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (2.7 units) but healthy margin room (48.4%, ₹75.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_PER_02', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_PER_02', 'Promotional Discount Candidate: Moisturizing Shea Body Lotion 250ml', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (3.5 units) but healthy margin room (48.9%, ₹115.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_WEL_02', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_WEL_02', 'Promotional Discount Candidate: Pure Apple Cider Vinegar 500ml', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (2.7 units) but healthy margin room (50.0%, ₹140.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED'),
  ('REC_PRICE_PRD_WOM_01', NULL, 'PROMOTE', 0.6217, 'MEDIUM', 0.8395, 0.5, 0.5725, 'product', 'PRD_WOM_01', 'Promotional Discount Candidate: Women Pure Cotton Printed Kurti', 'Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity.', 'Product exhibits low projected demand (2.7 units) but healthy margin room (55.6%, ₹389.00). Modest discounting can stimulate sales without compromising unit viability.', '2026-09-26 08:43:05', 'GENERATED')
ON CONFLICT DO NOTHING;

INSERT INTO public."inventory_recommendations" ("recommendation_id", "merchant_id", "type", "priority", "priority_band", "confidence", "urgency", "expected_impact", "entity_type", "entity_id", "title", "action", "reason", "created_at", "status")
VALUES
  ('REC_INV_PRD_SNK_01', NULL, 'RESTOCK', 0.6673, 'MEDIUM', 0.8395, 0.7217343966712899, 0.4905, 'product', 'PRD_SNK_01', 'Restock Spicy Masala Potato Chips 150g (Snacks)', 'Order approximately 21 units to cover 7-day forecast demand of 16 units and 5 units safety stock.', 'Projected 7-day demand is 16 units with daily velocity of 2.2 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 21 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_SNK_02', NULL, 'RESTOCK', 0.6551, 'MEDIUM', 0.8395, 0.7194725692558392, 0.4654, 'product', 'PRD_SNK_02', 'Restock Roasted Salted Almonds 200g (Snacks)', 'Order approximately 20 units to cover 7-day forecast demand of 15 units and 5 units safety stock.', 'Projected 7-day demand is 15 units with daily velocity of 2.2 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 20 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_MOB_01', NULL, 'RESTOCK', 0.6529, 'MEDIUM', 0.8395, 0.5646594594594595, 0.5872, 'product', 'PRD_MOB_01', 'Restock Entry-level 4G Smartphone 32GB (Mobiles)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 2 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_LAP_02', NULL, 'RESTOCK', 0.6465, 'MEDIUM', 0.8395, 0.6503018867924528, 0.495, 'product', 'PRD_LAP_02', 'Restock Wireless Optical Mouse 2.4GHz (Laptops)', 'Order approximately 9 units to cover 7-day forecast demand of 6 units and 2 units safety stock.', 'Projected 7-day demand is 6 units with daily velocity of 0.8 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 9 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_EAR_02', NULL, 'RESTOCK', 0.6423, 'MEDIUM', 0.8395, 0.6315837104072398, 0.4997, 'product', 'PRD_EAR_02', 'Restock Deep Bass Wired Earphones 3.5mm (Earphones)', 'Order approximately 8 units to cover 7-day forecast demand of 5 units and 2 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.7 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_ELE_01', NULL, 'RESTOCK', 0.6368, 'MEDIUM', 0.8395, 0.6183706004140787, 0.4975, 'product', 'PRD_ELE_01', 'Restock Smart LED Desk Lamp 10W (Home Electronics)', 'Order approximately 8 units to cover 7-day forecast demand of 5 units and 3 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.8 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_CAB_01', NULL, 'RESTOCK', 0.6361, 'MEDIUM', 0.8395, 0.6163120879120879, 0.4974, 'product', 'PRD_CAB_01', 'Restock Braided USB-C to USB-C Cable 1.5m (Cables)', 'Order approximately 8 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_MOB_02', NULL, 'RESTOCK', 0.6361, 'MEDIUM', 0.8395, 0.5242259615384616, 0.5849, 'product', 'PRD_MOB_02', 'Restock Budget 5G Smartphone 128GB (Mobiles)', 'Order approximately 6 units to cover 7-day forecast demand of 3 units and 3 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 6 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_EAR_01', NULL, 'RESTOCK', 0.6355, 'MEDIUM', 0.8395, 0.5975693069306931, 0.5117, 'product', 'PRD_EAR_01', 'Restock TWS True Wireless Earbuds (Earphones)', 'Order approximately 8 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_CAB_02', NULL, 'RESTOCK', 0.6349, 'MEDIUM', 0.8395, 0.6133473684210526, 0.497, 'product', 'PRD_CAB_02', 'Restock Lightning Charging Cable 1m (Cables)', 'Order approximately 8 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_ELE_02', NULL, 'RESTOCK', 0.6325, 'MEDIUM', 0.8395, 0.6053030888030888, 0.4979, 'product', 'PRD_ELE_02', 'Restock Electric Kettle 1.5L Stainless Steel (Home Electronics)', 'Order approximately 7 units to cover 7-day forecast demand of 5 units and 2 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_CHG_01', NULL, 'RESTOCK', 0.6304, 'MEDIUM', 0.8395, 0.6177532467532467, 0.4831, 'product', 'PRD_CHG_01', 'Restock Fast Charger 33W USB-C Adapter (Chargers)', 'Order approximately 8 units to cover 7-day forecast demand of 5 units and 2 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.7 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_CAK_02', NULL, 'RESTOCK', 0.6296, 'MEDIUM', 0.8395, 0.636943527591542, 0.4668, 'product', 'PRD_CAK_02', 'Restock Eggless Pineapple Cake 500g (Cakes)', 'Order approximately 10 units to cover 7-day forecast demand of 6 units and 3 units safety stock.', 'Projected 7-day demand is 6 units with daily velocity of 0.9 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 10 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_HOU_01', NULL, 'RESTOCK', 0.627, 'MEDIUM', 0.8395, 0.6098333333333333, 0.4815, 'product', 'PRD_HOU_01', 'Restock Microfiber Cleaning Cloth 4-Pack (Household)', 'Order approximately 9 units to cover 7-day forecast demand of 5 units and 3 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.7 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 9 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_PAS_02', NULL, 'RESTOCK', 0.6267, 'MEDIUM', 0.8395, 0.61309941089838, 0.4782, 'product', 'PRD_PAS_02', 'Restock Choco Lava Lava Cake Single (Pastries)', 'Order approximately 9 units to cover 7-day forecast demand of 5 units and 4 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.8 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 9 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_LAP_01', NULL, 'RESTOCK', 0.6263, 'MEDIUM', 0.8395, 0.5982509652509653, 0.4892, 'product', 'PRD_LAP_01', 'Restock Laptop Stand Aluminum Ergonomic (Laptops)', 'Order approximately 8 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_PAS_01', NULL, 'RESTOCK', 0.6257, 'MEDIUM', 0.8395, 0.61885960591133, 0.4716, 'product', 'PRD_PAS_01', 'Restock Red Velvet Pastry Slice (Pastries)', 'Order approximately 9 units to cover 7-day forecast demand of 6 units and 3 units safety stock.', 'Projected 7-day demand is 6 units with daily velocity of 0.8 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 9 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_ACC_02', NULL, 'RESTOCK', 0.625, 'MEDIUM', 0.8395, 0.6093031055900621, 0.4772, 'product', 'PRD_ACC_02', 'Restock Fashion Sunglasses (Accessories)', 'Order approximately 7 units to cover 7-day forecast demand of 5 units and 2 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_CAS_01', NULL, 'RESTOCK', 0.6241, 'MEDIUM', 0.8395, 0.5872063492063492, 0.4931, 'product', 'PRD_CAS_01', 'Restock Shockproof Matte Phone Case (Cases)', 'Order approximately 7 units to cover 7-day forecast demand of 3 units and 3 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_CAS_02', NULL, 'RESTOCK', 0.624, 'MEDIUM', 0.8395, 0.5870863254392666, 0.4931, 'product', 'PRD_CAS_02', 'Restock Premium Leather Back Case (Cases)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_ACC_01', NULL, 'RESTOCK', 0.6239, 'MEDIUM', 0.8395, 0.6268486140724947, 0.4615, 'product', 'PRD_ACC_01', 'Restock Leather Wallet (Accessories)', 'Order approximately 9 units to cover 7-day forecast demand of 6 units and 3 units safety stock.', 'Projected 7-day demand is 6 units with daily velocity of 0.8 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 9 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_CHG_02', NULL, 'RESTOCK', 0.6239, 'MEDIUM', 0.8395, 0.585521978021978, 0.494, 'product', 'PRD_CHG_02', 'Restock Wireless Charging Pad 15W (Chargers)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_NOT_02', NULL, 'RESTOCK', 0.623, 'MEDIUM', 0.8395, 0.6244270676691729, 0.4612, 'product', 'PRD_NOT_02', 'Restock Executive PU Leather Diary (Notebooks)', 'Order approximately 8 units to cover 7-day forecast demand of 5 units and 2 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.8 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_HOU_02', NULL, 'RESTOCK', 0.6223, 'MEDIUM', 0.8395, 0.6227743842364531, 0.4609, 'product', 'PRD_HOU_02', 'Restock Aromatherapy Reed Diffuser 100ml (Household)', 'Order approximately 9 units to cover 7-day forecast demand of 6 units and 3 units safety stock.', 'Projected 7-day demand is 6 units with daily velocity of 0.8 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 9 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_DES_01', NULL, 'RESTOCK', 0.6213, 'MEDIUM', 0.8395, 0.6418543307086614, 0.445, 'product', 'PRD_DES_01', 'Restock Gulab Jamun Box 500g (Desserts)', 'Order approximately 10 units to cover 7-day forecast demand of 7 units and 3 units safety stock.', 'Projected 7-day demand is 7 units with daily velocity of 1.0 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 10 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_TEA_02', NULL, 'RESTOCK', 0.6212, 'MEDIUM', 0.8395, 0.628399217221135, 0.4543, 'product', 'PRD_TEA_02', 'Restock Organic Darjeeling Green Tea 100g (Tea)', 'Order approximately 8 units to cover 7-day forecast demand of 5 units and 2 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.8 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_WRI_02', NULL, 'RESTOCK', 0.6176, 'MEDIUM', 0.8395, 0.6028412698412698, 0.4654, 'product', 'PRD_WRI_02', 'Restock Permanent Whiteboard Marker Set 4s (Writing)', 'Order approximately 8 units to cover 7-day forecast demand of 5 units and 3 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.7 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_WRI_01', NULL, 'RESTOCK', 0.6146, 'MEDIUM', 0.8395, 0.6038128772635815, 0.4581, 'product', 'PRD_WRI_01', 'Restock Gel Roller Pen Blue Pack of 5 (Writing)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 2 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_OFF_01', NULL, 'RESTOCK', 0.6144, 'MEDIUM', 0.8395, 0.6074122807017545, 0.4549, 'product', 'PRD_OFF_01', 'Restock Heavy Duty Desktop Stapler Set (Office Supplies)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 2 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_MEN_01', NULL, 'RESTOCK', 0.6128, 'MEDIUM', 0.8395, 0.5911578947368421, 0.4637, 'product', 'PRD_MEN_01', 'Restock Men Casual Slim-Fit Cotton Shirt (Men)', 'Order approximately 6 units to cover 7-day forecast demand of 4 units and 2 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 6 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_CAK_01', NULL, 'RESTOCK', 0.6105, 'MEDIUM', 0.8395, 0.5976580547112462, 0.4534, 'product', 'PRD_CAK_01', 'Restock Dutch Chocolate Truffle Cake 500g (Cakes)', 'Order approximately 9 units to cover 7-day forecast demand of 5 units and 4 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.7 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 9 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_BRD_02', NULL, 'RESTOCK', 0.61, 'MEDIUM', 0.8395, 0.6091092750533049, 0.4439, 'product', 'PRD_BRD_02', 'Restock Artisanal Sourdough Bread Loaf (Bread)', 'Order approximately 9 units to cover 7-day forecast demand of 5 units and 3 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.8 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 9 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_MEN_02', NULL, 'RESTOCK', 0.6097, 'MEDIUM', 0.8395, 0.5704246575342465, 0.4733, 'product', 'PRD_MEN_02', 'Restock Men Comfort Stretch Denim Jeans (Men)', 'Order approximately 5 units to cover 7-day forecast demand of 3 units and 2 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.4 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 5 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_MEA_01', NULL, 'RESTOCK', 0.6094, 'MEDIUM', 0.8395, 0.5910357142857143, 0.4562, 'product', 'PRD_MEA_01', 'Restock Special North Indian Thali Combo (Meals)', 'Order approximately 6 units to cover 7-day forecast demand of 4 units and 2 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 6 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_WEL_01', NULL, 'RESTOCK', 0.6091, 'MEDIUM', 0.8395, 0.628671114599686, 0.4281, 'product', 'PRD_WEL_01', 'Restock Immunity Booster Chyawanprash 1kg (Wellness)', 'Order approximately 8 units to cover 7-day forecast demand of 5 units and 2 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.7 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_WOM_01', NULL, 'RESTOCK', 0.6082, 'MEDIUM', 0.8395, 0.5645402597402598, 0.4747, 'product', 'PRD_WOM_01', 'Restock Women Pure Cotton Printed Kurti (Women)', 'Order approximately 5 units to cover 7-day forecast demand of 3 units and 2 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.4 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 5 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_PER_02', NULL, 'RESTOCK', 0.6073, 'MEDIUM', 0.8395, 0.5899473684210527, 0.4522, 'product', 'PRD_PER_02', 'Restock Moisturizing Shea Body Lotion 250ml (Personal Care)', 'Order approximately 6 units to cover 7-day forecast demand of 4 units and 2 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 6 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_DES_02', NULL, 'RESTOCK', 0.606, 'MEDIUM', 0.8395, 0.5828144329896907, 0.4549, 'product', 'PRD_DES_02', 'Restock Belgian Waffle with Syrup (Desserts)', 'Order approximately 8 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_KID_02', NULL, 'RESTOCK', 0.6052, 'MEDIUM', 0.8395, 0.5689617940199336, 0.4641, 'product', 'PRD_KID_02', 'Restock Children Educational Puzzle Game (Kids)', 'Order approximately 5 units to cover 7-day forecast demand of 3 units and 2 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.4 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 5 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_COF_02', NULL, 'RESTOCK', 0.6038, 'MEDIUM', 0.8395, 0.5939137931034484, 0.4416, 'product', 'PRD_COF_02', 'Restock Instant Cold Brew Premix 200g (Coffee)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 2 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_BEV_01', NULL, 'RESTOCK', 0.603, 'MEDIUM', 0.8395, 0.6133367346938776, 0.4258, 'product', 'PRD_BEV_01', 'Restock Fresh Mango Juice 1L (Beverages)', 'Order approximately 10 units to cover 7-day forecast demand of 6 units and 3 units safety stock.', 'Projected 7-day demand is 6 units with daily velocity of 0.9 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 10 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_MED_01', NULL, 'RESTOCK', 0.6026, 'MEDIUM', 0.8395, 0.5785, 0.4505, 'product', 'PRD_MED_01', 'Restock Paracetamol 650mg Strip of 15 (Medicine)', 'Order approximately 6 units to cover 7-day forecast demand of 4 units and 2 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 6 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_ART_01', NULL, 'RESTOCK', 0.6025, 'MEDIUM', 0.8395, 0.5990692640692641, 0.4349, 'product', 'PRD_ART_01', 'Restock Acrylic Color Set 12-Pack (Art Supplies)', 'Order approximately 9 units to cover 7-day forecast demand of 5 units and 4 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.7 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 9 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_KID_01', NULL, 'RESTOCK', 0.6019, 'MEDIUM', 0.8395, 0.5573559718969555, 0.4661, 'product', 'PRD_KID_01', 'Restock Kids Cotton Graphic T-Shirt (Kids)', 'Order approximately 6 units to cover 7-day forecast demand of 3 units and 3 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.4 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 6 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_TEA_01', NULL, 'RESTOCK', 0.6007, 'MEDIUM', 0.8395, 0.5862153734590283, 0.4404, 'product', 'PRD_TEA_01', 'Restock Assam Masala CTC Chai 500g (Tea)', 'Order approximately 8 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_ESS_02', NULL, 'RESTOCK', 0.6, 'MEDIUM', 0.8395, 0.5803837209302326, 0.4433, 'product', 'PRD_ESS_02', 'Restock Antibacterial Floor Cleaner 1L (Daily Essentials)', 'Order approximately 6 units to cover 7-day forecast demand of 3 units and 2 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 6 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_NOT_01', NULL, 'RESTOCK', 0.5996, 'MEDIUM', 0.8395, 0.579400974025974, 0.4432, 'product', 'PRD_NOT_01', 'Restock Spiral Hardcover Journal 200 Pages (Notebooks)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 2 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_WOM_02', NULL, 'RESTOCK', 0.5996, 'MEDIUM', 0.8395, 0.5408313069908814, 0.4749, 'product', 'PRD_WOM_02', 'Restock Embroidered Rayon Anarkali Suit (Women)', 'Order approximately 5 units to cover 7-day forecast demand of 2 units and 2 units safety stock.', 'Projected 7-day demand is 2 units with daily velocity of 0.2 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 5 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_ART_02', NULL, 'RESTOCK', 0.5987, 'MEDIUM', 0.8395, 0.5814121779859485, 0.4397, 'product', 'PRD_ART_02', 'Restock Sketching Canvas Board 10x12 (Art Supplies)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_MED_02', NULL, 'RESTOCK', 0.5974, 'MEDIUM', 0.8395, 0.5619936034115138, 0.4518, 'product', 'PRD_MED_02', 'Restock Multivitamin & Minerals 30 Tablets (Medicine)', 'Order approximately 5 units to cover 7-day forecast demand of 3 units and 2 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.4 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 5 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_WEL_02', NULL, 'RESTOCK', 0.5939, 'MEDIUM', 0.8395, 0.5538088531187123, 0.4506, 'product', 'PRD_WEL_02', 'Restock Pure Apple Cider Vinegar 500ml (Wellness)', 'Order approximately 5 units to cover 7-day forecast demand of 3 units and 2 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.4 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 5 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_MEA_02', NULL, 'RESTOCK', 0.5937, 'MEDIUM', 0.8395, 0.5532061482820977, 0.4505, 'product', 'PRD_MEA_02', 'Restock Paneer Butter Masala Meal Box (Meals)', 'Order approximately 6 units to cover 7-day forecast demand of 3 units and 3 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.4 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 6 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_ESS_01', NULL, 'RESTOCK', 0.5928, 'MEDIUM', 0.8395, 0.5590181086519115, 0.4439, 'product', 'PRD_ESS_01', 'Restock Organic Hand Wash 500ml (Daily Essentials)', 'Order approximately 5 units to cover 7-day forecast demand of 3 units and 2 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.4 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 5 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_PER_01', NULL, 'RESTOCK', 0.5923, 'MEDIUM', 0.8395, 0.5578095238095239, 0.4437, 'product', 'PRD_PER_01', 'Restock Herbal Aloe Vera Face Wash 150ml (Personal Care)', 'Order approximately 5 units to cover 7-day forecast demand of 3 units and 2 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.4 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 5 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_BRD_01', NULL, 'RESTOCK', 0.5917, 'MEDIUM', 0.8395, 0.5725937046004843, 0.4309, 'product', 'PRD_BRD_01', 'Restock Brown Whole Wheat Bread 400g (Bread)', 'Order approximately 8 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_BEV_02', NULL, 'RESTOCK', 0.5916, 'MEDIUM', 0.8395, 0.5808181818181819, 0.4246, 'product', 'PRD_BEV_02', 'Restock Cold Pressed Orange Juice 500ml (Beverages)', 'Order approximately 9 units to cover 7-day forecast demand of 5 units and 3 units safety stock.', 'Projected 7-day demand is 5 units with daily velocity of 0.7 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 9 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_BABY_02', NULL, 'RESTOCK', 0.5882, 'MEDIUM', 0.8395, 0.5642959183673469, 0.4296, 'product', 'PRD_BABY_02', 'Restock Gentle Baby Wet Wipes 72s (Baby Care)', 'Order approximately 7 units to cover 7-day forecast demand of 3 units and 3 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_COF_01', NULL, 'RESTOCK', 0.5872, 'MEDIUM', 0.8395, 0.5576685393258427, 0.4324, 'product', 'PRD_COF_01', 'Restock Arabica Roast Ground Coffee 250g (Coffee)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_OFF_02', NULL, 'RESTOCK', 0.5795, 'MEDIUM', 0.8395, 0.5642674418604652, 0.4109, 'product', 'PRD_OFF_02', 'Restock A4 Copier Paper Ream 500 Sheets (Office Supplies)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_STA_01', NULL, 'RESTOCK', 0.5674, 'MEDIUM', 0.8395, 0.5745000000000001, 0.3787, 'product', 'PRD_STA_01', 'Restock Premium Basmati Rice 5kg (Staples)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 2 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.6 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_STA_02', NULL, 'RESTOCK', 0.5672, 'MEDIUM', 0.8395, 0.551689837008629, 0.394, 'product', 'PRD_STA_02', 'Restock Sharbati Whole Wheat Atta 5kg (Staples)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 3 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_DAI_02', NULL, 'RESTOCK', 0.5584, 'MEDIUM', 0.8395, 0.5436258879242305, 0.3815, 'product', 'PRD_DAI_02', 'Restock Fresh Malai Paneer 200g (Dairy)', 'Order approximately 6 units to cover 7-day forecast demand of 3 units and 2 units safety stock.', 'Projected 7-day demand is 3 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 6 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_DAI_01', NULL, 'RESTOCK', 0.5486, 'LOW', 0.8395, 0.5424421560035056, 0.3626, 'product', 'PRD_DAI_01', 'Restock Fresh Cow Milk Pouch 1L (Dairy)', 'Order approximately 7 units to cover 7-day forecast demand of 4 units and 2 units safety stock.', 'Projected 7-day demand is 4 units with daily velocity of 0.5 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 7 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED'),
  ('REC_INV_PRD_BABY_01', NULL, 'RESTOCK', 0.5369, 'LOW', 0.8395, 0.4971057142857143, 0.3708, 'product', 'PRD_BABY_01', 'Restock Baby Diaper Mega Pack (M) (Baby Care)', 'Order approximately 5 units to cover 7-day forecast demand of 2 units and 2 units safety stock.', 'Projected 7-day demand is 2 units with daily velocity of 0.2 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 5 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).', '2026-09-26 08:43:04', 'GENERATED')
ON CONFLICT DO NOTHING;
