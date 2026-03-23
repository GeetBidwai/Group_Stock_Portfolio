# API Documentation

## Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/auth/sessions`
- `POST /api/auth/forgot-password/request-otp`
- `POST /api/auth/forgot-password/verify-otp`
- `POST /api/auth/forgot-password/reset-password`

## Portfolio

- `GET /api/portfolio-types/`
- `POST /api/portfolio-types/`
- `GET /api/portfolio-stocks/`
- `POST /api/portfolio-stocks/`
- `DELETE /api/portfolio-stocks/:id`

## Stocks and Analytics

- `GET /api/stocks/search?q=`
- `GET /api/stocks/:symbol/analytics`
- `GET /api/portfolio/pe-comparison`
- `POST /api/portfolio/compare`
- `GET|POST /api/portfolio/clustering`

## Risk and Forecasting

- `POST /api/stock/risk-categorization`
- `POST /api/stock/forecast`
- `POST /api/stock/portfolio-forecast-next-day`

## Commodities and Crypto

- `GET /api/commodities/gold-silver-correlation`
- `GET /api/crypto/btcusd-hourly`
