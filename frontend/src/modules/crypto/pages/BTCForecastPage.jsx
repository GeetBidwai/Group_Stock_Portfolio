import { useEffect, useState } from "react";

import { BTCChart } from "../components/BTCChart";
import { BTCStatsCard } from "../components/BTCStatsCard";
import { cryptoApi } from "../services/cryptoApi";

const RANGE_OPTIONS = [
  { value: "3m", label: "3M", description: "Last 90 days" },
  { value: "6m", label: "6M", description: "Last 180 days" },
  { value: "1y", label: "1Y", description: "Last 365 days" },
];

function formatCurrency(value) {
  return `$${Number(value ?? 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

export function BTCForecastPage() {
  const [selectedRange, setSelectedRange] = useState("3m");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;
    setError("");
    setResult(null);

    cryptoApi
      .btcForecast(selectedRange)
      .then((data) => {
        if (!isMounted) {
          return;
        }
        if (data.error) {
          setError(data.error);
          return;
        }
        setResult(data);
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [selectedRange]);

  if (error) {
    return (
      <section className="panel">
        <h1>BTC/USD Forecast</h1>
        <p>{error}</p>
      </section>
    );
  }

  if (!result) {
    return (
      <section className="panel">
        <h1>BTC/USD Forecast</h1>
        <p>Loading BTC forecast...</p>
      </section>
    );
  }

  const trendTone = result.trend === "bullish" ? "positive" : "negative";
  const selectedRangeMeta = RANGE_OPTIONS.find((option) => option.value === selectedRange) || RANGE_OPTIONS[0];
  const periodReturns = result.period_returns || {};
  const cards = [
    { label: "Current Price", value: formatCurrency(result.current_price) },
    { label: "Predicted Price", value: formatCurrency(result.predicted_price), tone: trendTone },
    { label: "3M Return", value: `${periodReturns["3m"] ?? 0}%`, tone: (periodReturns["3m"] ?? 0) >= 0 ? "positive" : "negative" },
    { label: "6M Return", value: `${periodReturns["6m"] ?? 0}%`, tone: (periodReturns["6m"] ?? 0) >= 0 ? "positive" : "negative" },
    { label: "1Y Return", value: `${periodReturns["1y"] ?? 0}%`, tone: (periodReturns["1y"] ?? 0) >= 0 ? "positive" : "negative" },
    { label: "Model", value: result.model || "Exponential Smoothing" },
    { label: "Forecast Days", value: String(result.forecast_days || 30) },
    { label: "Expected Return", value: `${result.expected_return}%`, tone: trendTone },
    { label: "Trend", value: result.trend, tone: trendTone },
  ];

  return (
    <div className="grid" style={{ gap: 20 }}>
      <section className="panel">
        <h1 style={{ marginTop: 0, marginBottom: 8 }}>BTC/USD Forecasting</h1>
        <p className="muted" style={{ marginTop: 0, marginBottom: 16 }}>
          Range-aware BTC analytics with a continuous 30-day forecast based on one year of daily market data.
        </p>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          {RANGE_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              className={selectedRange === option.value ? "btn" : ""}
              onClick={() => setSelectedRange(option.value)}
              style={
                selectedRange === option.value
                  ? undefined
                  : {
                      padding: "12px 16px",
                      borderRadius: 14,
                      border: "1px solid var(--border)",
                      background: "rgba(255, 255, 255, 0.7)",
                      cursor: "pointer",
                    }
              }
            >
              {option.label}
            </button>
          ))}
        </div>
      </section>

      <BTCChart
        historicalData={result.historical_data}
        forecastData={result.forecast_data}
        rangeLabel={selectedRangeMeta.description}
      />

      <section
        className="grid"
        style={{ gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 20 }}
      >
        {cards.map((card) => (
          <BTCStatsCard key={card.label} label={card.label} value={card.value} tone={card.tone} />
        ))}
      </section>
    </div>
  );
}
