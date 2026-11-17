# 🛍️ VyaparMitra (व्यापारमित्र) — MerchantOS
### *Intelligence-Led Operating System for Digitally-Enabled Indian Retail Merchants*

[![Live Application](https://img.shields.io/badge/Live%20Application-vyaparmitra--xdy9.onrender.com-00BAF2?style=for-the-badge&logo=render&logoColor=white)](https://vyaparmitra-xdy9.onrender.com/)
[![API Swagger Docs](https://img.shields.io/badge/Swagger%20Docs-Live%20API-002970?style=for-the-badge&logo=fastapi&logoColor=white)](https://vyaparmitra-xdy9.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6.svg)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-248%20Passed-00B970.svg)](tests/)
[![Security](https://img.shields.io/badge/Security-RBAC%20%2B%20JWT%20Isolated-success.svg)](#-security--authentication-architecture)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

> 🚀 **Live Production URL:** [https://vyaparmitra-xdy9.onrender.com/](https://vyaparmitra-xdy9.onrender.com/)  
> 📖 **Interactive API Swagger Docs:** [https://vyaparmitra-xdy9.onrender.com/docs](https://vyaparmitra-xdy9.onrender.com/docs)

---

## 📌 1. Product Overview & Core Promise

**VyaparMitra (MerchantOS)** is an intelligence-led retail operating system built for India's 60M+ local retail merchants (kirana stores, pharmacies, electronics, and general trade). 

### Core Product Flywheel:
$$\textbf{UNDERSTAND} \longrightarrow \textbf{DECIDE} \longrightarrow \textbf{ACT}$$

- **UNDERSTAND:** Aggregates POS billing, Khata credit, customer purchase patterns, and stock movements into real-time metrics, ML sales forecasts, and hyperlocal benchmarks.
- **DECIDE:** Intelligent Copilot AI agents run autonomous analyses to propose stock reorders, dynamic pricing, churn prevention alerts, and cash flow actions.
- **ACT:** Closed-loop human-in-the-loop approval workflows. An Owner or Manager reviews and approves purchase orders, records goods inward receipts, and settles Khata ledgers with full audit trails.

---

## 🏗️ 2. Architecture & Technology Stack

The system is architected as a lightweight, high-performance monorepo:

```
vyaparmitra/
├── frontend/                     # Modern React SPA
│   ├── src/
│   │   ├── api/client.ts         # Centralized API client with JWT & 401 interception
│   │   ├── components/           # UI components, layout, soundbox alerts
│   │   ├── pages/                # Dashboard, Products, Sales POS, Customers Khata, Copilot
│   │   └── types/                # Strict TypeScript domain interfaces
│   └── package.json
├── src/                          # FastAPI Backend & Intelligence Core
│   ├── analytics/                # Sales, customer RFM, payment & product analytics
│   ├── api/                      # REST API routing, auth, config, and middleware
│   │   ├── auth.py               # Canonical RBAC (OWNER, MANAGER, STAFF) & JWT validation
│   │   ├── db.py                 # SQLite WAL persistence, schema migrations, and indexing
│   │   ├── routes/               # Modular API routers (sales, inventory, copilot, etc.)
│   │   └── services/             # Business services (ProductService, CustomerService, EmailService)
│   ├── copilot/                  # Autonomous agents, L3 draft generation & approval tools
│   ├── features/                 # Parquet feature stores & contextual aggregations
│   ├── ml/                       # Scikit-learn demand forecasting & inference predictors
│   └── recommendations/          # Deterministic prioritization & action engine
├── data/                         # Parquet feature store & operational SQLite database
├── tests/                        # 248 Automated unit, integration, and security tests
├── render.yaml                   # Production Render blueprint configuration
└── Dockerfile                    # Multi-stage production container
```

### Technology Highlights:
- **Backend:** FastAPI (Python 3.12+), Pydantic v2, SQLite in WAL mode with Foreign Keys enabled.
- **Frontend:** React 19, TypeScript 5.5, Vite 6, TailwindCSS v4, Lucide Icons.
- **Intelligence & ML:** Scikit-learn regressors, Pandas/PyArrow Parquet feature stores, Groq LPU (`llama-3.3-70b-versatile` / `qwen-2.5-32b`) with zero-hallucination deterministic fallbacks.
- **Auth & Security:** HMAC-SHA256 JWT tokens, bcrypt password hashing, constant-time comparisons, branch-isolated tenant enforcement.

---

## 🔒 3. Security & Authentication Architecture

Security is enforced at the backend middleware and dependency injection layer, never relying solely on frontend UI visibility.

### A. Strict JWT Authentication
- **Zero-Bypass Enforcement:** All operational endpoints (`/api/inventory`, `/api/sales`, `/api/customer-ops`, `/api/audit-logs`, `/api/copilot/approvals`) strictly require an `Authorization: Bearer <token>` header.
- **Header & Query Param Neutralization:** Deprecated or insecure mechanisms (e.g. `X-Merchant-Id` or `?merchant_id=...` parameter bypasses) are completely removed. Requests without a valid cryptographic JWT receive `401 Unauthorized`.
- **Production Startup Hardening:** If `ENVIRONMENT=production`, the application refuses to start if `JWT_SECRET_KEY` is missing, default, or less than 32 characters in length.
- **Session Termination (Logout):** The frontend `clearAuthSession()` method purges tokens, cached merchant IDs, and user profiles from `localStorage`, and the global 401 axios interceptor immediately redirects to `/login`.

### B. Role-Based Access Control (RBAC)
MerchantOS enforces exactly three canonical business roles:

| Role | Permissions & Operational Scope | Restricted Endpoints |
|---|---|---|
| **OWNER** | Full administrative and business control. Can view all branches, manage users/roles, view audit logs, access finance & P&L summaries, and approve high-value L3 agent drafts / Purchase Orders. | *None* |
| **MANAGER** | Store operational management. Can manage inventory, inward goods (Goods Receipt), initiate purchase drafts, register customers, and record counter sales. Restricted to assigned branch. | Cannot create Owners or Managers. Cannot approve high-value purchase drafts. Cannot view cross-store audit logs or sensitive business finance records. |
| **STAFF** | Point of Sale (POS) and counter operations only. Can record retail counter sales, perform product SKU lookups, and register new customer contacts. | Cannot import CSVs. Cannot adjust stock manually. Cannot create users. Cannot view financial reports or audit logs. Cannot approve or reject agent requests. |

*Legacy aliases (`admin`, `supervisor`) are automatically normalized to `owner` and `manager` respectively on token validation without breaking legacy accounts.*

### C. Tenant & Branch Isolation
- Every operational database query filters by `WHERE business_id = ?`.
- Attempting to pass another merchant's ID via query parameters or headers triggers an immediate `403 Forbidden` response: `Cross-tenant access prohibited. You cannot query or modify another merchant's data.`
- Staff and Manager queries are automatically constrained to their assigned `branch_id`.

---

## 💾 4. Database & Persistence Runbook

### Engine & Storage
- **Production Engine:** SQLite 3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`), synchronous normal (`PRAGMA synchronous=NORMAL;`), and enforced foreign keys (`PRAGMA foreign_keys=ON;`).
- **Database Path:** Configured via `DATABASE_URL` (default: `sqlite:///data/vyaparmitra.db`).

### Git Tracking & Secret Hygiene
- Operational database files (`*.db`, `*.db-wal`, `*.db-shm`) and secrets are explicitly ignored in `.gitignore` and untracked from Git history to prevent data leakage.
- `init_db()` is idempotent: it runs `CREATE TABLE IF NOT EXISTS` and applies non-destructive column migrations without resetting existing merchant records.

### Render Persistent Disk Mount Configuration
By default, Render web services run on ephemeral filesystems. Redeploying or restarting the container will destroy local SQLite data unless a persistent disk is configured.

To configure persistent storage on Render:
1. In the **Render Dashboard**, open your Web Service (`vyaparmitra-xdy9`).
2. Navigate to **Disks** → Click **Add Disk**.
3. Configure the disk:
   - **Name:** `vyaparmitra-db-data`
   - **Mount Path:** `/var/data`
   - **Size:** `1 GB` (or larger depending on merchant scale).
4. Update **Environment Variables** in Render:
   - `DATABASE_URL` = `sqlite:////var/data/vyaparmitra.db`
5. Click **Save Changes** and deploy.

> ⚠️ **Important Migration Note for Horizontal Scaling:**  
> SQLite is suitable for single-instance MVPs. When scaling beyond 1 web container or onboarding high-concurrency paying merchants, migrate `DATABASE_URL` to a managed PostgreSQL cluster (e.g. Render Managed Postgres).

---

## 📥 5. Bulk CSV Ingestion Specifications

The `POST /api/import/csv` endpoint enables high-throughput data migration for onboarding existing kirana stores.

### Constraints & Guards:
- **Maximum File Size:** `5 MB` (Files exceeding 5MB are rejected with `400 Bad Request`).
- **Allowed File Format:** `.csv` only.
- **Allowed Roles:** `OWNER` or `MANAGER` (Staff requests return `403 Forbidden`).
- **Entity Type Matching:** The endpoint inspects headers and rejects mismatched files (e.g., uploading customer headers to `entity_type=inventory` returns `400 Bad Request`).

### Entity Schemas & Required Headers:

#### 1. Inventory (`entity_type=inventory`)
- **Required Columns:** `product_name`, `selling_price`
- **Optional Columns:** `product_id`, `category`, `current_stock`, `min_stock_threshold`, `unit_cost`
- **Validation Rules:** `selling_price > 0`, `unit_cost >= 0`, `current_stock >= 0`.
- **Example CSV:**
  ```csv
  product_id,product_name,category,current_stock,unit_cost,selling_price
  SKU_ATT_10K,Aashirvaad Atta 10kg,Flours,25,380.00,430.00
  SKU_OIL_1L,Fortune Sunflower Oil 1L,Oils,40,110.00,135.00
  ```

#### 2. Customers (`entity_type=customers`)
- **Required Columns:** `name`
- **Optional Columns:** `phone`, `email`, `city`, `credit_limit`
- **Validation Rules:** `credit_limit >= 0`. Deduplicates on phone/name.
- **Example CSV:**
  ```csv
  name,phone,email,city,credit_limit
  Ramesh Verma,+919876543210,ramesh@example.com,Lucknow,5000.00
  Pooja Sharma,+919876543219,pooja@example.com,Kanpur,10000.00
  ```

#### 3. Sales (`entity_type=sales`)
- **Required Columns:** `product_id`, `quantity`
- **Optional Columns:** `payment_method` (`CASH`, `UPI`, `CARD`, `CREDIT`), `customer_id`, `unit_price`, `sale_date`
- **Validation Rules:** `quantity > 0` (integer). The `product_id` **must exist** in the merchant's active inventory. Sales for non-existent SKUs are rejected with row errors and **never** auto-create phantom inventory items. Sufficient inventory stock is verified before decrementing.
- **Example CSV:**
  ```csv
  product_id,quantity,payment_method
  SKU_ATT_10K,2,UPI
  SKU_OIL_1L,1,CASH
  ```

---

## ⚡ 6. Two-Step Procurement Workflow

To maintain absolute accounting integrity:
1. **Purchase Reorder Draft (L3):** Triggered by AI copilot or merchant request when stock drops below threshold. Status: `PENDING_APPROVAL`.
2. **Owner Approval (`POST /api/copilot/approvals/{id}/approve`):** Generates an official Purchase Order (`PO-XXXX`) and transitions state to `APPROVED`. **Physical stock does NOT increase at this step.**
3. **Goods Receipt (`POST /api/copilot/approvals/{id}/receive-goods`):** Executed by Owner or Manager upon physical stock delivery. Verifies PO, transitions status to `GOODS_RECEIVED`, updates live inventory stock, and appends a security audit entry.

---

## ⚙️ 7. Environment Variables Reference

| Variable | Required in Production | Default / Example | Purpose |
|---|---|---|---|
| `ENVIRONMENT` | Yes | `production` | Enables strict security guards (halts startup if secrets are weak). |
| `JWT_SECRET_KEY` | Yes | `min-32-char-random-string` | Cryptographic secret for signing JWT auth tokens. |
| `DEMO_MODE` | Yes | `false` | When `false`, disables seed credentials and default demo users. |
| `DATABASE_URL` | No | `sqlite:///data/vyaparmitra.db` | Operational database connection string. |
| `GROQ_API_KEY` | Optional | `gsk_...` | Enables Groq LPU inference for natural language Copilot chat. |
| `BREVO_API_KEY` | Optional | `xkeysib-...` | Enables transactional email OTP delivery via Brevo. |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins for frontend-backend communication. |

---

## 🚀 8. Local Development Setup

### Prerequisites:
- Python 3.12 or higher
- Node.js 18 or higher & npm

### Backend Setup:
```bash
# Clone the repository
git clone https://github.com/atleekumaar/VyaparMitra.git
cd VyaparMitra

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations and seed
python -c "from src.api.db import init_db; init_db()"

# Start FastAPI development server
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
API will be live at `http://127.0.0.1:8000` with Swagger docs at `/docs`.

### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```
Frontend will be live at `http://localhost:5173`.

---

## 🧪 9. Quality Assurance & Test Execution

Run the complete test suite:
```bash
# Run all tests
pytest -q

# Run specific security & RBAC tests
pytest tests/test_backend_auth_rbac.py tests/test_negative_security_and_isolation.py -v

# Run targeted procurement workflow test
pytest tests/test_live_agent_approval_workflow.py -v
```

Current test status: **248 passed, 0 failed (100% pass rate)**.

---

## 📄 License
Distributed under the **MIT License**.
