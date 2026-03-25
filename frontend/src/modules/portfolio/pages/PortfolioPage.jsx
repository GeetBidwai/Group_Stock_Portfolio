import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { portfolioApi } from "../services/portfolioApi";

const CHART_COLORS = ["#167c80", "#28b8b0", "#77c9e3", "#f2bf5e", "#ef6f6c", "#7b6ee6"];
const RISK_COLORS = {
  low: "#25b381",
  medium: "#f2bf5e",
  high: "#d16666",
};

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function formatPrice(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value);
}

export function PortfolioPage() {
  const navigate = useNavigate();
  const [groupedPortfolio, setGroupedPortfolio] = useState([]);
  const [insights, setInsights] = useState({
    risk_breakdown: { low: 0, medium: 0, high: 0 },
    top_gainers: [],
    top_losers: [],
  });
  const [error, setError] = useState("");

  async function load() {
    try {
      const [groupedData, insightsData] = await Promise.all([
        portfolioApi.groupedSectorPortfolio(),
        portfolioApi.portfolioInsights(),
      ]);
      setGroupedPortfolio(Array.isArray(groupedData) ? groupedData : []);
      setInsights(
        insightsData || {
          risk_breakdown: { low: 0, medium: 0, high: 0 },
          top_gainers: [],
          top_losers: [],
        },
      );
      setError("");
    } catch (err) {
      setError(err.message);
      setGroupedPortfolio([]);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const chartData = useMemo(() => {
    const total = groupedPortfolio.reduce((sum, group) => sum + group.items.length, 0) || 1;
    return groupedPortfolio.map((group) => ({
      name: group.sector.name,
      value: group.items.length,
      percentage: Math.round((group.items.length / total) * 100),
    }));
  }, [groupedPortfolio]);

  const sectorCards = useMemo(
    () => groupedPortfolio.map((group) => ({
      id: group.sector.id,
      name: group.sector.name,
      market: group.sector.market,
      count: group.items.length,
    })),
    [groupedPortfolio],
  );

  const riskItems = useMemo(
    () => [
      { key: "low", label: "Low Risk", value: insights.risk_breakdown?.low || 0 },
      { key: "medium", label: "Medium Risk", value: insights.risk_breakdown?.medium || 0 },
      { key: "high", label: "High Risk", value: insights.risk_breakdown?.high || 0 },
    ],
    [insights],
  );

  return (
    <>
      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Portfolio Studio</p>
            <h1 style={{ marginBottom: 6 }}>Portfolio Management</h1>
            <p className="muted" style={{ margin: 0 }}>
              Stocks added from the Stocks Browser are grouped automatically into sectors here.
            </p>
          </div>
          <div style={{ display: "flex", gap: 14, flexWrap: "wrap", justifyContent: "flex-end" }}>
            <button
              type="button"
              onClick={() => navigate("/stocks")}
              style={{
                minWidth: 220,
                padding: "16px 18px",
                borderRadius: 20,
                background: "linear-gradient(135deg, rgba(17, 75, 95, 0.08), rgba(26, 147, 111, 0.12))",
                border: "1px solid rgba(17, 75, 95, 0.08)",
                cursor: "pointer",
                textAlign: "left",
              }}
            >
              <p className="muted" style={{ margin: 0 }}>Stocks Browser</p>
              <p style={{ margin: "6px 0 0", fontSize: 18, fontWeight: 700 }}>Add More Stocks</p>
            </button>
            <div
              style={{
                minWidth: 220,
                padding: "16px 18px",
                borderRadius: 20,
                background: "linear-gradient(135deg, rgba(17, 75, 95, 0.08), rgba(26, 147, 111, 0.12))",
                border: "1px solid rgba(17, 75, 95, 0.08)",
              }}
            >
              <p className="muted" style={{ margin: 0 }}>Sectors</p>
              <p style={{ margin: "6px 0 0", fontSize: 32, fontWeight: 700 }}>{sectorCards.length}</p>
            </div>
          </div>
        </div>
        {error ? <p>{error}</p> : null}
      </section>

      <section className="grid two">
        <div className="panel">
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", flexWrap: "wrap", marginBottom: 12 }}>
            <div>
              <h3 style={{ margin: 0 }}>Portfolio Analysis</h3>
              <p className="muted" style={{ margin: "8px 0 0" }}>Snapshot of portfolio distribution by sector.</p>
            </div>
          </div>

          {chartData.length ? (
            <>
              <div style={{ height: 250 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={56} outerRadius={96} paddingAngle={2}>
                      {chartData.map((entry, index) => (
                        <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} stroke="#ffffff" strokeWidth={3} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value, _name, entry) => [`${value} stocks`, entry.payload.name]} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div style={{ display: "grid", gap: 10 }}>
                {chartData.map((item, index) => (
                  <div key={item.name} style={{ display: "grid", gridTemplateColumns: "16px 1fr auto", gap: 10, alignItems: "center" }}>
                    <span style={{ width: 12, height: 12, borderRadius: 999, background: CHART_COLORS[index % CHART_COLORS.length] }} />
                    <span className="muted">{item.name}</span>
                    <strong>{item.value} ({item.percentage}%)</strong>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div
              style={{
                minHeight: 260,
                display: "grid",
                placeItems: "center",
                borderRadius: 22,
                background: "linear-gradient(135deg, rgba(17, 75, 95, 0.05), rgba(26, 147, 111, 0.09))",
                border: "1px dashed rgba(17, 75, 95, 0.16)",
                textAlign: "center",
                padding: 24,
              }}
            >
              <p className="muted" style={{ margin: 0 }}>Add stocks from the Stocks page to generate analysis.</p>
            </div>
          )}
        </div>

        <div className="panel">
          <div style={{ marginBottom: 16 }}>
            <h3 style={{ margin: 0 }}>Risk Breakdown + Top Movers</h3>
            <p className="muted" style={{ margin: "8px 0 0" }}>
              Quick read on stability and the stocks currently moving your portfolio the most.
            </p>
          </div>

          <div style={{ display: "grid", gap: 14 }}>
            {riskItems.map((item) => (
              <div
                key={item.key}
                style={{
                  padding: "14px 16px",
                  borderRadius: 16,
                  background: "rgba(255, 255, 255, 0.72)",
                  border: "1px solid rgba(17, 75, 95, 0.08)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ width: 12, height: 12, borderRadius: 999, background: RISK_COLORS[item.key] }} />
                  <span>{item.label}</span>
                </div>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>

          <div style={{ display: "grid", gap: 18, marginTop: 20 }}>
            <div>
              <h4 style={{ margin: "0 0 10px" }}>Top Gainers</h4>
              {!insights.top_gainers?.length ? (
                <p className="muted" style={{ margin: 0 }}>No mover data yet.</p>
              ) : (
                <div style={{ display: "grid", gap: 10 }}>
                  {insights.top_gainers.map((item) => (
                    <button
                      key={`gainer-${item.entry_id}`}
                      type="button"
                      onClick={() => navigate(`/stock/${encodeURIComponent(item.symbol)}`)}
                      style={{
                        padding: "12px 14px",
                        borderRadius: 14,
                        background: "rgba(37, 179, 129, 0.08)",
                        border: "1px solid rgba(37, 179, 129, 0.18)",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        cursor: "pointer",
                        textAlign: "left",
                      }}
                    >
                      <div>
                        <strong>{item.symbol}</strong>
                        <p className="muted" style={{ margin: "6px 0 0" }}>{item.name}</p>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <strong style={{ color: "#25b381" }}>{formatPercent(item.change_pct)}</strong>
                        <p className="muted" style={{ margin: "6px 0 0" }}>{formatPrice(item.current_price)}</p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div>
              <h4 style={{ margin: "0 0 10px" }}>Top Losers</h4>
              {!insights.top_losers?.length ? (
                <p className="muted" style={{ margin: 0 }}>No mover data yet.</p>
              ) : (
                <div style={{ display: "grid", gap: 10 }}>
                  {insights.top_losers.map((item) => (
                    <button
                      key={`loser-${item.entry_id}`}
                      type="button"
                      onClick={() => navigate(`/stock/${encodeURIComponent(item.symbol)}`)}
                      style={{
                        padding: "12px 14px",
                        borderRadius: 14,
                        background: "rgba(209, 102, 102, 0.08)",
                        border: "1px solid rgba(209, 102, 102, 0.18)",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        cursor: "pointer",
                        textAlign: "left",
                      }}
                    >
                      <div>
                        <strong>{item.symbol}</strong>
                        <p className="muted" style={{ margin: "6px 0 0" }}>{item.name}</p>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <strong style={{ color: "#d16666" }}>{formatPercent(item.change_pct)}</strong>
                        <p className="muted" style={{ margin: "6px 0 0" }}>{formatPrice(item.current_price)}</p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="panel">
        <h3>Sectors</h3>
        {!sectorCards.length ? (
          <p className="muted">No sectors added yet.</p>
        ) : (
          <div style={{ display: "grid", gap: 12 }}>
            {sectorCards.map((sector) => (
              <button
                key={sector.id}
                type="button"
                onClick={() => navigate(`/portfolio/sector/${encodeURIComponent(sector.name)}`)}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 16,
                  padding: "16px 18px",
                  borderRadius: 18,
                  border: "1px solid rgba(17, 75, 95, 0.08)",
                  background: "rgba(255, 255, 255, 0.72)",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                <div>
                  <p style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>{sector.name}</p>
                  <p className="muted" style={{ margin: "6px 0 0" }}>
                    {sector.count} stock{sector.count === 1 ? "" : "s"} · {sector.market}
                  </p>
                </div>
                <span style={{ fontSize: 20 }}>&rarr;</span>
              </button>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
