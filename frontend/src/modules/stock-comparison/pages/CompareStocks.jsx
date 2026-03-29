import { useEffect, useMemo, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, ChartCard, MetricCard } from "../../../components/ui/Card";
import { StockSelect } from "../components/StockSelect";
import { compareStocksApi } from "../services/compareStocksApi";
import "./../compare-stocks.css";

const RANGE_OPTIONS = ["1m", "3m", "6m", "1y"];

function formatCurrency(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return `Rs ${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return `${value}%`;
}

function buildChartData(result, showPercentChange) {
  if (!result?.stockA || !result?.stockB) {
    return [];
  }

  const combined = new Map();
  for (const point of result.stockA.normalized_data || []) {
    combined.set(point.date, { date: point.date, stockA: point.value, stockB: null });
  }
  for (const point of result.stockB.normalized_data || []) {
    const current = combined.get(point.date) || { date: point.date, stockA: null, stockB: null };
    current.stockB = point.value;
    combined.set(point.date, current);
  }

  return Array.from(combined.values())
    .sort((left, right) => left.date.localeCompare(right.date))
    .map((item) => ({
      ...item,
      stockA: showPercentChange && item.stockA !== null ? Number((item.stockA - 100).toFixed(2)) : item.stockA,
      stockB: showPercentChange && item.stockB !== null ? Number((item.stockB - 100).toFixed(2)) : item.stockB,
    }));
}

function StockCard({ title, stock, color, showPercentChange }) {
  return (
    <article className="compare-stock-card">
      <div className="compare-stock-card__meta">
        <div>
          <p className="eyebrow">{title}</p>
          <h2 style={{ marginTop: 0, marginBottom: 0 }}>{stock.symbol}</h2>
        </div>
        <span className="compare-stock-card__badge" style={{ background: color }}>
          {showPercentChange ? formatPercent(stock.return_pct) : formatCurrency(stock.current_price)}
        </span>
      </div>

      <div className="compare-metrics">
        <div className="compare-metric">
          <p className="muted" style={{ margin: 0, fontSize: 12 }}>Current Price</p>
          <p style={{ margin: "6px 0 0", fontWeight: 700 }}>{formatCurrency(stock.current_price)}</p>
        </div>
        <div className="compare-metric">
          <p className="muted" style={{ margin: 0, fontSize: 12 }}>% Change</p>
          <p style={{ margin: "6px 0 0", fontWeight: 700 }}>{formatPercent(stock.return_pct)}</p>
        </div>
        <div className="compare-metric">
          <p className="muted" style={{ margin: 0, fontSize: 12 }}>Profit</p>
          <p style={{ margin: "6px 0 0", fontWeight: 700 }}>{formatCurrency(stock.profit)}</p>
        </div>
        <div className="compare-metric">
          <p className="muted" style={{ margin: 0, fontSize: 12 }}>Volatility</p>
          <p style={{ margin: "6px 0 0", fontWeight: 700 }}>{formatPercent(stock.volatility)}</p>
        </div>
      </div>
    </article>
  );
}

function PerformanceRow({ label, valueA, valueB }) {
  const maxValue = Math.max(Math.abs(valueA), Math.abs(valueB), 1);
  return (
    <div className="compare-performance__row">
      <div style={{ fontWeight: 700 }}>{label}</div>
      <div className="compare-performance__bars">
        <div className="compare-performance__track">
          <div className="compare-performance__fill is-a" style={{ width: `${Math.min((Math.abs(valueA) / maxValue) * 100, 100)}%` }} />
        </div>
        <div className="compare-performance__track">
          <div className="compare-performance__fill is-b" style={{ width: `${Math.min((Math.abs(valueB) / maxValue) * 100, 100)}%` }} />
        </div>
        <div className="compare-performance__legend">
          <span>Stock A: {formatPercent(valueA)}</span>
          <span>Stock B: {formatPercent(valueB)}</span>
        </div>
      </div>
    </div>
  );
}

export function CompareStocksPage() {
  const [portfolioOptions, setPortfolioOptions] = useState([]);
  const [form, setForm] = useState({ stockA: "", stockB: "" });
  const [range, setRange] = useState("6m");
  const [normalizeData, setNormalizeData] = useState(true);
  const [showPercentChange, setShowPercentChange] = useState(true);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;

    compareStocksApi
      .listPortfolioStocks()
      .then((stocks) => {
        if (!isMounted) {
          return;
        }
        setPortfolioOptions(Array.isArray(stocks) ? stocks : []);
        if (stocks.length >= 2) {
          setForm({ stockA: stocks[0].symbol, stockB: stocks[1].symbol });
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.response?.data?.error || err.message || "Unable to load portfolio stocks.");
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const chartData = useMemo(
    () => buildChartData(result, normalizeData && showPercentChange),
    [normalizeData, result, showPercentChange],
  );

  async function handleCompare() {
    if (!form.stockA || !form.stockB) {
      setError("Please select two portfolio stocks.");
      return;
    }
    if (form.stockA === form.stockB) {
      setError("Please select two different stocks.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      const data = await compareStocksApi.compare(form.stockA, form.stockB, range);
      setResult(data);
    } catch (err) {
      setResult(null);
      setError(err.response?.data?.error || err.message || "Comparison failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="compare-dashboard">
      <Card>
        <div className="compare-toolbar">
          <div>
            <p className="eyebrow">Compare Studio</p>
            <h1 style={{ marginTop: 0, marginBottom: 8 }}>Compare Stocks</h1>
            <p className="muted" style={{ margin: 0 }}>
              Build a side-by-side performance view using only stocks from your own portfolio.
            </p>
          </div>

          <div className="compare-toolbar__row">
            <StockSelect
              label="Select Stock A"
              placeholder="Choose portfolio stock"
              options={portfolioOptions}
              value={form.stockA}
              onChange={(symbol) => setForm((current) => ({ ...current, stockA: symbol }))}
              disabledSymbol={form.stockB}
            />
            <StockSelect
              label="Select Stock B"
              placeholder="Choose portfolio stock"
              options={portfolioOptions}
              value={form.stockB}
              onChange={(symbol) => setForm((current) => ({ ...current, stockB: symbol }))}
              disabledSymbol={form.stockA}
            />

            <div>
              <p className="muted" style={{ marginTop: 0, marginBottom: 8, fontSize: 13 }}>Time Filter</p>
              <div className="compare-filter">
                {RANGE_OPTIONS.map((option) => (
                  <button
                    key={option}
                    type="button"
                    className={`compare-filter__button${range === option ? " is-active" : ""}`}
                    onClick={() => setRange(option)}
                  >
                    {option.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="compare-toggles">
            <label className="compare-toggle">
              <input type="checkbox" checked={normalizeData} onChange={(event) => setNormalizeData(event.target.checked)} />
              Normalize Data
            </label>
            <label className="compare-toggle">
              <input type="checkbox" checked={showPercentChange} onChange={(event) => setShowPercentChange(event.target.checked)} />
              Show % Change
            </label>
          </div>

          <div className="compare-actions">
            <button className="btn" type="button" onClick={handleCompare}>
              {loading ? "Comparing..." : "Compare"}
            </button>
          </div>
        </div>
        {error ? <p className="form-error">{error}</p> : null}
      </Card>

      {result && (
        <>
          <div className="compare-summary-grid">
            <MetricCard label="Range" value={range.toUpperCase()} meta="Selected comparison window" tone="primary" />
            <MetricCard label="Stock A" value={result.stockA.symbol} meta={formatPercent(result.stockA.return_pct)} tone="primary" />
            <MetricCard label="Stock B" value={result.stockB.symbol} meta={formatPercent(result.stockB.return_pct)} tone="success" />
          </div>

          <ChartCard
            className="compare-chart-card"
            title="Comparison Chart"
            description="The chart is now the visual focus, with softer lines and lighter grid styling."
          >
            <div style={{ height: 420 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 16, right: 20, bottom: 8, left: 8 }}>
                  <CartesianGrid stroke="rgba(148, 163, 184, 0.25)" vertical={false} />
                  <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#64748b" }} tickLine={false} axisLine={false} />
                  <YAxis
                    tick={{ fontSize: 12, fill: "#64748b" }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => (showPercentChange ? `${value}%` : value)}
                  />
                  <Tooltip
                    contentStyle={{
                      borderRadius: 14,
                      border: "1px solid #e2e8f0",
                      boxShadow: "0 8px 24px rgba(15, 23, 42, 0.12)",
                    }}
                    formatter={(value) => (showPercentChange ? `${value}%` : value)}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="stockA" name={result.stockA.symbol} stroke="#2563eb" strokeWidth={3} dot={false} connectNulls />
                  <Line type="monotone" dataKey="stockB" name={result.stockB.symbol} stroke="#22c55e" strokeWidth={3} dot={false} connectNulls />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          <section className="compare-cards">
            <StockCard title="Stock A" stock={result.stockA} color="#2563eb" showPercentChange={showPercentChange} />
            <StockCard title="Stock B" stock={result.stockB} color="#22c55e" showPercentChange={showPercentChange} />
          </section>

          <Card>
            <div className="card__header">
              <div>
                <h2 style={{ marginTop: 0 }}>Performance Comparison</h2>
                <p className="card__description">Cleaner bar rows to compare the two positions across common windows.</p>
              </div>
            </div>
            <div className="compare-performance">
              <PerformanceRow label="1 Month Return" valueA={result.stockA.performance["1m"]} valueB={result.stockB.performance["1m"]} />
              <PerformanceRow label="3 Month Return" valueA={result.stockA.performance["3m"]} valueB={result.stockB.performance["3m"]} />
              <PerformanceRow label="6 Month Return" valueA={result.stockA.performance["6m"]} valueB={result.stockB.performance["6m"]} />
            </div>
          </Card>

          <Card>
            <div className="card__header">
              <div>
                <h2 style={{ marginTop: 0 }}>Insights</h2>
                <p className="card__description">Short takeaways from the comparison output.</p>
              </div>
            </div>
            <div className="compare-insights">
              {result.insights.map((insight) => (
                <div key={insight} className="compare-insight">
                  {insight}
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
