import { useEffect, useMemo, useState } from "react";

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
        const stocks = await portfolioApi.listStocks();
        setPortfolioStocks(stocks);
        setPageError("");
      } catch (err) {
        setPageError(err.message);
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
        name: stock.company_name || stock.symbol,
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
      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", flexWrap: "wrap" }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Forecast Studio</p>
            <h1 style={{ marginBottom: 6 }}>Stock Forecasting</h1>
            <p className="muted" style={{ margin: 0 }}>Run ARIMA or RNN-based forecasts for stocks from your portfolio or any searchable symbol.</p>
          </div>
        </div>
        {pageError && <p style={{ color: "#c05353", marginTop: 14, marginBottom: 0 }}>{pageError}</p>}
      </section>

      <section className="grid" style={{ marginTop: 20 }}>
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
