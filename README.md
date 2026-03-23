# Stock Analytics Platform

Modular stock analytics platform built with Django REST Framework and React/Vite. The architecture is feature-sliced so auth, portfolio, search, analytics, comparison, risk, clustering, forecasting, commodities, and crypto can evolve independently.

## Stack

- Backend: Django, DRF, SimpleJWT, SQLite-first with PostgreSQL-friendly structure
- Frontend: React, Vite, Recharts
- Data and analytics: yfinance, pandas, numpy, scikit-learn, statsmodels
- Password recovery: Telegram OTP via abstracted notification service

## Folder Tree

```text
backend/
  apps/
    auth_module/
    portfolio_module/
    stock_search_module/
    analytics_module/
    comparison_module/
    risk_module/
    clustering_module/
    forecasting_module/
    commodities_module/
    crypto_module/
    shared/
  config/
  manage.py
frontend/
  src/
    app/
    components/
    modules/
      auth/
      dashboard/
      portfolio/
      stock-search/
      stock-analytics/
      stock-comparison/
      risk/
      clustering/
      forecasting/
      commodities/
      crypto/
    routes/
    services/
    utils/
docs/
  API.md
  ModuleCustomizationGuide.md
```

## Setup

### Backend

1. Create a virtual environment.
2. Install dependencies with `pip install -r backend/requirements.txt`.
3. Copy `backend/.env.example` to `backend/.env` and fill the secrets.
4. Run `python backend/manage.py migrate`.
5. Start the API with `python backend/manage.py runserver`.

### Frontend

1. Run `npm install` inside `frontend`.
2. Copy `frontend/.env.example` to `frontend/.env`.
3. Start the app with `npm run dev`.

## Telegram OTP Linking Strategy

The platform stores `telegram_chat_id` and optional `telegram_username` on `UserProfile`. Forgot-password accepts username, email, or Telegram username as the identifier. `PasswordResetService` resolves the user, checks cooldown, creates a single-use OTP record, hashes the OTP in storage, and sends the plaintext code through `TelegramNotificationService`.

To replace Telegram later, keep `PasswordResetService` and swap only the notification implementation plus the profile linkage fields.

## Feature Flags

Backend flags live in `settings.FEATURE_FLAGS` and frontend flags live in `frontend/.env`.

- `FF_ENABLE_PORTFOLIO`
- `FF_ENABLE_COMPARISON`
- `FF_ENABLE_RISK`
- `FF_ENABLE_CLUSTERING`
- `FF_ENABLE_FORECASTING`
- `FF_ENABLE_COMMODITIES`
- `FF_ENABLE_CRYPTO`

## Assumptions

- `yfinance` is the default market-data source for local development.
- The Telegram bot can message the stored `telegram_chat_id`.
- SQLite is enough for local development; the models are kept conventional for PostgreSQL migration later.
- Forecasting uses an explainable ARIMA baseline instead of a more operationally heavy ML pipeline.

## Known Limitations

- Search quality depends on upstream `yfinance` metadata availability.
- ARIMA on sparse or unstable series can fail without extra fallback handling.
- The frontend uses localStorage token persistence for local development rather than hardened HTTP-only cookies.
- Only the data-bearing apps with models currently include explicit migrations.

## Future Enhancements

- PostgreSQL config, Celery workers, and cached background jobs
- Better provider search index for Indian equities
- Confidence intervals, benchmark-aware analytics, and richer dashboard widgets
- Session/device revocation UI and more granular audit events

## Additional Docs

- API reference: `docs/API.md`
- Module replacement and disable guidance: `docs/ModuleCustomizationGuide.md`
