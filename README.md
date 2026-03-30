# Group Stock Project

Group Stock Project is a full-stack stock analytics platform with a Django REST backend and a React + Vite frontend. It combines auth, stock discovery, portfolio workflows, analytics, risk, clustering, forecasting, sentiment, recommendations, commodities, crypto forecasting, and an in-app assistant.

## Tech Stack

### Backend

- Python
- Django + Django REST Framework
- SimpleJWT authentication
- PostgreSQL (primary) or SQLite (fallback)
- yfinance + requests
- pandas + numpy
- scikit-learn + statsmodels
- reportlab (PDF sentiment report)
- textblob + vaderSentiment (sentiment fallback)
- transformers + torch (FinBERT sentiment path)
- Assistant stack: custom service flow + optional RAG (Gemini embeddings + ChromaDB/memory fallback + Ollama, with optional Grok API for general replies)

### Frontend

- React 18
- Vite
- React Router
- Axios
- Recharts

## Repository Layout

```text
Group_Stock_Project/
|-- backend/
|   |-- apps/
|   |-- config/
|   |-- manage.py
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |-- public/
|   `-- package.json
|-- data/
|-- docs/
`-- deploy/
```

## Active Backend Modules

- `auth_module`: register/signup, login, token refresh/logout, user/session endpoints
- `stock_search_module`: stock search and risk list endpoints
- `stocks_module`: market/sector/stock catalog and grouped portfolio flow
- `portfolio_module`: manual portfolio type and stock CRUD flow
- `analytics_module`: analytics + PE comparison
- `comparison_module`: stock-vs-stock comparison
- `risk_module`: risk categorization endpoint
- `clustering_module`: portfolio clustering + stock clustering endpoint
- `forecasting_module`: stock and next-day portfolio forecast
- `sentiment_module`: stock sentiment + PDF report download
- `recommendations_module`: recommendations endpoint
- `commodities_module`: gold/silver and correlation analytics
- `crypto_module`: BTC hourly and range forecast analytics
- `assistant_module`: personal assistant chat + optional RAG reindex

## Assistant Architecture (Current)

- The chatbot does **not** use LangGraph.
- It uses a custom orchestration flow in `assistant_module`:
  - Intent + deterministic reply path
  - Knowledge-base matcher
  - Optional RAG pipeline (`ASSISTANT_RAG_ENABLED=true`)
  - General LLM fallback (Grok if configured, else Ollama)
- Vector storage uses ChromaDB when installed, and an in-memory/JSON fallback when unavailable.

## Routing Note

- `auth_telegram` code exists in the repository, but its URL routes are not currently mounted in `backend/config/urls.py`.

## Local Setup

### 1) Backend setup

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -r backend/requirements.txt
```

Create `backend/.env` from `backend/.env.example`, then run:

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

Backend base URL: `http://127.0.0.1:8000/`

### 2) Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://127.0.0.1:5173/`

## Data Seeding

From `backend/`:

```bash
python manage.py seed_stocks
python manage.py seed_stocks_catalog --dry-run --path ../data/Global_400_Stocks_Database.xlsx
python manage.py seed_stocks_catalog --path ../data/Global_400_Stocks_Database.xlsx
python manage.py update_risk
```

## Environment Variables

### Backend (`backend/.env`)

Base variables:

```env
SECRET_KEY=change-me
DEBUG=true
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=stock_analytics_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-me
POSTGRES_CONN_MAX_AGE=60

JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7

MARKET_DATA_PROVIDER=yfinance
STOCKS_CATALOG_WORKBOOK=

NEWSAPI_KEY=
DATABRICKS_TOKEN=
DATABRICKS_SENTIMENT_URL=
DATABRICKS_TIMEOUT_SECONDS=10
FINBERT_ENABLED=true
FINBERT_MODEL_NAME=ProsusAI/finbert
FINBERT_CACHE_DIR=
FINBERT_LOCAL_FILES_ONLY=false
FINBERT_RETRY_COOLDOWN_SECONDS=600

FF_ENABLE_PORTFOLIO=true
FF_ENABLE_COMPARISON=true
FF_ENABLE_RISK=true
FF_ENABLE_CLUSTERING=true
FF_ENABLE_FORECASTING=true
FF_ENABLE_SENTIMENT=true
FF_ENABLE_COMMODITIES=true
FF_ENABLE_CRYPTO=true
```

Optional assistant RAG variables:

```env
ASSISTANT_RAG_ENABLED=false
GEMINI_API_KEY=
GEMINI_EMBEDDING_MODEL=text-embedding-004
GEMINI_TIMEOUT_SECONDS=12
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_TIMEOUT_SECONDS=18
OLLAMA_MAX_RETRIES=2
GROK_API_KEY=
GROK_MODEL=grok-2-latest
GROK_BASE_URL=https://api.x.ai/v1
GROK_TIMEOUT_SECONDS=20
GROK_MAX_RETRIES=1
CHROMA_PERSIST_DIR=
```

Optional deployment/security variables read by settings:

```env
CORS_ALLOW_ALL_ORIGINS=true
CORS_ALLOWED_ORIGINS=
CSRF_TRUSTED_ORIGINS=
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
SECURE_SSL_REDIRECT=false
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=false
SECURE_HSTS_PRELOAD=false
```

### Frontend (`frontend/.env`)

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_TELEGRAM_BOT_USERNAME=
VITE_TELEGRAM_QR_PROVIDER=https://api.qrserver.com/v1/create-qr-code/
VITE_FF_ENABLE_COMMODITIES=true
VITE_FF_ENABLE_CRYPTO=true
VITE_FF_ENABLE_CLUSTERING=true
VITE_FF_ENABLE_FORECASTING=true
VITE_FF_ENABLE_SENTIMENT=true
```

## API Endpoints (Current Routing)

### Auth

- `POST /api/auth/register`
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/auth/sessions`

### Portfolio Types and Stocks

- `GET, POST /api/portfolio-types/`
- `GET, PATCH, PUT, DELETE /api/portfolio-types/<pk>`
- `GET, POST /api/portfolio-stocks/`
- `DELETE /api/portfolio-stocks/<pk>`

### Stocks, Catalog, and Portfolio Intelligence

- `GET /api/sectors/`
- `POST /api/sectors/`
- `GET /api/stocks/search`
- `GET /api/stocks/risk/`
- `GET /api/stocks/<symbol>/analytics`
- `GET /api/stocks/`
- `GET /api/stocks/markets/`
- `GET /api/stocks/markets/<code>/sectors/`
- `GET /api/stocks/sectors/<id>/stocks/`
- `GET /api/portfolio/`
- `POST /api/portfolio/add/`
- `GET /api/portfolio/insights/`
- `DELETE /api/portfolio/entries/<entry_id>/`

### Analytics, Comparison, Clustering, Risk, Forecasting

- `GET /api/portfolio/pe-comparison`
- `GET /api/portfolio/portfolio-stock-analytics`
- `GET, POST /api/portfolio/compare`
- `GET /api/portfolio/stocks/`
- `GET, POST /api/portfolio/clustering`
- `GET /api/cluster-stocks/`
- `POST /api/stock/risk-categorization`
- `POST /api/stock/forecast`
- `POST /api/stock/portfolio-forecast-next-day`

### Sentiment, Recommendations, Commodities, Crypto, Assistant

- `POST /api/sentiment/analyze/`
- `GET /api/sentiment/report/`
- `GET /api/recommendations/`
- `GET /api/commodities/gold-silver-correlation`
- `GET /api/commodities/gold/`
- `GET /api/commodities/silver/`
- `GET /api/commodities/correlation/`
- `GET /api/crypto/btcusd-hourly`
- `GET /api/crypto/btc-forecast/`
- `POST /api/assistant/chat/`
- `POST /api/assistant/reindex/` (admin only)

## Notes

- Most APIs require authentication by JWT (`Authorization: Bearer <token>`); refresh is handled via `/api/auth/refresh`.
- `CookieOrHeaderJWTAuthentication` also supports an `access_token` cookie if present.
- Market snapshots/history are cached under `backend/.yfinance-cache/`, with bundled history fallback from `data/yfinance-cache/history/`.
- There are two portfolio model flows in this repository (`portfolio_module` and `stocks_module`) and both are currently used.

## Useful Commands

### Backend

```bash
cd backend
python manage.py migrate
python manage.py runserver
python manage.py seed_stocks
python manage.py seed_stocks_catalog --dry-run --path ../data/Global_400_Stocks_Database.xlsx
python manage.py seed_stocks_catalog --path ../data/Global_400_Stocks_Database.xlsx
python manage.py update_risk
python manage.py test
```

### Frontend

```bash
cd frontend
npm install
npm run dev
npm run build
```
