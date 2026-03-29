import { useEffect, useMemo, useState } from "react";

import { Card, MetricCard } from "../../../components/ui/Card";
import { ForecastCard } from "../components/ForecastCard";
import { ForecastChart } from "../components/ForecastChart";
import { portfolioApi } from "../../portfolio/services/portfolioApi";
import { stockApi } from "../../stock-search/services/stockApi";

export function ForecastPage() {
  const [portfolioStocks, setPortfolioStocks] = useState([]);
  const [result, setResult] = useState(null);
  const [pageError, setPageError] = useState("");

  useEffect(() => {
    async function loadPortfolioStocks() {
      try {
        const unifiedStocks = await portfolioApi.listStockOptions();
        setPortfolioStocks(Array.isArray(unifiedStocks) ? unifiedStocks : []);
        setPageError("");
      } catch (unifiedErr) {
        try {
          const legacyStocks = await portfolioApi.listStocks();
          const normalized = (Array.isArray(legacyStocks) ? legacyStocks : []).map((stock) => ({
            symbol: stock.symbol,
            name: stock.company_name || stock.symbol,
          }));
          setPortfolioStocks(normalized);
          setPageError("");
        } catch (legacyErr) {
          setPageError(legacyErr.message || unifiedErr.message);
        }
      }
    }

    loadPortfolioStocks();
  }, []);

  const portfolioOptions = useMemo(() => {
    const seen = new Set();
    return portfolioStocks
      .filter((stock) => {
        if (seen.has(stock.symbol)) {
          return false;
        }
        seen.add(stock.symbol);
        return true;
      })
      .map((stock) => ({
        symbol: stock.symbol,
        name: stock.name || stock.company_name || stock.symbol,
      }));
  }, [portfolioStocks]);

  async function handleForecast(payload) {
    try {
      setPageError("");
      setResult(null);
      const forecastResult = await stockApi.forecast(payload);
      setResult(forecastResult);
      setPageError(forecastResult?.message || "");
    } catch (err) {
      setResult(null);
      setPageError(err.message);
      throw err;
    }
  }

  return (
    <>
      <Card className="forecast-page-hero">
        <div className="stocks-page-hero__header">
          <div>
            <p className="eyebrow">Forecast Studio</p>
            <h1 style={{ marginBottom: 6 }}>Stock Forecasting</h1>
            <p className="muted" style={{ margin: 0 }}>Run ARIMA or RNN-based forecasts for portfolio stocks or any searchable symbol.</p>
          </div>
        </div>
        <div className="metric-grid">
          <MetricCard label="Portfolio Symbols" value={portfolioOptions.length} meta="Available in the portfolio selector" tone="primary" />
          <MetricCard label="Supported Horizons" value="3" meta="3M, 6M, and 1Y currently supported by the API" tone="primary" />
          <MetricCard label="Chart Focus" value={result?.symbol || "Ready"} meta={result ? `${result.model} • ${result.horizon}` : "Generate a forecast to visualize"} tone="success" />
        </div>
        {pageError ? <p className="form-error">{pageError}</p> : null}
      </Card>

      <section className="grid two">
        <ForecastCard
          title="Forecast from Portfolio"
          description="Choose a stock you already hold, select the model and horizon, then generate a forecast."
          mode="portfolio"
          portfolioOptions={portfolioOptions}
          onForecast={handleForecast}
        />
        <ForecastCard
          title="Forecast Any Stock"
          description="Search any stock symbol, pick a model and horizon, and compare its projected path."
          mode="search"
          onForecast={handleForecast}
        />
      </section>

      <ForecastChart result={result} />
    </>
  );
}
