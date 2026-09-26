# 🛍️ VyaparMitra (व्यापारमित्र)
### *AI-Powered Business Intelligence & Multilingual Copilot for Retail Merchants*

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6.svg)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-173%20Passed-00B970.svg)](tests/)
[![Zero Hallucination](https://img.shields.io/badge/AI%20Copilot-Zero%20Hallucination-002970.svg)](#-multilingual-ai-copilot)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Overview

**VyaparMitra** is a complete, production-grade business operating system and conversational AI assistant built specifically for small and medium retail merchants across India. 

Operating a retail store comes with daily challenges: unpredictable seasonal demand, cash flow volatility, stockouts, customer churn, and lack of actionable insights. VyaparMitra converts raw transactional records into real-time visual analytics, machine learning forecasts, automated decision recommendations, and a conversational AI copilot that speaks the merchant's language (**Hindi**, **Hinglish**, and **English**).

---

## ✨ Key Features

### 📊 1. Real-Time Command Center & Dashboard
- **Instant Financial KPIs**: Track Gross Revenue, Completed Orders, Average Order Value (AOV), and Realized Discount Rates.
- **Paytm-Inspired Soundbox UI**: Custom fintech color scheme (`#002970` Navy, `#00BAF2` Cyan, `#00B970` Green), dark/light mode toggle, and live soundbox banner.
- **Dynamic Sales Trend Visualization**: Day-by-day and date-labeled sales bar charts with peak collection tracking.

### 🤖 2. Multilingual Conversational AI Copilot
- **100% Zero-Hallucination Architecture**: Strictly grounded in the merchant's underlying transactional feature store and peer benchmark data.
- **Native Hindi, Hinglish & English Support**: Query business data naturally (e.g. *"Kal kitni bikri hui thi?"*, *"Agle hafte kaunsa maal restock karein?"*, *"Meri dukaan dusron se kaisi hai?"*).
- **Daily Morning Audio/Text Briefs**: Instant summaries of yesterday's sales, urgent restock alerts, and top priority actions.

### 🏆 3. Peer Benchmarking Engine
- **Hyperlocal Comparison**: Compare performance against peer stores in the same city and category (e.g., *"Lucknow FMCG & Retail — Rank #4 of 9"*).
- **Metric-by-Metric Scorecards**: Percentile rankings for Revenue, Basket Size, Customer Retention, and Transaction Velocity against peer group medians.
- **"What Top Performers Do" Playbooks**: Actionable tactical playbooks derived from top-quartile merchant behaviors.

### ⚡ 4. Action Center & Decision Engine
- **Prioritized Recommendations**: AI-synthesized actions categorized across **Inventory Restock**, **Customer Retention**, **Cross-Sell Bundling**, and **Pricing Optimization**.
- **Audit-Ready Evidence**: Every recommendation displays the underlying metric indicators, historical benchmarks, and estimated revenue impact in Rupees.
- **Commercial Safety Guardrails**: Human-in-the-loop safeguards requiring merchant confirmation before execution.

### 🔮 5. Predictive Machine Learning & Demand Forecasting
- **7-Day Revenue Projections**: Autoregressive time-series forecasting with non-lookahead validation.
- **SKU-Level Demand Forecasting**: Projected unit demand rankings for top inventory items.
- **Customer Churn Risk Scoring**: RFM-based machine learning classifiers flagging at-risk patrons before they lapse.

### 📱 6. Multi-Channel Notifications & Outreach
- **WhatsApp & SMS Digests**: Integrated with Twilio to dispatch morning briefings, restock alerts, and customer re-engagement vouchers.

---

## 🏗️ Architecture & Data Flow

```text
  ┌────────────────────────────────────────────────────────┐
  │         Raw Ingested Data (CSV / Point-of-Sale)        │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │   Data Quality Validation, Cleaning & Quarantine Log   │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │  Feature Store & Analytics Pipeline (Parquet Storage)  │
  │  • Sales & Time Aggregations  • RFM Customer Segments  │
  │  • Product Pareto Matrix      • Festival & Weather Joins│
  └─────────────┬───────────────────────────┬──────────────┘
                │                           │
                ▼                           ▼
  ┌───────────────────────────┐ ┌──────────────────────────┐
  │  ML Predictive Engine     │ │  Benchmark & Action      │
  │  • 7-Day Revenue Forecast │ │  Recommendation Engine   │
  │  • SKU Demand Forecaster  │ │  • Priority Scoring      │
  │  • Churn Risk Classifier  │ │  • Evidence Packaging    │
  └─────────────┬─────────────┘ └───────────┬──────────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │            FastAPI Production Backend Layer            │
  │    • RESTful Endpoints   • Context Builder Engine      │
  │    • Multilingual Router • Grounded Response Validator │
  └───────────────────────────┬────────────────────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
  ┌───────────────────┐               ┌───────────────────┐
  │ React 19 Frontend │               │ WhatsApp & SMS    │
  │ Tailwind UI & i18n│               │ Automated Digests │
  └───────────────────┘               └───────────────────┘
```

---

## 📂 Project Structure

```text
VyaparMitra/
├── configs/                      # Pipeline and application configurations
├── data/                         # Data storage layers
│   ├── raw/                      # Ingested relational CSV tables
│   ├── processed/                # Normalized Parquet data
│   ├── features/                 # Merchant & customer feature store
│   ├── analytics/                # Pre-aggregated business analytical tables
│   ├── recommendations/          # Action plans, evidence records, summaries
│   ├── knowledge/                # Grounding business glossaries & FAQs
│   └── quality_reports/          # Data validation reports
├── docs/                         # System documentation
│   ├── data_dictionary.md        # Comprehensive data dictionary
│   ├── analytics_architecture.md # Analytics and schema guide
│   ├── recommendation_engine.md  # Recommendation framework
│   └── hindi_ai_copilot.md       # Copilot grounding specification
├── frontend/                     # React 19 + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── api/                  # Typed API client
│   │   ├── components/           # UI components (Navbar, Sidebar, MetricCard, Modal, etc.)
│   │   ├── i18n/                 # Multilingual translation dictionary & React Context
│   │   ├── pages/                # Dashboard, Analytics, Compare, Action Center, Copilot, etc.
│   │   └── types.ts              # Full TypeScript interface definitions
│   ├── package.json
│   └── vite.config.ts
├── src/                          # Backend application source code
│   ├── api/                      # FastAPI endpoints, routes, middleware, and schemas
│   ├── cleaning/                 # Data hygiene and quarantine router
│   ├── copilot/                  # Grounded intent classification, retrieval & response validation
│   ├── features/                 # Time, festival, weather, and transaction feature generators
│   ├── ingestion/                # Strongly-typed data ingestion
│   ├── ml/                       # Autoregressive models, baselines, and inference engine
│   ├── recommendations/          # Subsystems for inventory, pricing, churn & cross-sell
│   ├── reporting/                # Markdown and summary artifact generators
│   ├── schemas/                  # Pydantic data schemas
│   ├── validation/               # Referential integrity and data validators
│   └── pipeline.py               # End-to-end data pipeline runner
├── tests/                        # Comprehensive unit & integration test suite (173 tests)
├── .env.example                  # Environment configuration template
├── docker-compose.yml            # Containerized multi-service orchestration
├── Dockerfile                    # Production backend container definition
├── requirements.txt              # Production Python dependencies
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** & **npm**

---

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/atleekumaar/VyaparMitra.git
cd VyaparMitra

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Copy environment template
cp .env.example .env

# Run data pipeline to generate feature store and models
python -m src.pipeline

# Start the FastAPI server
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend server will be live at `http://127.0.0.1:8000/`.  
Interactive Swagger API documentation is available at `http://127.0.0.1:8000/docs`.

---

### 2. Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev

# Or build for production
npm run build
```

The frontend application will be live at `http://localhost:5173/` (or served directly through FastAPI at `http://127.0.0.1:8000/`).

---

## 🌐 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status and uptime |
| `GET` | `/api/dashboard/summary` | Complete merchant financial KPIs, trends & action counts |
| `GET` | `/api/merchants/{id}/benchmark` | Hyperlocal peer group ranking, scorecard & percentiles |
| `GET` | `/api/dashboard/actions` | Top priority recommendations for dashboard display |
| `GET` | `/api/recommendations` | Full list of prioritized actions with evidence & filters |
| `POST` | `/api/recommendations/{id}/status` | Update action state (`ACCEPTED`, `EXECUTED`, `REJECTED`) |
| `POST` | `/api/copilot/ask` | Natural language business query (Hindi/Hinglish/English) |
| `GET` | `/api/copilot/daily-brief` | Morning business briefing summary |
| `GET` | `/api/analytics/sales` | Historical sales series, AOV, and discount rates |
| `GET` | `/api/analytics/customers` | RFM customer segmentation and churn tiers |
| `GET` | `/api/analytics/products` | Top revenue drivers and 80/20 Pareto distribution |
| `GET` | `/api/forecasts/sales` | 7-day forward projected revenue and model info |
| `GET` | `/api/forecasts/demand` | SKU-level projected 7-day unit demand |
| `POST` | `/api/notifications/whatsapp` | Dispatch WhatsApp digests via Twilio |

---

## 🧪 Testing & Quality Assurance

The codebase includes an extensive suite of **173 automated tests** covering data validation, machine learning zero-leakage guards, recommendation engines, and API endpoints.

```bash
# Run the entire test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

### Key Verification Checks:
- ✅ **Referential Integrity**: Guarantees zero orphan records across merchants, products, and transactions.
- ✅ **Strict Anti-Leakage**: Ensures feature store computations strictly use chronological cutoff dates.
- ✅ **Zero Hallucination Retrieval**: Verifies copilot answers are backed 100% by validated parquet records.
- ✅ **Dynamic Localization**: Validates responsive switching across Hindi, Hinglish, and English strings.

---

## 🐳 Docker Deployment

To launch the full production stack using Docker:

```bash
# Build and run container
docker-compose up --build -d

# Verify container status
docker-compose ps
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'feat: Add AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  Built with ❤️ for Indian Retail Merchants by <b>VyaparMitra Team</b>
</p>
