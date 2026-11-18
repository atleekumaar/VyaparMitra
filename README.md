# 🛍️ VyaparMitra (व्यापारमित्र) — MerchantOS
### *Intelligence-Led Retail Operating System for Digitally-Enabled Indian Merchants*

[![Live Application](https://img.shields.io/badge/Live%20Application-vyaparmitra--xdy9.onrender.com-00BAF2?style=for-the-badge&logo=render&logoColor=white)](https://vyaparmitra-xdy9.onrender.com/)
[![API Swagger Docs](https://img.shields.io/badge/Swagger%20Docs-Live%20API-002970?style=for-the-badge&logo=fastapi&logoColor=white)](https://vyaparmitra-xdy9.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6.svg)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg)](https://tailwindcss.com/)
[![Security](https://img.shields.io/badge/Security-RBAC%20%2B%20JWT%20Isolated-success.svg)](#4-security-authentication--multi-tenancy)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

> 🌐 **Live Web Application:** [https://vyaparmitra-xdy9.onrender.com/](https://vyaparmitra-xdy9.onrender.com/)  
> 📖 **Interactive API Documentation:** [https://vyaparmitra-xdy9.onrender.com/docs](https://vyaparmitra-xdy9.onrender.com/docs)  
> 🎬 **Official Launch Video:** [`brag-output/brag.mp4`](brag-output/brag.mp4) (Full HD, 20s Launch Demo)  
> 📂 **Sample Datasets for Testing:** [`sample_csvs/`](sample_csvs/) (Inventory, Customers, Sales)

---

## 📌 1. Executive Summary & Problem-Solution Fit

India is home to over **60 million micro, small, and medium retail merchants** (Kirana stores, general provision stores, pharmacies, electronics shops). Despite widespread digital payment adoption via UPI, day-to-day store operations remain fragmented:
- **Loose Paper Diaries (उधार बहीखाता):** Unrecorded customer debt, forgotten credit balances, and slow manual debt recovery.
- **Stockout Guesswork:** Overstocking slow-moving SKUs while popular staples run out during peak weekend rushes and regional festivals.
- **Billing Friction:** Slow calculator-based checkout queues leading to cart abandonment.
- **Disconnected Supply Chains:** Manual phone orders to distributors with zero visibility into purchase price variations.

**VyaparMitra (MerchantOS)** replaces manual paper ledgers with an integrated, intelligence-led operating system designed around a closed-loop execution model:

$$\textbf{UNDERSTAND} \longrightarrow \textbf{DECIDE} \longrightarrow \textbf{ACT}$$

1. **UNDERSTAND:** Ingests live counter sales, barcode scans, customer Khata balances, and stock velocity into real-time operational ledgers and hyperlocal demand models.
2. **DECIDE:** An autonomous, zero-hallucination AI Copilot and statistical engine detects low stock, calculates 7-day demand spikes (incorporating festival calendars), and prepares draft procurement orders.
3. **ACT:** Multi-tier role-based approvals enforce strict operational control. Owners approve purchase orders, managers record physical goods receipt, and automated WhatsApp balance links recover customer credit.

---

## 🏗️ 2. System Architecture & Tech Stack

The platform is structured as a production-grade monorepo combining a high-performance Python ASGI backend and a modern React client:

```
vyaparmitra/
├── frontend/                     # React 19 + TypeScript SPA
│   ├── src/
│   │   ├── api/client.ts         # Axios API client with automatic JWT injection & 401 redirection
│   │   ├── components/           # Reusable UI primitives (Modals, Badges, Soundbox, Thermal Receipt)
│   │   ├── pages/                # LandingPage, Dashboard, Products, Sales POS, Customers Khata, Copilot
│   │   └── types/                # Canonical TypeScript interfaces matching backend models
│   ├── public/                   # Static assets, launch video, and 1-click sample CSV downloads
│   └── package.json
├── src/                          # FastAPI Backend & Intelligence Core
│   ├── api/                      # REST API routing, authentication, and database session management
│   │   ├── auth.py               # Canonical 3-tier RBAC (OWNER, MANAGER, STAFF) & JWT validation
│   │   ├── db.py                 # SQLite WAL mode connection pooling, indexing, and migrations
│   │   ├── routes/               # Domain routers (auth, inventory, sales, customers, copilot, import, health)
│   │   └── services/             # Business services (ProductService, CustomerService, EmailService)
│   ├── copilot/                  # Autonomous agent orchestration, L3 drafts, and approval execution
│   ├── analytics/                # Real-time transaction aggregation and financial metrics
│   ├── ml/                       # Scikit-learn demand forecasting & festival trend analysis
│   └── recommendations/          # Deterministic reorder prioritization engine
├── sample_csvs/                  # Ready-to-import Kirana datasets (Inventory, Customers, Sales)
├── brag-output/                  # Official launch video deliverables (brag.mp4, poster, share copy)
├── tests/                        # Automated unit, integration, RBAC, and concurrency test suites
├── render.yaml                   # Infrastructure-as-code Render deployment blueprint
└── Dockerfile                    # Multi-stage production container
```

### Core Technologies
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+), [Pydantic v2](https://docs.pydantic.dev/), SQLite 3 in WAL mode with Foreign Keys enabled.
- **Frontend:** [React 19](https://react.dev/), [TypeScript 5.5](https://www.typescriptlang.org/), [Vite 6](https://vitejs.dev/), [Tailwind CSS v4](https://tailwindcss.com/), [Lucide React](https://lucide.dev/).
- **AI & Forecasting:** Groq LPU (`llama-3.3-70b-versatile` / `qwen-2.5-32b`) with deterministic rule-based fallback, Scikit-learn demand regressors.
- **Security & Communications:** HMAC-SHA256 JWT tokens, bcrypt password hashing, Brevo transactional email/SMS OTP delivery.

---

## ⚡ 3. Key Functional Modules

### 1. Business Command Center (`/dashboard`)
- **Live Revenue & Ticket Size:** Real-time calculation of gross revenue, average transaction value, and payment method distribution (UPI, Cash, Card).
- **Cold-Start Warmup Architecture:** A static, high-speed landing page with background health checks (`/api/health`) eliminates spin-down latency on cloud hosting.
- **Quick Action Bar:** 1-click modals for recording counter sales, adding new catalog SKUs, and bulk CSV ingestion.

### 2. Point of Sale (POS) & Voice Soundbox (`/sales`)
- **3-Second Checkout:** Instant SKU barcode lookup, quantity adjustments, and custom discounts.
- **Smart Soundbox Simulation:** Integrated audio alert engine confirming incoming payments in English and Hindi (*"₹193.00 Prapt Hue"*).
- **Thermal Slip Generation:** Instant printable receipt formatting compatible with 58mm/80mm thermal receipt printers.

### 3. Digital Customer Khata (`/customers`)
- **Ledger Balance Tracking:** Real-time customer balance calculation (credit vs. debit ledger).
- **Credit Limit Guards:** Prevents opening new debt lines if a customer exceeds their configured credit limit.
- **1-Click WhatsApp Collection:** Generates pre-filled WhatsApp payment reminders containing direct UPI payment links.

### 4. Inventory & Catalog Management (`/products`)
- **Real-Time Stock Depletion:** Stock decrements automatically upon counter sale completion.
- **Low-Stock Alerts:** Color-coded status chips (`STAR`, `FOCUS`, `MONITOR`) highlighting reorder urgency.
- **Multi-Branch Isolation:** Ensures stock levels and catalog items are cleanly separated across multiple physical store locations.

### 5. AI Copilot & Two-Step Procurement (`/copilot`, `/approvals`)
To prevent unauthorized purchases and ensure strict inventory accounting:
1. **L3 Reorder Proposal:** The AI Copilot detects low-stock items and creates a reorder proposal with status `PENDING_APPROVAL`.
2. **Owner Authorization:** Only users with the `OWNER` role can approve the proposal, generating a formal Purchase Order (`PO-XXXX`). **Physical stock does not increase at this step.**
3. **Goods Receipt Inward:** When stock physically arrives at the store, an `OWNER` or `MANAGER` executes Goods Receipt (`POST /api/copilot/approvals/{id}/receive-goods`), which formally increments inventory and logs an immutable audit entry.

---

## 🔒 4. Security, Authentication & Multi-Tenancy

Security is enforced at the backend routing and dependency injection layer, never relying purely on frontend visual gating.

### A. Zero-Bypass JWT Authentication
- All operational routes (`/api/inventory`, `/api/sales`, `/api/customer-ops`, `/api/audit-logs`, `/api/copilot/approvals`) mandate a valid `Authorization: Bearer <token>` header.
- Insecure parameter bypasses (such as `X-Merchant-Id` headers or `?merchant_id=` query parameters) are strictly rejected. Requests without a valid cryptographic JWT receive `401 Unauthorized`.
- **Production Startup Guard:** In `ENVIRONMENT=production`, the application refuses to start if `JWT_SECRET_KEY` is missing, default, or less than 32 characters in length.

### B. Role-Based Access Control (RBAC)
MerchantOS enforces exactly three canonical business roles:

| Role | Scope & Permissions | Enforced Restrictions |
|---|---|---|
| **OWNER** | Full administrative and business control across all store branches. Can manage users, view complete P&L analytics, access audit logs, and approve high-value procurement orders. | *None* |
| **MANAGER** | Daily store management. Can manage inventory, receive physical goods deliveries, register customers, initiate purchase drafts, and record sales within their assigned branch. | Cannot create Owners or Managers. Cannot approve high-value POs. Cannot view cross-store financial records or audit logs. |
| **STAFF** | Point of Sale (POS) billing and counter operations only. Can record retail sales, look up product SKUs, and register new walk-in customers. | Cannot import CSVs. Cannot adjust stock manually. Cannot create users. Cannot view financial reports or audit logs. Cannot approve or reject agent requests. |

*Legacy role aliases (`admin`, `supervisor`) are automatically normalized to `owner` and `manager` during token validation without disrupting existing accounts.*

### C. Tenant & Multi-Branch Isolation
- Every database query strictly filters by `WHERE business_id = ?`.
- Cross-tenant access attempts immediately return `403 Forbidden` (`"Cross-tenant access prohibited. You cannot query or modify another merchant's data."`).
- Manager and Staff permissions are automatically scoped to their designated `branch_id`.

---

## 📥 5. Bulk CSV Ingestion Engine

The `POST /api/import/csv` endpoint allows merchants to onboard existing catalogs and customer lists in seconds.

### Parsing Resilience for Indian Retail Formats
Real-world Kirana spreadsheets contain unique formatting that standard CSV parsers fail on. VyaparMitra handles:
- **Currency Symbols & Suffixes:** Strips `₹`, `Rs.`, `INR`, and trailing `/-` (e.g., `₹ 1,250.00` and `Rs. 45/-` parse cleanly to floats).
- **Thousands Separators:** Handles quoted numbers with commas (`"1,250.00"` → `1250.0`).
- **Units in Stock Quantities:** Strips measurement units (e.g., `25 bags`, `10 pcs`, `50 pkts` → `25`, `10`, `50`).
- **Header Synonym Mapping:** Recognizes diverse column aliases (`Item Name`, `Particulars`, `Rate`, `MRP`, `Cost Price`, `Qty`, `Closing Stock`, `Mobile`).
- **Transparent Reporting:** The UI displays a detailed summary (Total, Imported, Skipped) with an expandable row-by-row error inspector.

### Pre-Packaged Sample Datasets
The repository includes three pre-formatted sample files in [`sample_csvs/`](sample_csvs/) (also downloadable directly from the web app's CSV import modal):
1. **[`sample_inventory.csv`](sample_csvs/sample_inventory.csv):** 21 popular Kirana items (Tata Salt, Fortune Oil, Aashirvaad Atta, Amul Butter, Maggi, Parle-G, Dettol Soap, etc.).
2. **[`sample_customers.csv`](sample_csvs/sample_customers.csv):** 10 verified customer contacts with phone numbers and credit limits.
3. **[`sample_sales.csv`](sample_csvs/sample_sales.csv):** 15 retail sales transactions across UPI, Cash, and Card.

---

## ⚙️ 6. Environment Variables Reference

| Variable | Required in Production | Default / Example | Purpose |
|---|---|---|---|
| `ENVIRONMENT` | Yes | `production` | Enables strict production security guards. |
| `JWT_SECRET_KEY` | Yes | `32+ char random string` | Signing secret for cryptographic HMAC-SHA256 JWT tokens. |
| `DEMO_MODE` | Yes | `false` | When `false`, disables default demo users and enforces real OTP authentication. |
| `DATABASE_URL` | No | `sqlite:///data/vyaparmitra.db` | Operational database connection string. |
| `GROQ_API_KEY` | Optional | `gsk_...` | Groq LPU inference key for natural language Copilot chat. |
| `BREVO_API_KEY` | Optional | `xkeysib-...` | Brevo API key for transactional email OTP delivery. |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins for API communication. |

---

## 🚀 7. Local Development Setup

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/atleekumaar/VyaparMitra.git
cd VyaparMitra

# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database schema and indexes
python -c "from src.api.db import init_db; init_db()"

# Start FastAPI development server
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
The API will be available at `http://127.0.0.1:8000` with Swagger documentation at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
The React frontend will be live at `http://localhost:5173`.

---

## ☁️ 8. Production Deployment & Persistent Storage (Render)

The application is deployed using Render's Infrastructure-as-Code blueprint (`render.yaml`).

### Persistent Disk Configuration
Because standard Render web services run on ephemeral containers, local SQLite data would reset on redeployment unless mounted to a persistent disk:
1. In the **Render Dashboard**, open the Web Service (`vyaparmitra-xdy9`).
2. Navigate to **Disks** → Click **Add Disk**.
3. Configure the persistent mount:
   - **Name:** `vyaparmitra-db-data`
   - **Mount Path:** `/var/data`
   - **Size:** `1 GB` (or larger)
4. Set the environment variable:
   - `DATABASE_URL` = `sqlite:////var/data/vyaparmitra.db`
5. Save changes and trigger a deployment.

---

## 🧪 9. Quality Assurance & Testing

Run the automated test suite:
```bash
# Run security, RBAC, and isolation tests
pytest tests/test_backend_auth_rbac.py tests/test_negative_security_and_isolation.py -v

# Run CSV import validation (including Indian currency & unit parser tests)
pytest tests/test_backend_import_csv.py -v

# Run concurrency and rate-limiting tests
pytest tests/test_concurrency_and_ratelimit.py -v

# Run procurement and approval workflow tests
pytest tests/test_live_agent_approval_workflow.py -v
```

---

## 📄 License
This project is open-source software licensed under the [MIT License](LICENSE).
