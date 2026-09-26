# VyaparMitra Data Dictionary & Schema Documentation (Phase 1)

This document provides a comprehensive data dictionary for all raw, cleaned, and feature store datasets within the **VyaparMitra** platform.

---

## 1. Raw & Processed Datasets

### A. Transactions (`data/raw/transactions.csv` & `data/processed/clean_transactions.parquet`)

| Column | Data Type | Description | Source | Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `transaction_id` | string | Unique identifier for each transaction record | System/POS | Alphanumeric, non-empty | `TXN0001590` |
| `merchant_id` | string | Unique merchant identifier | System | Registered merchant ID (`M001` - `M050`) | `M015` |
| `customer_id` | string | Unique customer identifier | System | Registered customer ID (`C00001` - `C03308`) | `C03276` |
| `timestamp` | string / datetime | ISO-8601 timestamp of transaction event | POS Terminal | `YYYY-MM-DD HH:MM:SS` | `2025-10-01 11:14:09` |
| `product_id` | string | Foreign key referencing product catalog | POS Terminal | Registered catalog ID | `PRD_CAK_01` |
| `product_category`| string | Primary category of purchased item | Catalog | 32 standard categories | `Cakes` |
| `quantity` | integer | Number of product units purchased | POS Terminal | Integer `> 0` | `2` |
| `unit_price` | float | Selling price per single product unit | Catalog/POS | Float `>= 0.00` | `₹550.00` |
| `discount` | float | Total promotional discount applied | POS/Coupon | Float `0.00 <= discount <= quantity * unit_price` | `₹50.00` |
| `payment_method` | string | Payment channel used for settlement | Payment Gateway | `UPI`, `CASH`, `CARD`, `NETBANKING`, `WALLET` | `UPI` |

---

### B. Merchants (`data/raw/merchants.csv` & `data/processed/clean_merchants.parquet`)

| Column | Data Type | Description | Source | Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `merchant_id` | string | Unique merchant identifier (Primary Key) | Onboarding | `M001` - `M050` | `M015` |
| `merchant_name` | string | Legal or display business name | Onboarding | Text | `Merchant_015` |
| `business_type` | string | Sector / business vertical | Onboarding | `Bakery`, `Cafe`, `Electronics`, `Grocery`, etc. | `Bakery` |
| `city` | string | City location of merchant establishment | Address | Valid Indian cities | `Noida` |
| `state` | string | State or Union Territory | Address | Valid Indian states | `Uttar Pradesh` |
| `pincode` | string | Postal index number | Postal Service | 6-digit Indian PIN | `201301` |
| `latitude` | float | Geographic latitude coordinate | GPS / Geocoding | `-90.0` to `+90.0` | `28.5355` |
| `longitude` | float | Geographic longitude coordinate | GPS / Geocoding | `-180.0` to `+180.0` | `77.3910` |

---

### C. Customers (`data/raw/customers.csv` & `data/processed/clean_customers.parquet`)

| Column | Data Type | Description | Source | Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `customer_id` | string | Unique customer identifier (Primary Key) | CRM | `C00001` - `C03308` | `C03276` |
| `customer_name` | string | Name of registered customer | CRM | Text | `Customer_C03276` |
| `customer_type` | string | Engagement classification | CRM | `New`, `Regular`, `Repeat` | `Repeat` |
| `city` | string | Primary residential or operating city | Profile | Valid Indian cities | `Noida` |
| `signup_date` | string / date | Customer registration date | CRM | `YYYY-MM-DD` | `2025-01-15` |

---

### D. Products (`data/raw/products.csv` & `data/processed/clean_products.parquet`)

| Column | Data Type | Description | Source | Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `product_id` | string | Unique SKU identifier (Primary Key) | Inventory | Standard SKU code | `PRD_CAK_01` |
| `product_name` | string | Commercial product title | Inventory | Text | `Dutch Chocolate Truffle Cake 500g` |
| `product_category`| string | Product taxonomy category | Catalog | 32 categories | `Cakes` |
| `unit_cost` | float | Wholesale unit acquisition cost | Procurement | Float `>= 0.00` | `₹280.00` |
| `selling_price` | float | Recommended base selling price | Catalog | Float `>= unit_cost` | `₹550.00` |

---

### E. Festivals / Calendar (`data/raw/festivals.csv` & `data/processed/clean_festivals.parquet`)

| Column | Data Type | Description | Source | Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `date` | string / date | Calendar date of festival event | Indian Calendar | `YYYY-MM-DD` | `2025-10-21` |
| `festival_name` | string | Name of celebration or national holiday | Calendar | Supports multiple fests per day (e.g. `Ambedkar Jayanti / Baisakhi`) | `Diwali` |
| `festival_type` | string | Scope or category of festival | Cultural Data | `National`, `Religious`, `Regional`, `Cultural` | `Religious` |
| `is_festival` | integer | Indicator whether date is a festival | Calendar | `0` or `1` | `1` |
| `festival_intensity`| float | Relative commercial demand impact scale | Market Research | `0.0` to `1.0` | `1.0` |

---

### F. Weather (`data/raw/weather.csv` & `data/processed/clean_weather.parquet`)

| Column | Data Type | Description | Source | Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `date` | string / date | Observation date | Meteorology | `YYYY-MM-DD` | `2025-10-01` |
| `city` | string | Observation city location | Meteorology | City name | `Noida` |
| `temperature` | float | Daily ambient temperature in Celsius | Sensor / API | `-10.0` to `55.0` | `28.4` |
| `humidity` | float | Relative atmospheric humidity percentage | Sensor / API | `0.0` to `100.0` | `50.3` |
| `rainfall` | float | Precipitation in millimeters | Sensor / API | `>= 0.0` | `1.8` |
| `weather_condition`| string | Textual weather synopsis | Weather model | `Clear`, `Partly Cloudy`, `Rainy`, `Hot`, `Cool` | `Clear` |

---

## 2. Feature Store Datasets (`data/features/`)

### A. Transaction Features (`transaction_features.parquet`)

Combines cleaned transactions with calculated financial amounts, temporal features, festival context, and local weather.

* `total_amount` (float): Gross transaction sum (`quantity * unit_price`).
* `discount_amount` (float): Exact discount amount applied.
* `net_amount` (float): Final collected revenue (`total_amount - discount_amount`).
* `date` (string): Calendar date (`YYYY-MM-DD`).
* `day` (integer): Day of month (1-31).
* `day_of_week` (integer): 0=Monday to 6=Sunday.
* `day_name` (string): Full name of the day (`Wednesday`).
* `hour` (integer): Hour of transaction (0-23).
* `week` (integer): ISO calendar week number (1-53).
* `month` (integer): Calendar month (1-12).
* `quarter` (integer): Financial quarter (1-4).
* `year` (integer): Calendar year (e.g. 2025, 2026).
* `is_weekend` (integer): Binary flag (1 if Saturday or Sunday, else 0).
* `is_month_start` (integer): 1 if 1st day of month, else 0.
* `is_month_end` (integer): 1 if final day of month, else 0.
* `festival_name` (string): Merged festival name for date, or `"None"`.
* `festival_type` (string): Category of festival, or `"None"`.
* `is_festival` (integer): 1 if festival date, else 0.
* `festival_intensity` (float): Intensity score (0.0 to 1.0).
* `days_to_festival` (integer): Calendar days to the closest upcoming festival.
* `days_after_festival` (integer): Calendar days elapsed since the closest past festival.
* `temperature` (float): Ambient local temperature (°C).
* `humidity` (float): Ambient local humidity (%).
* `rainfall` (float): Local rainfall precipitation (mm).
* `weather_condition` (string): Weather state (`Clear`, `Rainy`, etc.).
* `is_rainy` (integer): 1 if rainfall > 0.0 or condition is Rainy, else 0.

---

### B. Merchant Features (`merchant_features.parquet`)

Merchant-level performance aggregations.

* `merchant_id` (string): Unique identifier.
* `merchant_name` (string): Business title.
* `business_type` (string): Category (`Bakery`, `Cafe`, `Electronics`, etc.).
* `city`, `state`, `pincode`, `latitude`, `longitude`: Geospatial attributes.
* `merchant_total_revenue` (float): Total lifetime net sales revenue (₹).
* `merchant_total_orders` (integer): Total lifetime orders processed.
* `average_order_value` (float): Average net spend per order (`revenue / orders`).
* `unique_customers` (integer): Distinct customers who made purchases.
* `unique_products` (integer): Distinct SKUs sold.
* `active_days` (integer): Number of distinct calendar days with transactions.
* `revenue_per_day` (float): Average daily net sales revenue (`revenue / active_days`).
* `orders_per_day` (float): Average daily order transaction count (`orders / active_days`).

---

### C. Customer Features (`customer_features.parquet`)

Customer-level RFM (Recency, Frequency, Monetary) analytics.

* `customer_id` (string): Unique customer ID.
* `customer_name`, `customer_type`, `city`, `signup_date`: Profile metadata.
* `customer_total_spend` (float): Cumulative net spending across all transactions (₹).
* `customer_order_count` (integer): Total lifetime orders placed.
* `customer_average_order_value` (float): Mean net transaction amount (₹).
* `customer_recency` (float): Number of days since customer's last purchase.
* `customer_purchase_frequency` (float): Average purchase frequency normalized to 30-day window.
* `customer_first_purchase` (string): ISO timestamp of first recorded transaction.
* `customer_last_purchase` (string): ISO timestamp of most recent transaction.

---

### D. Product Features (`product_features.parquet`)

Catalog SKU-level demand and sales metrics.

* `product_id` (string): SKU identifier.
* `product_name`, `product_category`, `unit_cost`, `selling_price`: Catalog metadata.
* `product_sales` (integer): Cumulative physical units sold.
* `product_revenue` (float): Cumulative net sales revenue (₹).
* `product_order_count` (integer): Number of transaction orders containing this SKU.
* `unique_customers` (integer): Distinct customer count who purchased this SKU.
* `average_quantity` (float): Mean units bought per order.
* `average_selling_price` (float): Effective realized selling price (`net_revenue / product_sales`).

---

### E. Daily Aggregated Features (`daily_features.parquet`)

Temporal time-window features across calendar days.

* `date` (string): Calendar date (`YYYY-MM-DD`).
* `daily_total_revenue` (float): Sum of all transactions net revenue for that day.
* `daily_total_orders` (integer): Number of transactions occurring on that day.
* `daily_total_units` (integer): Total physical units sold across all merchants.
* `daily_active_merchants` (integer): Count of distinct active merchants.
* `daily_active_customers` (integer): Count of distinct active customers.
* `daily_avg_order_value` (float): Average net spend per order on that date.
* `is_festival`, `festival_intensity`, `days_to_festival`, `days_after_festival`: Festival timeline metrics.
* `avg_temperature`, `avg_humidity`, `total_rainfall`, `is_rainy_day`: Day's meteorological conditions.
* `day_of_week`, `day_name`, `day_of_month`, `week_of_year`, `month`, `quarter`, `year`: Calendar breakdown.
* `is_weekend`, `is_month_start`, `is_month_end`: Calendar flags.
* `lag_1d_revenue` (float): Previous day's revenue (`shift(1)`), strictly historical.
* `lag_7d_revenue` (float): Same-day previous week revenue (`shift(7)`).
* `rolling_7d_avg_revenue` (float): 7-day trailing moving average calculated exclusively using past observations (`shift(1).rolling(7)`).

---

## 3. Data Leakage Protection Framework

For future Phase 3 time-series forecasting and ML models, strict boundaries must separate available features from target/future information.

### What is Available at Prediction Time ($T$)?
1. **Calendar & Astronomical attributes**: Day of week, month, year, weekend flags, month start/end.
2. **Upcoming Festival Calendar**: `days_to_festival`, `is_festival` (the calendar date is known in advance).
3. **Historical / Trailing Aggregations**:
   - Lagged revenues: `lag_1d_revenue`, `lag_7d_revenue`.
   - Trailing rolling averages: `rolling_7d_avg_revenue` (strictly using observations prior to $T$).
   - Merchant / Customer cumulative metrics calculated up to $T - 1$.
4. **Weather Forecasts**: Near-term temperature, humidity, rainfall forecast.

### What is NOT Available at Prediction Time ($T$)?
1. **Contemporaneous / Future Transaction Data**: Net amount, order count, or unit sales of day $T$ or future days.
2. **Post-event Metrics**: `customer_recency` or customer spend computed using future transactions.
3. **Centered or Future Moving Averages**: Rolling windows that span $(T - k, T + k)$. All rolling metrics must use strict trailing offsets (`shift(1)`).
