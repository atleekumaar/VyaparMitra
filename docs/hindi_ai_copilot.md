# VyaparMitra Phase 5: Hindi AI Business Copilot

## 1. Overview & Architecture

The **VyaparMitra Hindi AI Business Copilot** empowers retail merchants to interact with their business intelligence, predictive ML models, and recommendation decision engine in **Hindi (Devanagari)**, **Hinglish (Roman script Hindi)**, and **English**.

### The Golden Rule: The LLM Is Never the Source of Truth
The LLM functions strictly as a natural language communicator and translator. It **never** computes business numbers, estimates inventory, or invents recommendations. Every numeric figure, SKU, customer churn band, and action item is derived deterministically from the underlying Phase 1–4 data marts.

```text
                                MERCHANT INPUT
                        (Hindi / Hinglish / English)
                                     │
                                     ▼
                        [1. Language Detection]
                                     │
                                     ▼
                   [2. Intent & Entity Extraction]
                   (with Multi-turn State & Anaphora)
                                     │
                                     ▼
                          [3. Query Planning]
                                     │
                                     ▼
                       [4. Grounded Context Retrieval]
          ┌──────────────────────────┴──────────────────────────┐
          ▼                                                     ▼
Phase 1-4 Data Marts                                  Knowledge Base (RAG)
(Sales, Forecasts, Recs)                              (Glossary, FAQ, Guides)
          │                                                     │
          └──────────────────────────┬──────────────────────────┘
                                     ▼
                         [5. Prompt Construction]
                        (System + Grounded Context)
                                     │
                                     ▼
                         [6. LLM / Mock Provider]
                                     │
                                     ▼
                     [7. Anti-Hallucination Guard]
                        (Numeric & Entity Check)
                                     │
                                     ▼
                             MERCHANT ANSWER
                       (with Verified Citations)
```

---

## 2. Component Taxonomy

### 2.1 Language Processing Layer (`src/copilot/language/`)
- **`LanguageDetector`**: Detects Devanagari Unicode ($\ge 15\% \to$ Hindi), disambiguates English keywords vs Latin Hindi tokens, and identifies code-mixed Hinglish.
- **`LanguageNormalizer`**: Cleans punctuation and standardizes merchant phonetic variants (`zyaada` $\to$ `zyada`, `pehele` $\to$ `pehle`, `kyuu` $\to$ `kyun`).

### 2.2 Intent & Entity Engine (`src/copilot/intent/`)
- **`IntentClassifier`**: Classifies queries across 20 business intents:
  - `SALES_SUMMARY`, `SALES_TREND`, `SALES_FORECAST`
  - `PRODUCT_PERFORMANCE`, `PRODUCT_DEMAND_FORECAST`
  - `INVENTORY_RECOMMENDATION`, `PRICING_RECOMMENDATION`, `CROSS_SELL`
  - `CUSTOMER_RISK`, `CUSTOMER_ANALYSIS`, `RETENTION_RECOMMENDATION`
  - `DAILY_ACTION_PLAN`, `RECOMMENDATION_EXPLANATION`
  - `GREETING`, `HELP_CAPABILITIES`, `OUT_OF_DOMAIN`
- **`EntityExtractor`**: Extracts Product SKUs (`PRD_*`, `SKU-*`), Customer IDs (`C*`), Categories, timeframes (`kal`, `yesterday`, `aaj`), and anaphoric markers (`uska`, `iske`, `it`).
- **`QueryRouter`**: Combines intent, entities, and multi-turn state into an executable `QueryPlan`.

### 2.3 Retrieval & Context Synthesis (`src/copilot/retrieval/`)
- **`BusinessQueryEngine`**: Direct Python query layer against Parquet artifacts:
  - Phase 1: `product_features.parquet`, `customer_features.parquet`
  - Phase 2: `sales_summary.parquet`, `sales_daily.parquet`, `product_rankings.parquet`
  - Phase 3: `sales_forecast_7d.parquet`, `product_demand_forecast_7d.parquet`, `customer_risk_scores.parquet`
  - Phase 4: `merchant_action_plan.parquet`, `inventory_recommendations.parquet`, `recommendation_evidence.parquet`
- **`KnowledgeRetriever`**: BM25 keyword search over domain documentation in `data/knowledge/` (`business_glossary.md`, `merchant_faq.md`, `metric_definitions.md`, `recommendation_guide.md`, `system_capabilities.md`).
- **`ContextBuilder`**: Merges business queries, metrics, and knowledge snippets into `BusinessContext`.

### 2.4 LLM Providers (`src/copilot/llm/`)
- **`MockProvider`**: Default deterministic natural language engine in Hindi, Hinglish, and English using exact numbers and entities from `BusinessContext`. Enables 100% test reproducibility with zero API keys or external network calls.
- **`GeminiProvider`**: Google Gemini (`gemini-1.5-flash`) integration with automatic fallback to `MockProvider`.
- **`OpenAIProvider`**: OpenAI (`gpt-4o-mini`) integration with automatic fallback to `MockProvider`.

### 2.5 Validation & Anti-Hallucination Guard (`src/copilot/validation/`)
- **`GroundingChecker`**: Extracts all numbers, currencies (₹), and entity IDs from the generated text and verifies they match numbers in `BusinessContext`.
- **`ResponseValidator`**: Flags ungrounded claims and auto-substitutes ungrounded responses with deterministic grounded templates.

### 2.6 Conversation State & Memory (`src/copilot/conversation/`)
- **`ConversationState`**: Bounded multi-turn session tracking active entities (`last_product_id`, `last_customer_id`, `last_intent`, `last_language`) and resolving anaphora across turns (e.g. "PRD_SNK_01 ka sales?" $\to$ "Aur iska demand forecast?").

---

## 3. CLI & Usage Guide

### CLI Commands
```bash
# 1. Interactive Multi-turn Chat
python -m src.copilot

# 2. Daily Merchant Action Brief
python -m src.copilot --daily-brief

# 3. Single Query in Hinglish
python -m src.copilot --query "Kaunsa product restock karna chahiye?"

# 4. Single Query in Hindi (Devanagari)
python -m src.copilot --query "मेरी कुल बिक्री कितनी रही है?" --language hindi

# 5. Single Query in English
python -m src.copilot --query "What is the 7-day sales forecast?" --language english

# 6. Structured JSON Output
python -m src.copilot --query "Kaunsa maal khatam hone wala hai?" --json
```

### Python API Integration
```python
from src.copilot import VyaparMitraCopilot

copilot = VyaparMitraCopilot()
response = copilot.ask("Kal kitni bikri hui thi?")

print(response.answer)
print(response.sources)
print(response.validation.valid)
```
