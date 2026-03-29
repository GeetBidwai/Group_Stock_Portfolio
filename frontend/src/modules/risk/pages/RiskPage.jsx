import { useEffect, useMemo, useState } from "react";

import { stockApi } from "../../stock-search/services/stockApi";
import { RiskDistributionChart } from "../components/RiskDistributionChart";
import { RiskStockTable } from "../components/RiskStockTable";
import { RiskSummaryCards } from "../components/RiskSummaryCards";
import { RiskOverviewPanels } from "../components/RiskOverviewPanels";
import "../risk-page.css";

const FILTERS = ["All", "Low", "Medium", "High", "Unknown"];
const SCOPES = [
  { value: "portfolio", label: "My Portfolio" },
  { value: "tracked", label: "Tracked Universe" },
];

export function RiskPage() {
  const [items, setItems] = useState([]);
  const [selectedRisk, setSelectedRisk] = useState("All");
  const [scope, setScope] = useState("portfolio");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadRiskItems() {
      try {
        setLoading(true);
        const data = await stockApi.riskList(scope);
        if (!cancelled) {
          setItems(Array.isArray(data) ? data : []);
          setError("");
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadRiskItems();
    return () => {
      cancelled = true;
    };
  }, [scope]);

  const summary = useMemo(() => {
    return items.reduce(
      (accumulator, item) => {
        const risk = item.risk || "Unknown";
        accumulator.total += 1;
        accumulator[risk] = (accumulator[risk] || 0) + 1;
        return accumulator;
      },
      { total: 0, Low: 0, Medium: 0, High: 0, Unknown: 0 },
    );
  }, [items]);

  const filteredItems = useMemo(() => {
    if (selectedRisk === "All") {
      return items;
    }
    return items.filter((item) => (item.risk || "Unknown") === selectedRisk);
  }, [items, selectedRisk]);

  const sortedItems = useMemo(() => {
    const order = { High: 0, Medium: 1, Low: 2, Unknown: 3 };
    return [...filteredItems].sort((left, right) => {
      const riskDiff = (order[left.risk || "Unknown"] ?? 9) - (order[right.risk || "Unknown"] ?? 9);
      if (riskDiff !== 0) {
        return riskDiff;
      }
      return (left.symbol || "").localeCompare(right.symbol || "");
    });
  }, [filteredItems]);

  const highlightedCategories = useMemo(
    () => [
      {
        risk: "High",
        title: "High Risk",
        description: "Shows larger daily swings and needs closer monitoring during volatile sessions.",
        criteria: "Volatility at or above the configured medium threshold.",
        count: summary.High,
      },
      {
        risk: "Medium",
        title: "Medium Risk",
        description: "Balanced risk profile with moderate price movement across the observed period.",
        criteria: "Volatility between the low and medium thresholds.",
        count: summary.Medium,
      },
      {
        risk: "Low",
        title: "Low Risk",
        description: "More stable trading behavior relative to the rest of the tracked universe.",
        criteria: "Volatility below the configured low threshold.",
        count: summary.Low,
      },
      {
        risk: "Unknown",
        title: "Unknown",
        description: "Insufficient or missing historical data prevented a confident categorization.",
        criteria: "No usable history or cached price context.",
        count: summary.Unknown,
      },
    ],
    [summary.High, summary.Low, summary.Medium, summary.Unknown],
  );

  return (
    <div className="risk-page">
      <section className="panel risk-hero">
        <div>
          <p className="risk-kicker">RISK STUDIO</p>
          <h1 className="risk-title">Risk Categorization</h1>
          <p className="muted risk-subtitle">
            Review risk buckets, inspect the overall distribution, and switch between your portfolio and the tracked market universe.
          </p>
        </div>
        <div className="risk-controls">
          <label className="risk-control">
            <span className="risk-control__label">Scope</span>
            <select value={scope} onChange={(event) => setScope(event.target.value)}>
              {SCOPES.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label className="risk-control">
            <span className="risk-control__label">Category Filter</span>
            <select value={selectedRisk} onChange={(event) => setSelectedRisk(event.target.value)}>
              {FILTERS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      {error ? (
        <section className="panel">
          <p style={{ margin: 0 }}>{error}</p>
        </section>
      ) : null}

      <section className="risk-dashboard-grid">
        <div className="panel">
          <div className="risk-section-header">
            <div>
              <h2>Overview</h2>
              <p className="muted">
                {scope === "portfolio"
                  ? "Live view of the risk categories for the stocks in your portfolio."
                  : "Live from the cached risk snapshot endpoint used by the broader tracked universe view."}
              </p>
            </div>
          </div>
          <RiskSummaryCards summary={summary} loading={loading} />
        </div>

        <div className="panel">
          <div className="risk-section-header">
            <div>
              <h2>Risk Distribution</h2>
              <p className="muted">
                {scope === "portfolio"
                  ? "A quick view of how your portfolio holdings are spread across each bucket."
                  : "A quick view of how the tracked stocks are spread across each bucket."}
              </p>
            </div>
          </div>
          <RiskDistributionChart items={filteredItems} loading={loading} />
        </div>
      </section>

      <section className="panel">
        <div className="risk-section-header">
          <div>
            <h2>Category Guide</h2>
            <p className="muted">Each category explains what the classification means in this module.</p>
          </div>
        </div>
        <RiskOverviewPanels categories={highlightedCategories} />
      </section>

      <section className="panel">
        <div className="risk-section-header">
          <div>
            <h2>{scope === "portfolio" ? "Portfolio Stocks" : "Tracked Stocks"}</h2>
            <p className="muted">
              {selectedRisk === "All"
                ? scope === "portfolio"
                  ? "Your portfolio stocks grouped by their stored risk classification."
                  : "All available tracked stocks grouped by their stored risk classification."
                : scope === "portfolio"
                  ? `Showing only ${selectedRisk.toLowerCase()}-risk stocks from your portfolio.`
                  : `Showing only ${selectedRisk.toLowerCase()}-risk stocks from the current snapshot.`}
            </p>
          </div>
        </div>
        <RiskStockTable items={sortedItems} loading={loading} />
      </section>
    </div>
  );
}
