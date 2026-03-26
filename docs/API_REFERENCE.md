# API Reference

This document lists the currently wired backend API endpoints from `backend/config/urls.py` and the included module route files.

## Auth

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Register a new username/password user account. |
| `POST` | `/api/auth/login` | Log in with username and password and receive JWT tokens. |
| `POST` | `/api/auth/refresh` | Refresh an access token using a refresh token. |
| `POST` | `/api/auth/logout` | Revoke the provided refresh token session. |
| `GET` | `/api/auth/me` | Return the currently authenticated user profile. |
| `GET` | `/api/auth/sessions` | List the active sessions for the logged-in user. |
| `POST` | `/api/auth/request-reset-otp` | Send a Telegram OTP for the mobile-number-based reset flow. |
| `POST` | `/api/auth/verify-otp` | Verify a reset OTP and issue a short-lived password reset token. |
| `POST` | `/api/auth/reset-password` | Reset the password using the short-lived reset token. |
| `POST` | `/api/auth/forgot-password/request-otp` | Start the identifier-based forgot-password flow. |
| `POST` | `/api/auth/forgot-password/verify-otp` | Verify the forgot-password OTP. |
| `POST` | `/api/auth/forgot-password/reset-password` | Complete password reset after OTP verification. |
| `POST` | `/api/auth/signup/telegram-link/session` | Create a Telegram signup-link session and deep link payload. |
| `GET` | `/api/auth/signup/telegram-link/status/<token>` | Check whether a Telegram signup-link session is pending, linked, or expired. |
| `POST` | `/api/auth/signup/telegram-link/complete` | Finish signup after Telegram account linking is complete. |
| `POST` | `/api/auth/telegram/webhook` | Receive Telegram webhook updates for the signup-link flow. |

## Telegram MPIN Auth

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/auth/telegram/` | Verify Telegram login payload and identify the Telegram user. |
| `POST` | `/api/auth/set-mpin/` | Create an MPIN for a Telegram-authenticated user and issue JWT tokens. |
| `POST` | `/api/auth/login-mpin/` | Log in with Telegram ID and MPIN. |
| `POST` | `/api/auth/mobile/request-otp/` | Send an OTP to the Telegram-linked account for MPIN reset. |
| `POST` | `/api/auth/mobile/verify-otp/` | Verify the OTP used for MPIN reset. |
| `POST` | `/api/auth/reset-mpin/` | Reset the MPIN after successful OTP verification. |

## Portfolio Types

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/portfolio-types/` | List portfolio types belonging to the current user. |
| `POST` | `/api/portfolio-types/` | Create a new portfolio type for the current user. |
| `GET` | `/api/portfolio-types/<pk>` | Retrieve a specific portfolio type. |
| `PATCH` | `/api/portfolio-types/<pk>` | Update a specific portfolio type. |
| `PUT` | `/api/portfolio-types/<pk>` | Replace a specific portfolio type. |
| `DELETE` | `/api/portfolio-types/<pk>` | Delete a specific portfolio type. |

## Portfolio Stocks

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/portfolio-stocks/` | List manually added portfolio stocks for the current user. |
| `POST` | `/api/portfolio-stocks/` | Add a stock to a user portfolio type. |
| `DELETE` | `/api/portfolio-stocks/<pk>` | Delete a manually added portfolio stock. |

## Sector Catalog

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/sectors/` | List sectors, optionally from the stock catalog by market filter. |
| `POST` | `/api/sectors/` | Create a portfolio-sector record. |

## Stock Search and Stock Catalog

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/stocks/search` | Search `StockReference` records by symbol or company name. |
| `GET` | `/api/stocks/risk/` | List cached stock risk labels and cached price snapshots. |
| `GET` | `/api/stocks/<symbol>/analytics` | Return analytics for one stock symbol. |
| `GET` | `/api/stocks/` | List stock catalog entries, optionally filtered by sector. |
| `GET` | `/api/stocks/markets/` | List available markets in the stock catalog. |
| `GET` | `/api/stocks/markets/<code>/sectors/` | List sectors for a market such as `IN` or `US`. |
| `GET` | `/api/stocks/sectors/<id>/stocks/` | List stocks in a sector with live price payloads. |

## Portfolio Insights and Grouped Portfolio

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/portfolio/` | Return grouped stock-catalog portfolio entries by sector. |
| `POST` | `/api/portfolio/add/` | Add a stock-catalog stock to the grouped portfolio. |
| `GET` | `/api/portfolio/insights/` | Return risk breakdown plus top gainers and losers for the grouped portfolio. |
| `DELETE` | `/api/portfolio/entries/<entry_id>/` | Remove a grouped portfolio entry. |

## Analytics

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/portfolio/pe-comparison` | Compare PE ratios across the user's manually added portfolio stocks. |
| `GET` | `/api/portfolio/portfolio-stock-analytics` | Return analytics for stocks in a specific portfolio type. |

## Comparison

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/portfolio/compare` | Compare two stocks using query parameters and a selected time range. |
| `POST` | `/api/portfolio/compare` | Compare two stocks using request-body symbols. |
| `GET` | `/api/portfolio/stocks/` | List deduplicated stock options from the user's portfolio for comparison UI. |

## Risk

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/stock/risk-categorization` | Classify a stock into low, medium, or high risk using volatility. |

## Clustering

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/portfolio/clustering` | Cluster manually added portfolio stocks using return, volatility, and price features. |
| `GET` | `/api/cluster-stocks/` | Build PCA or optional UMAP stock clusters for the user portfolio. |

## Forecasting

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/stock/forecast` | Forecast a stock price series using ARIMA or the MLP-based model path. |
| `POST` | `/api/stock/portfolio-forecast-next-day` | Compute the next-day average forecast across a portfolio. |

## Sentiment

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/sentiment/analyze/` | Analyze recent news sentiment for a stock symbol. |
| `GET` | `/api/sentiment/report/` | Download a PDF sentiment report for a stock symbol. |

## Recommendations

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/recommendations/` | Return ranked top and bottom stock recommendations. |

## Commodities

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/commodities/gold-silver-correlation` | Return gold and silver correlation analytics. |
| `GET` | `/api/commodities/gold/` | Return the gold commodity analytics payload. |
| `GET` | `/api/commodities/silver/` | Return the silver commodity analytics payload. |
| `GET` | `/api/commodities/correlation/` | Return commodity correlation data used by the commodity views. |

## Crypto

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/crypto/btcusd-hourly` | Return BTC/USD recent hourly history and next-hour forecast. |
| `GET` | `/api/crypto/btc-forecast/` | Return the longer-range BTC forecast payload for the requested range. |

## Notes

- Most endpoints require authentication by default unless the view explicitly allows anonymous access.
- Query parameters such as `portfolio_id`, `range`, `method`, `k`, and `sector_id` are handled by the corresponding module views.
- The authoritative routing source is `backend/config/urls.py` plus the included module `urls.py` files.
