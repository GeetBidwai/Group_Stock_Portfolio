import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { RecommendationModal } from "../../recommendations/components/RecommendationModal";
import { qualityStocksApi } from "../../quality-stocks/services/qualityStocksApi";
import { Card, ChartCard, MetricCard } from "../../../components/ui/Card";
import { portfolioApi } from "../services/portfolioApi";

const CHART_COLORS = ["#2563eb", "#0ea5e9", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"];
const RISK_COLORS = {
  low: "#22c55e",
  medium: "#f59e0b",
  high: "#ef4444",
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

function sectorIcon(name) {
  if (name.includes("Bank")) return "🏦";
  if (name.includes("Energy")) return "⚡";
  if (name.includes("Auto")) return "🚗";
  if (name.includes("Metal")) return "⛏️";
  if (name.includes("IT")) return "💻";
  if (name.includes("MNC")) return "🚀";
  if (name.includes("Media")) return "📺";
  return "📊";
}

export function PortfolioPage() {
  const navigate = useNavigate();
  const [groupedPortfolio, setGroupedPortfolio] = useState([]);
  const [qualityReports, setQualityReports] = useState([]);
  const [insights, setInsights] = useState({
    risk_breakdown: { low: 0, medium: 0, high: 0 },
    top_gainers: [],
    top_losers: [],
  });
  const [isRecommendationOpen, setIsRecommendationOpen] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    try {
      const [groupedData, insightsData, qualityData] = await Promise.all([
        portfolioApi.groupedSectorPortfolio(),
        portfolioApi.portfolioInsights(),
        qualityStocksApi.list(),
      ]);
      setGroupedPortfolio(Array.isArray(groupedData) ? groupedData : []);
      setQualityReports(Array.isArray(qualityData) ? qualityData : []);
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
      setQualityReports([]);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const totalHoldings = useMemo(
    () => groupedPortfolio.reduce((sum, group) => sum + group.items.length, 0),
    [groupedPortfolio],
  );

  const chartData = useMemo(() => {
    const total = totalHoldings || 1;
    return groupedPortfolio.map((group) => ({
      name: group.sector.name,
      value: group.items.length,
      percentage: Math.round((group.items.length / total) * 100),
    }));
  }, [groupedPortfolio, totalHoldings]);

  const sectorCards = useMemo(() => {
    const total = totalHoldings || 1;
    return groupedPortfolio.map((group) => {
      const qualityCount = qualityReports.filter(
        (item) => String(item.portfolio_name || "").trim().toLowerCase() === String(group.sector.name || "").trim().toLowerCase(),
      ).length;
      return {
        id: group.sector.id,
        name: group.sector.name,
        market: group.sector.market,
        marketCode: group.sector.market_code || "IN",
        count: group.items.length,
        mixPercent: Math.round((group.items.length / total) * 100),
        qualityCount,
      };
    });
  }, [groupedPortfolio, qualityReports, totalHoldings]);

  const riskItems = useMemo(
    () => [
      { key: "low", label: "Low Risk", value: insights.risk_breakdown?.low || 0 },
      { key: "medium", label: "Medium Risk", value: insights.risk_breakdown?.medium || 0 },
      { key: "high", label: "High Risk", value: insights.risk_breakdown?.high || 0 },
    ],
    [insights],
  );

  const riskScore = useMemo(() => {
    if (!totalHoldings) {
      return 0;
    }
    const score = ((riskItems[0].value * 1) + (riskItems[1].value * 2) + (riskItems[2].value * 3)) / totalHoldings;
    return score.toFixed(1);
  }, [riskItems, totalHoldings]);

  const strongestMover = insights.top_gainers?.[0] || insights.top_losers?.[0] || null;

  return (
    <>
      <div className="portfolio-page">
        <Card className="portfolio-hero">
          <div className="portfolio-hero__header">
            <div>
              <p className="eyebrow">Portfolio Studio</p>
              <h1 style={{ marginBottom: 6 }}>Portfolio Management</h1>
              <p className="muted" style={{ margin: 0 }}>
                Stocks added from the browser are grouped automatically into cleaner sector cards and analytics blocks.
              </p>
            </div>
            <div className="portfolio-hero__actions">
              <button type="button" className="portfolio-action" onClick={() => setIsRecommendationOpen(true)}>
                <span className="muted">Insights</span>
                <p className="portfolio-action__value">Recommendations</p>
                <span className="muted">Open portfolio recommendation modal</span>
              </button>
              <button type="button" className="portfolio-action" onClick={() => navigate("/quality-stocks")}>
                <span className="muted">Research</span>
                <p className="portfolio-action__value">Quality Stocks</p>
                <span className="muted">Review AI research reports</span>
              </button>
            </div>
          </div>

          <div className="metric-grid">
            <MetricCard label="Total Holdings" value={totalHoldings} meta="Live from your grouped portfolio" tone="primary" />
            <MetricCard label="Active Sectors" value={sectorCards.length} meta="Current sector allocations" tone="primary" />
            <MetricCard label="Risk Score" value={riskScore} meta="Derived from low, medium, high mix" tone="danger" />
            <MetricCard
              label="Quality Reports"
              value={qualityReports.length}
              meta={strongestMover ? `Top mover: ${strongestMover.symbol} ${formatPercent(strongestMover.change_pct)}` : "Research coverage across portfolios"}
              tone="success"
            />
          </div>

          {error ? <p className="form-error">{error}</p> : null}
        </Card>

        <div className="portfolio-analytics">
          <ChartCard
            className="portfolio-chart"
            title="Portfolio Allocation"
            description="Sector distribution is the main visual focus in the upgraded portfolio view."
          >
            {chartData.length ? (
              <>
                <div style={{ height: 280 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
                      <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={68} outerRadius={108} paddingAngle={3}>
                        {chartData.map((entry, index) => (
                          <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} stroke="#ffffff" strokeWidth={3} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          borderRadius: 14,
                          border: "1px solid #e2e8f0",
                          boxShadow: "0 8px 24px rgba(15, 23, 42, 0.12)",
                        }}
                        formatter={(value, _name, entry) => [`${value} stocks`, entry.payload.name]}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="chart-legend">
                  {chartData.map((item, index) => (
                    <div key={item.name} className="chart-legend__item">
                      <span className="chart-legend__dot" style={{ background: CHART_COLORS[index % CHART_COLORS.length] }} />
                      <span className="muted">{item.name}</span>
                      <strong>{item.value} ({item.percentage}%)</strong>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="chart-empty">
                <p className="muted" style={{ margin: 0 }}>Add stocks from the Stocks page to unlock portfolio allocation analytics.</p>
              </div>
            )}
          </ChartCard>

          <Card>
            <div className="card__header">
              <div>
                <h3 className="card__title">Risk Breakdown + Movers</h3>
                <p className="card__description">A cleaner side panel for portfolio stability and the strongest daily moves.</p>
              </div>
            </div>

            <div className="risk-list">
              {riskItems.map((item) => (
                <div key={item.key} className="risk-row">
                  <div className="risk-row__left">
                    <span className="risk-row__dot" style={{ background: RISK_COLORS[item.key] }} />
                    <span>{item.label}</span>
                  </div>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>

            <div className="movers-list">
              <div>
                <h4 style={{ margin: "0 0 10px" }}>Top Gainer</h4>
                {!insights.top_gainers?.length ? (
                  <p className="muted" style={{ margin: 0 }}>No positive mover right now.</p>
                ) : (
                  insights.top_gainers.map((item) => (
                    <button
                      key={`gainer-${item.entry_id}`}
                      type="button"
                      className="mover-card mover-card--gain"
                      onClick={() => navigate(`/stock/${encodeURIComponent(item.symbol)}`)}
                    >
                      <div>
                        <strong>{item.symbol}</strong>
                        <p className="muted" style={{ margin: "6px 0 0" }}>{item.name}</p>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <strong style={{ color: RISK_COLORS.low }}>{formatPercent(item.change_pct)}</strong>
                        <p className="muted" style={{ margin: "6px 0 0" }}>{formatPrice(item.current_price)}</p>
                      </div>
                    </button>
                  ))
                )}
              </div>

              <div>
                <h4 style={{ margin: "0 0 10px" }}>Top Loser</h4>
                {!insights.top_losers?.length ? (
                  <p className="muted" style={{ margin: 0 }}>No negative mover right now.</p>
                ) : (
                  insights.top_losers.map((item) => (
                    <button
                      key={`loser-${item.entry_id}`}
                      type="button"
                      className="mover-card mover-card--loss"
                      onClick={() => navigate(`/stock/${encodeURIComponent(item.symbol)}`)}
                    >
                      <div>
                        <strong>{item.symbol}</strong>
                        <p className="muted" style={{ margin: "6px 0 0" }}>{item.name}</p>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <strong style={{ color: RISK_COLORS.high }}>{formatPercent(item.change_pct)}</strong>
                        <p className="muted" style={{ margin: "6px 0 0" }}>{formatPrice(item.current_price)}</p>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </Card>
        </div>

        <Card>
          <div className="card__header">
            <div>
              <h3 className="card__title">Sector Cards</h3>
              <p className="card__description">Each sector is now presented as a cleaner card with quick actions and quality coverage.</p>
            </div>
          </div>

          {!sectorCards.length ? (
            <p className="muted">No sectors added yet.</p>
          ) : (
            <div className="sector-grid">
              {sectorCards.map((sector) => (
                <Card key={sector.id} as="article" className="sector-card" interactive>
                  <div className="sector-card__top">
                    <div style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
                      <div className="sector-card__icon">{sectorIcon(sector.name)}</div>
                      <div>
                        <div className="sector-card__title-row">
                          <p style={{ margin: 0, fontSize: 18, fontWeight: 800 }}>{sector.name}</p>
                          <span className="badge">[{sector.marketCode}]</span>
                          <span className="badge badge--primary">QS {sector.qualityCount}</span>
                        </div>
                        <p className="muted" style={{ margin: "6px 0 0" }}>
                          {sector.market} holdings currently mapped into this portfolio segment.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="sector-card__progress">
                    <div className="sector-card__stats">
                      <span className="muted">Portfolio coverage</span>
                      <strong>{sector.mixPercent}% mix</strong>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-bar__fill" style={{ width: `${sector.mixPercent}%` }} />
                    </div>
                    <div className="sector-card__stats">
                      <span className="muted">{sector.count} stocks</span>
                      <span className="muted">{sector.qualityCount} quality reports</span>
                    </div>
                  </div>

                  <div className="sector-card__actions">
                    <button
                      type="button"
                      className="btn"
                      onClick={() => navigate(`/portfolio/sector/${encodeURIComponent(sector.name)}`)}
                    >
                      Open Stocks
                    </button>
                    <button
                      type="button"
                      className="ghost-btn"
                      onClick={() => navigate(`/quality-stocks?portfolio=${encodeURIComponent(`sector:${sector.id}`)}`)}
                    >
                      Quality
                    </button>
                    <button type="button" className="ghost-btn" onClick={() => navigate("/clustering")}>
                      Clusters
                    </button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </Card>
      </div>

      <RecommendationModal
        isOpen={isRecommendationOpen}
        onClose={() => setIsRecommendationOpen(false)}
      />
    </>
  );
}
