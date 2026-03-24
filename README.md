# Stock Sentiment Project

A modular full-stack market intelligence platform for Indian equities, built with Django REST Framework and React. The project combines portfolio management, stock analytics, comparison tools, forecasting, sentiment analysis, recommendations, commodities correlation, and BTC forecasting in a single feature-oriented codebase.

## Highlights

- JWT-based authentication with session tracking
- Portfolio organization by sector and portfolio type
- Indian stock search with local reference data and yfinance-backed market snapshots
- Stock analytics with price history, valuation context, and PE-based insights
- Stock-to-stock comparison using return, volatility, and risk-adjusted signals
- Risk categorization based on historical volatility
- Portfolio and stock clustering
- Multi-horizon forecasting for stocks and portfolios
- News-driven sentiment analysis with PDF report export
- Recommendation engine based on sentiment plus recent trend
- Gold/Silver correlation analytics
- BTC/USD hourly and 30-day forecast views

## Tech Stack

### Backend

- Python
- Django 5
- Django REST Framework
- SimpleJWT
- PostgreSQL for active development/runtime
- yfinance, pandas, numpy
- scikit-learn, statsmodels
- requests, reportlab
- psycopg 3

### Frontend

- React 18
- Vite
- React Router
- Recharts

## Project Structure

```text
Stock_sentiment_Project/
|-- backend/
|   |-- apps/
|   |   |-- analytics_module/
|   |   |-- auth_module/
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
|   |   `-- stock_search_module/
|   |-- config/
|   |-- manage.py
|   `-- requirements.txt
|-- frontend/
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

## Core Features

### 1. Authentication

- User registration and login
- JWT access/refresh flow
- Session tracking per refresh token
- Forgot-password flow with Telegram OTP support
- Development shortcut mode when OTP verification is disabled

### 2. Portfolio Management

- Create sectors
- Create portfolio types under sectors
- Add and remove portfolio stocks
- Prevent duplicate stock entries within the same portfolio

### 3. Stock Discovery and Analytics

- Search stock references by symbol or company name
- Fetch live/cached price history from yfinance
- Show valuation-oriented analytics such as PE, EPS, intrinsic value estimate, and discount percentage

### 4. Comparison, Risk, and Clustering

- Compare two stocks over a selected period
- Categorize risk using annualized volatility
- Cluster holdings using KMeans
- Additional stock clustering view with PCA and optional UMAP-style workflow fallback

### 5. Forecasting

- Stock forecasting using ARIMA
- Neural-network-style forecast option using `MLPRegressor`
- Portfolio next-day forecast aggregation
- BTC forecast analytics and hourly BTC prediction

### 6. Sentiment and Recommendations

- Fetch recent stock news from NewsAPI, Yahoo RSS, or Google News RSS
- Score article sentiment using Databricks if configured
- Fallback sentiment scoring via `textblob`, `vaderSentiment`, or keyword heuristics
- Export sentiment analysis as PDF
- Generate ranked stock recommendations from sentiment plus recent trend

### 7. Commodities and Crypto

- Gold/Silver correlation analysis
- BTC/USD visualization and forecast metrics

## Local Setup

### Backend

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Create `backend/.env` and configure it.
4. Run migrations:

```bash
cd backend
python manage.py migrate
```

5. Start the backend server:

```bash
python manage.py runserver
```

The API will run at `http://127.0.0.1:8000/`.

### Frontend

1. Install frontend dependencies:

```bash
cd frontend
npm install
```

2. Optionally create `frontend/.env` for frontend flags and API base URL.
3. Start the frontend:

```bash
npm run dev
```

The frontend will usually run at `http://127.0.0.1:5173/`.

## Backend Environment Variables

Create `backend/.env` with values like these:

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
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_BOT_API_URL=https://api.telegram.org
TELEGRAM_OTP_EXPIRY_SECONDS=300
TELEGRAM_OTP_RESEND_COOLDOWN_SECONDS=60
AUTH_RESET_REQUIRE_OTP=false
NEWSAPI_KEY=
DATABRICKS_TOKEN=
DATABRICKS_SENTIMENT_URL=
DATABRICKS_TIMEOUT_SECONDS=10
FF_ENABLE_PORTFOLIO=true
FF_ENABLE_COMPARISON=true
FF_ENABLE_RISK=true
FF_ENABLE_CLUSTERING=true
FF_ENABLE_FORECASTING=true
FF_ENABLE_SENTIMENT=true
FF_ENABLE_COMMODITIES=true
FF_ENABLE_CRYPTO=true
```

### Notes

- The project is currently configured to run on PostgreSQL.
- SQLite can still be used only as a fallback if `DB_ENGINE=sqlite`.
- `AUTH_RESET_REQUIRE_OTP=false` keeps password reset easy during local development.
- `NEWSAPI_KEY` is optional. Without it, the app falls back to Yahoo Finance RSS and Google News RSS.
- Databricks sentiment configuration is optional. If missing, fallback sentiment methods are used.

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

## Main API Areas

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/auth/sessions`
- `POST /api/auth/forgot-password/request-otp`
- `POST /api/auth/forgot-password/verify-otp`
- `POST /api/auth/forgot-password/reset-password`

### Portfolio and Stocks

- `GET /api/portfolio-types/`
- `POST /api/portfolio-types/`
- `GET /api/portfolio-stocks/`
- `POST /api/portfolio-stocks/`
- `DELETE /api/portfolio-stocks/:id`
- `GET /api/sectors/`
- `POST /api/sectors/`
- `GET /api/stocks/search?q=...`
- `GET /api/stocks/risk/`

### Analytics and Intelligence

- `GET /api/stocks/:symbol/analytics`
- `GET /api/portfolio/pe-comparison`
- `GET /api/portfolio/portfolio-stock-analytics?portfolio_id=:id`
- `POST /api/portfolio/compare`
- `GET /api/portfolio/clustering`
- `GET /api/cluster-stocks/`
- `POST /api/stock/risk-categorization`
- `POST /api/stock/forecast`
- `POST /api/stock/portfolio-forecast-next-day`
- `POST /api/sentiment/analyze/`
- `GET /api/sentiment/report/?stock=:symbol`
- `GET /api/recommendations/`
- `GET /api/commodities/gold-silver-correlation`
- `GET /api/crypto/btcusd-hourly`
- `GET /api/crypto/btc-forecast/`

For module details, see [docs/API.md](docs/API.md) and [docs/ModuleCustomizationGuide.md](docs/ModuleCustomizationGuide.md).

## Data Sources and Behavior

- Django now uses PostgreSQL through environment-based settings.
- Market data is primarily fetched through `yfinance`.
- Stock search uses a local `StockReference` table and seed data for initial discovery.
- Several services cache results in Django's local memory cache.
- The yfinance provider also stores local snapshot files for resilience when live responses are incomplete.

## Current Development Notes

- PostgreSQL is the current database backend.
- A local SQLite backup/fixture may still exist only for migration rollback/reference.
- Authentication tokens are stored in browser localStorage in the current frontend implementation.
- Some advanced features degrade gracefully when external data sources are unavailable.
- UMAP-style clustering is optional; the implementation falls back to PCA if the required package is not installed.

## Useful Commands

### Backend

```bash
cd backend
python manage.py migrate
python manage.py runserver
python manage.py seed_stocks
python manage.py update_risk
```

### Frontend

```bash
cd frontend
npm install
npm run dev
npm run build
```

## Future Improvements

- Celery/background jobs for long-running data tasks
- Better provider coverage for Indian markets
- More robust production auth hardening
- Stronger automated test coverage
- CI/CD and deployment documentation

## License

Add your preferred license before publishing the repository.
