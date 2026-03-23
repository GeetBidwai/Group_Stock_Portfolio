import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { portfolioApi } from "../services/portfolioApi";

const CHART_COLORS = ["#60dbe8", "#43b6d5", "#388fbe", "#1f6f9b", "#8be0ee", "#0f9ca7"];

export function PortfolioAnalysisPage() {
  const [portfolios, setPortfolios] = useState([]);
  const [activeSector, setActiveSector] = useState("");
  const [error, setError] = useState("");

  async function load() {
    try {
      const portfolioData = await portfolioApi.listTypes();
      setPortfolios(portfolioData);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const chartData = useMemo(() => {
    const buckets = portfolios.reduce((accumulator, portfolio) => {
      const key = portfolio.sector_name || "Unassigned";
      accumulator[key] = (accumulator[key] || 0) + 1;
      return accumulator;
    }, {});

    return Object.entries(buckets).map(([name, value]) => ({ name, value }));
  }, [portfolios]);

  useEffect(() => {
    if (!chartData.length) {
      setActiveSector("");
      return;
    }
    if (!chartData.some((item) => item.name === activeSector)) {
      setActiveSector(chartData[0].name);
    }
  }, [activeSector, chartData]);

  const visiblePortfolios = activeSector
    ? portfolios.filter((portfolio) => (portfolio.sector_name || "Unassigned") === activeSector)
    : portfolios;

  return (
    <>
      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Sector Allocation</p>
            <h1 style={{ marginBottom: 6 }}>Portfolio Analysis</h1>
            <p className="muted" style={{ margin: 0 }}>Use the chart to inspect sector concentration and review which portfolios sit inside each slice.</p>
          </div>
          <Link
            to="/portfolio"
            style={{
              padding: "12px 16px",
              borderRadius: 14,
              border: "1px solid rgba(17, 75, 95, 0.12)",
              background: "rgba(255, 255, 255, 0.72)",
            }}
          >
            ← Back to Portfolio
          </Link>
        </div>
        {error && <p>{error}</p>}
      </section>

      <section className="panel" style={{ padding: 0, overflow: "hidden" }}>
        {!chartData.length ? (
          <div style={{ padding: 32 }}>
            <p className="muted" style={{ margin: 0 }}>No portfolios are available yet to analyze.</p>
          </div>
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "minmax(320px, 1.2fr) minmax(280px, 1fr)",
              minHeight: 480,
            }}
          >
            <div
              style={{
                padding: 24,
                background: "linear-gradient(180deg, rgba(202, 238, 246, 0.5), rgba(255, 255, 255, 0.55))",
                borderRight: "1px solid rgba(17, 75, 95, 0.12)",
              }}
            >
              <div style={{ height: 430 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={170}
                      innerRadius={0}
                      paddingAngle={1}
                      activeIndex={chartData.findIndex((item) => item.name === activeSector)}
                      activeShape={{ stroke: "#ffffff", strokeWidth: 4 }}
                      onClick={(_, index) => setActiveSector(chartData[index]?.name || "")}
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} stroke="#ffffff" strokeWidth={2} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div style={{ padding: 24 }}>
              <div style={{ display: "grid", gap: 18 }}>
                {chartData.map((item, index) => (
                  <button
                    key={item.name}
                    type="button"
                    onClick={() => setActiveSector(item.name)}
                    style={{
                      display: "grid",
                      gridTemplateColumns: "20px 1fr auto",
                      gap: 12,
                      alignItems: "center",
                      border: 0,
                      background: activeSector === item.name ? "rgba(17, 75, 95, 0.08)" : "transparent",
                      borderRadius: 14,
                      padding: "12px 10px",
                      cursor: "pointer",
                      textAlign: "left",
                    }}
                  >
                    <span style={{ width: 12, height: 12, borderRadius: 999, background: CHART_COLORS[index % CHART_COLORS.length] }} />
                    <span>{item.name}</span>
                    <span>{item.value}</span>
                  </button>
                ))}
              </div>

              <div style={{ marginTop: 24, paddingTop: 20, borderTop: "1px solid rgba(17, 75, 95, 0.12)" }}>
                <h3 style={{ marginTop: 0 }}>{activeSector || "Selected Sector"}</h3>
                <div style={{ display: "grid", gap: 10 }}>
                  {visiblePortfolios.map((portfolio) => (
                    <div
                      key={portfolio.id}
                      style={{
                        padding: "14px 16px",
                        borderRadius: 14,
                        background: "rgba(255, 255, 255, 0.82)",
                        border: "1px solid rgba(17, 75, 95, 0.08)",
                      }}
                    >
                      <p style={{ margin: 0, fontWeight: 700 }}>{portfolio.name}</p>
                      <p className="muted" style={{ margin: "6px 0 0" }}>{portfolio.description || "No description provided."}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </section>
    </>
  );
}
