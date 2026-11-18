# Sample CSV Datasets for VyaparMitra / MerchantOS

This folder contains pre-formatted, production-ready sample CSV files designed for testing and populating a new or existing merchant store in VyaparMitra.

## Available Files

### 1. `sample_inventory.csv` (21 Popular Kirana Items)
- **Target Entity:** `Inventory / SKUs`
- **Columns:**
  - `product_id` (Unique SKU, e.g., `PRD_TATA_SALT`)
  - `product_name` (Item title, e.g., `Tata Salt 1kg`)
  - `category` (e.g., `Groceries`, `Dairy`, `Staples`, `Snacks & Bakery`, etc.)
  - `selling_price` (Retail price in ₹)
  - `unit_cost` (Purchase cost in ₹)
  - `current_stock` (Stock units on hand)
  - `min_stock_threshold` (Low-stock reorder alert level)
  - `barcode` (13-digit EAN/UPC barcode)
  - `unit` (e.g., `pkt`, `btl`, `bag`, `pcs`, `jar`)

### 2. `sample_customers.csv` (10 Verified Retail Customers)
- **Target Entity:** `Customers`
- **Columns:**
  - `name` (Full customer name)
  - `phone` (Contact number with +91)
  - `email` (Customer email)
  - `address` (Store local area/street)
  - `city` (City name)
  - `credit_limit` (Khata credit limit in ₹)

### 3. `sample_sales.csv` (15 Retail Sales Transactions)
- **Target Entity:** `Sales Records`
- **Note:** Import `sample_inventory.csv` first so the catalog items exist before importing historical sales.
- **Columns:**
  - `product_id` (Matching catalog SKU)
  - `product_name` (Item name)
  - `quantity` (Units sold)
  - `unit_price` (Sale rate in ₹)
  - `payment_method` (`UPI`, `CASH`, `CARD`)
  - `customer_name` (Customer or `Walk-in Customer`)
  - `discount` (Discount in ₹)

## How to Import
1. Log in to your VyaparMitra store dashboard (`/dashboard` or `/products` or `/customers`).
2. Click the **Import CSV** button.
3. Select the matching tab (`Inventory / SKUs`, `Customers`, or `Sales Records`).
4. Upload the corresponding sample CSV file.
5. Review the instant confirmation report displaying imported vs. skipped row counts.
