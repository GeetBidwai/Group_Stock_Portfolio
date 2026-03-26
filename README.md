# Stock Sentiment Project

Stock Sentiment Project is a modular full-stack market intelligence platform built with Django REST Framework and React. It combines authentication, portfolio workflows, stock discovery, analytics, forecasting, clustering, news sentiment, recommendations, commodities analysis, and BTC forecasting in one codebase.

## Tech Stack

### Backend

- Python
- Django 5
- Django REST Framework
- SimpleJWT
- PostgreSQL, with SQLite fallback
- yfinance
- pandas, numpy
- scikit-learn, statsmodels
- requests
- reportlab
- TextBlob, VaderSentiment
- transformers, torch

### Frontend

- React 18
- Vite
- React Router
- Recharts

## Repository Layout

```text
Stock_sentiment_Project/
|-- backend/
|   |-- apps/
|   |   |-- analytics_module/
|   |   |-- auth_module/
|   |   |-- auth_telegram/
|   |   |-- clustering_module/
|   |   |-- commodities_module/
|   |   |-- comparison_module/
|   |   |-- crypto_module/
|   |   |-- forecasting_module/
|   |   |-- portfolio_module/
|   |   |-- recommendations_module/
|   |   |-- risk_module/
|   |   |-- sentiment_module/
|   |   |-- shared/
|   |   |-- stock_search_module/
|   |   `-- stocks_module/
|   |-- config/
|   |-- manage.py
|   `-- requirements.txt
|-- frontend/
|   |-- public/
|   |-- src/
|   |   |-- app/
|   |   |-- components/
|   |   |-- modules/
|   |   |-- routes/
|   |   |-- services/
|   |   `-- utils/
|   |-- package.json
|   `-- vite.config.js
`-- docs/
    |-- API.md
    `-- ModuleCustomizationGuide.md
```

## Backend Modules

- `auth_module`: username/password auth, JWT token issuing, user sessions, password reset, Telegram signup link flow
- `auth_telegram`: Telegram login verification, MPIN setup/login/reset flow
- `portfolio_module`: user-defined portfolio types and manually added portfolio stocks
- `stocks_module`: market, sector, stock catalog, grouped portfolio entries, live sector stock browsing
- `stock_search_module`: stock reference search and cached stock risk list
- `analytics_module`: stock analytics, PE comparison, portfolio stock analytics
- `comparison_module`: stock-vs-stock comparison and portfolio stock options
- `risk_module`: volatility-driven risk categorization
- `clustering_module`: portfolio clustering plus PCA or optional UMAP stock clustering
- `forecasting_module`: stock forecast and portfolio next-day forecast
- `sentiment_module`: news aggregation, sentiment scoring, PDF report export
- `recommendations_module`: ranked recommendations from sentiment and recent trend
- `commodities_module`: gold/silver views and correlation analytics
- `crypto_module`: BTC/USD hourly forecast and longer-range BTC forecast payloads
- `shared`: market-data provider abstraction, OTP utilities, Telegram notification service, feature flags, valuation/risk helpers

## Main Features

- JWT login, refresh, logout, and session tracking
- Telegram signup linking by deep link or QR
- Telegram MPIN-based mobile login flow
- Stock search with local seeded references
- Market and sector catalog browsing
- Sector-based stock portfolio entries
- Manual portfolio types and portfolio-stock CRUD
- Stock analytics using yfinance snapshots and price history
- PE-based valuation helpers and opportunity signals
- Risk classification from historical volatility
- Stock comparison with returns, volatility, and normalized trend charts
- Portfolio clustering and stock clustering
- Stock forecasting with ARIMA or MLP-based fallback path
- Sentiment analysis from NewsAPI, Yahoo RSS, or Google News RSS
- PDF sentiment report generation
- Recommendation ranking
- Gold/silver analytics
- BTC hourly and range-based forecast endpoints

## Architecture Notes

- The backend is organized around thin DRF views and service classes.
- Market data flows through `apps.shared.services.market_data_service.MarketDataService`.
- `yfinance` is the active provider and also writes local snapshot cache files under `backend/.yfinance-cache/`.
- Django cache is configured as `LocMemCache`.
- Frontend auth is managed with React context and tokens stored in `localStorage`.
- There are currently two portfolio-related model flows in the codebase:
  - `portfolio_module` for `PortfolioType` and `PortfolioStock`
  - `stocks_module` for catalog-driven `PortfolioEntry`

## Local Setup

### Backend

1. Create and activate a virtual environment.
2. Install backend dependencies.

```bash
pip install -r backend/requirements.txt
```

3. Create `backend/.env`.
4. Run migrations.

```bash
cd backend
python manage.py migrate
```

5. Seed stock data if required.

```bash
python manage.py seed_stocks
python manage.py seed_stocks_catalog --dry-run --path ../data/Global_400_Stocks_Database.xlsx
python manage.py seed_stocks_catalog --path ../data/Global_400_Stocks_Database.xlsx
python manage.py update_risk
```

6. Start the backend server.

```bash
python manage.py runserver
```

Backend base URL: `http://127.0.0.1:8000/`

### Frontend

1. Install frontend dependencies.

```bash
cd frontend
npm install
```

2. Optionally create `frontend/.env`.
3. Start the Vite dev server.

```bash
npm run dev
```

Frontend default URL: `http://127.0.0.1:5173/`

## Backend Environment Variables

Example `backend/.env`:

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

TELEGRAM_BOT_TOKEN=
TELEGRAM_BOT_USERNAME=
TELEGRAM_BOT_API_URL=https://api.telegram.org
TELEGRAM_WEBHOOK_SECRET=
TELEGRAM_SIGNUP_LINK_EXPIRY_SECONDS=900
TELEGRAM_OTP_EXPIRY_SECONDS=300
TELEGRAM_OTP_RESEND_COOLDOWN_SECONDS=60
OTP_VERIFIED_CACHE_SECONDS=600
PASSWORD_RESET_OTP_MAX_ATTEMPTS=3
PASSWORD_RESET_OTP_REQUEST_LIMIT_PER_HOUR=3
PASSWORD_RESET_TOKEN_EXPIRY_SECONDS=600
AUTH_RESET_REQUIRE_OTP=false
TELEGRAM_AUTH_MAX_AGE_SECONDS=86400

NEWSAPI_KEY=
DATABRICKS_TOKEN=
DATABRICKS_SENTIMENT_URL=
DATABRICKS_TIMEOUT_SECONDS=10
FINBERT_ENABLED=true
FINBERT_MODEL_NAME=ProsusAI/finbert
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

### Environment Notes

- `DB_ENGINE=postgres` is the main runtime path.
- `DB_ENGINE=sqlite` uses `backend/db.sqlite3`.
- `STOCKS_CATALOG_WORKBOOK` is optional and can point to the 400-stock workbook so `seed_stocks_catalog` can run without passing `--path` every time.
- `NEWSAPI_KEY` is optional. The sentiment module falls back to Yahoo RSS and Google News RSS.
- Databricks sentiment is optional.
- FinBERT support depends on `transformers` and `torch`, and may require model download or local cache availability.
- Telegram-dependent flows require bot credentials and, for webhook verification, `TELEGRAM_WEBHOOK_SECRET`.

## Stock Catalog Import

- The deployed stocks browser reads `Market`, `Sector`, and `Stock` rows from PostgreSQL.
- The bundled migration seeds only a small default catalog for India and USA.
- The 400-stock workbook must be imported once per environment to load the full catalog.

```bash
cd backend
python manage.py seed_stocks_catalog --dry-run --path ../data/Global_400_Stocks_Database.xlsx
python manage.py seed_stocks_catalog --path ../data/Global_400_Stocks_Database.xlsx
```

- `--dry-run` validates the workbook and reports how many rows would be created or updated without changing the database.
- `--replace-existing` is destructive and should be avoided unless you intentionally want to rebuild the catalog from scratch.
- If `STOCKS_CATALOG_WORKBOOK` is set in `backend/.env`, you can omit `--path`.

## Frontend Environment Variables

Example `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_FF_ENABLE_CLUSTERING=true
VITE_FF_ENABLE_FORECASTING=true
VITE_FF_ENABLE_SENTIMENT=true
VITE_FF_ENABLE_COMMODITIES=true
VITE_FF_ENABLE_CRYPTO=true
```

## API Overview

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/auth/sessions`
- `POST /api/auth/signup/telegram-link/session`
- `GET /api/auth/signup/telegram-link/status/:token`
- `POST /api/auth/signup/telegram-link/complete`
- `POST /api/auth/telegram/webhook`
- `POST /api/auth/request-reset-otp`
- `POST /api/auth/verify-otp`
- `POST /api/auth/reset-password`
- `POST /api/auth/forgot-password/request-otp`
- `POST /api/auth/forgot-password/verify-otp`
- `POST /api/auth/forgot-password/reset-password`

### Telegram MPIN Auth

- `POST /api/auth/telegram/`
- `POST /api/auth/set-mpin/`
- `POST /api/auth/login-mpin/`
- `POST /api/auth/mobile/request-otp/`
- `POST /api/auth/mobile/verify-otp/`
- `POST /api/auth/reset-mpin/`

### Portfolio and Catalog

- `GET /api/portfolio-types/`
- `POST /api/portfolio-types/`
- `GET /api/portfolio-stocks/`
- `POST /api/portfolio-stocks/`
- `DELETE /api/portfolio-stocks/:id`
- `GET /api/sectors/`
- `POST /api/sectors/`
- `GET /api/stocks/`
- `GET /api/stocks/markets/`
- `GET /api/stocks/markets/:code/sectors/`
- `GET /api/stocks/sectors/:id/stocks/`
- `GET /api/portfolio/`
- `POST /api/portfolio/add/`
- `GET /api/portfolio/insights/`
- `DELETE /api/portfolio/entries/:entry_id/`

### Search, Analytics, and Intelligence

- `GET /api/stocks/search?q=...`
- `GET /api/stocks/risk/`
- `GET /api/stocks/:symbol/analytics`
- `GET /api/portfolio/pe-comparison`
- `GET /api/portfolio/portfolio-stock-analytics?portfolio_id=:id`
- `GET /api/portfolio/compare?stockA=:a&stockB=:b&range=:range`
- `POST /api/portfolio/compare`
- `GET /api/portfolio/stocks/`
- `GET /api/portfolio/clustering`
- `GET /api/cluster-stocks/?method=pca&k=3`
- `POST /api/stock/risk-categorization`
- `POST /api/stock/forecast`
- `POST /api/stock/portfolio-forecast-next-day`
- `POST /api/sentiment/analyze/`
- `GET /api/sentiment/report/?stock=:symbol`
- `GET /api/recommendations/`
- `GET /api/commodities/gold-silver-correlation`
- `GET /api/commodities/gold/`
- `GET /api/commodities/silver/`
- `GET /api/commodities/correlation/`
- `GET /api/crypto/btcusd-hourly`
- `GET /api/crypto/btc-forecast/?range=3m`

See [docs/API.md](docs/API.md) for the shorter endpoint reference.

## Dependency Notes

`backend/requirements.txt` contains the runtime backend dependencies used in the current codebase.

- `transformers` and `torch` support FinBERT sentiment scoring
- `reportlab` is required for PDF sentiment reports
- `bcrypt` is required for Telegram MPIN hashing
- `umap-learn` is optional and currently commented out because the clustering code falls back to PCA if UMAP is unavailable

## Current Limitations

- Automated test coverage is minimal at the moment.
- Several advanced features depend on live third-party providers.
- Some portfolio functionality is split across two backend model flows.
- Tokens are stored in browser `localStorage` in the current frontend implementation.

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

## License

Add a project license before publishing or distributing the repository.
