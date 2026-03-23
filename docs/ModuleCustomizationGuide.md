# Module Customization Guide

## Auth and Identity

- Purpose: registration, login, JWT refresh, session tracking, Telegram OTP password recovery.
- Backend ownership: `backend/apps/auth_module/*`, `backend/apps/shared/services/otp_service.py`, `backend/apps/shared/services/telegram_notification_service.py`.
- Frontend ownership: `frontend/src/modules/auth/*`, `frontend/src/routes/ProtectedRoute.jsx`.
- APIs: `/api/auth/*`.
- Shared contracts: JWT token payload, `UserProfile.telegram_chat_id`, password reset OTP lifecycle.
- Replace or disable: swap `TelegramNotificationService` to an email/SMS implementation and keep `PasswordResetService` unchanged; auth disable is not recommended because all protected pages depend on it.
- Risks when editing: token rotation and OTP single-use logic must stay aligned, otherwise reset and session revocation can drift.
- Extension ideas: multi-device logout, refresh-token cookie transport, admin OTP audit view.

## Portfolio Management

- Purpose: create portfolio types, add/remove holdings, prevent duplicates.
- Backend ownership: `backend/apps/portfolio_module/*`.
- Frontend ownership: `frontend/src/modules/portfolio/*`.
- APIs: `/api/portfolio-types/`, `/api/portfolio-stocks/`.
- Dependencies: authenticated user, stock symbol input, analytics modules optionally consume stored holdings.
- Replace or disable: disable by feature flag and remove dashboard/sidebar links; analytics depending on holdings should show empty-state fallbacks.
- Risks when editing: preserve unique constraint on `(user, portfolio_type, symbol)`.
- Extension ideas: watchlists, transaction ledger, realized/unrealized PnL.

## Stock Search

- Purpose: Indian stock discovery by symbol/company proxy.
- Backend ownership: `backend/apps/stock_search_module/*`.
- Frontend ownership: `frontend/src/modules/stock-search/*`.
- APIs: `/api/stocks/search`.
- Dependencies: `MarketDataService`.
- Replace or disable: swap `backend/apps/shared/data_providers/yfinance_provider.py` with another provider behind `MarketDataProvider`.
- Risks when editing: provider normalization for `.NS` and `.BO` symbols must remain consistent.
- Extension ideas: sector browsing, autocomplete cache, exchange filters.

## Stock Analytics

- Purpose: detail analytics, valuation metrics, chart-ready history, PE comparison.
- Backend ownership: `backend/apps/analytics_module/*`, `backend/apps/shared/services/valuation_service.py`.
- Frontend ownership: `frontend/src/modules/stock-analytics/*`.
- APIs: `/api/stocks/:symbol/analytics`, `/api/portfolio/pe-comparison`.
- Inputs: symbol, portfolio holdings.
- Outputs: pricing summary, PE/EPS/market cap, intrinsic value, discount percentage, opportunity signal, chart series.
- Replace or disable: replace only `StockAnalyticsService` or `ValuationService` and keep endpoint contracts stable.
- Risks when editing: null provider data must be handled gracefully.
- Extension ideas: DCF valuation, technical indicators, statement-driven ratios.

## Stock Comparison

- Purpose: compare two stocks on return, volatility, Sharpe ratio, and narrative winner.
- Backend ownership: `backend/apps/comparison_module/*`.
- Frontend ownership: `frontend/src/modules/stock-comparison/*`.
- APIs: `/api/portfolio/compare`.
- Replace or disable: update `StockComparisonService` scoring logic only.
- Risks when editing: scoring rules should remain explainable and deterministic.
- Extension ideas: benchmark comparison, drawdown analysis, rolling metrics.

## Risk Categorization

- Purpose: low/medium/high risk labeling from volatility rules.
- Backend ownership: `backend/apps/risk_module/*`.
- Frontend ownership: `frontend/src/modules/risk/*`.
- APIs: `/api/stock/risk-categorization`.
- Replace or disable: replace only `RiskCategorizationService`.
- Risks when editing: keep category thresholds documented for auditability.
- Extension ideas: beta, VaR, downside deviation.

## Portfolio Clustering

- Purpose: unsupervised grouping of portfolio stocks by return/volatility/price behavior.
- Backend ownership: `backend/apps/clustering_module/*`.
- Frontend ownership: `frontend/src/modules/clustering/*`.
- APIs: `/api/portfolio/clustering`.
- Replace or disable: disable via feature flag or swap KMeans with another clustering algorithm inside `PortfolioClusteringService`.
- Risks when editing: sparse history must still return a useful empty state.
- Extension ideas: cluster naming, sector overlays, dimensionality reduction views.

## Forecasting

- Purpose: next-step stock and portfolio forecasts using an explainable baseline.
- Backend ownership: `backend/apps/forecasting_module/*`.
- Frontend ownership: `frontend/src/modules/forecasting/*`.
- APIs: `/api/stock/forecast`, `/api/stock/portfolio-forecast-next-day`.
- Replace or disable: replace only `StockForecastingService` and keep request/response shape stable.
- Risks when editing: ARIMA requires minimum data and can fail on noisy series; wrap production errors carefully.
- Extension ideas: Prophet/ETS adapter, confidence intervals, batch jobs.

## Commodities

- Purpose: gold/silver correlation, line/scatter/regression outputs.
- Backend ownership: `backend/apps/commodities_module/*`.
- Frontend ownership: `frontend/src/modules/commodities/*`.
- APIs: `/api/commodities/gold-silver-correlation`.
- Replace or disable: disable via `FF_ENABLE_COMMODITIES` and remove navigation link.
- Risks when editing: commodity ticker/provider compatibility can differ from equities.
- Extension ideas: oil correlation, rolling windows, macro overlays.

## Crypto

- Purpose: BTC-USD hourly pricing and next-hour forecast.
- Backend ownership: `backend/apps/crypto_module/*`.
- Frontend ownership: `frontend/src/modules/crypto/*`.
- APIs: `/api/crypto/btcusd-hourly`.
- Replace or disable: disable via `FF_ENABLE_CRYPTO` and remove navigation link.
- Risks when editing: hourly intervals can be less stable from upstream providers.
- Extension ideas: ETH pair support, volatility bands, streaming prices.
