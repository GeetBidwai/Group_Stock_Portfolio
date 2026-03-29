import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { Card, MetricCard } from "../components/ui/Card";
import { portfolioApi } from "../modules/portfolio/services/portfolioApi";
import { qualityStocksApi } from "../modules/quality-stocks/services/qualityStocksApi";

function signalTone(buySignal) {
  if (buySignal === "BUY") return "Positive";
  if (buySignal === "SELL") return "Negative";
  return "Neutral";
}

function miniSeries(score) {
  const base = Number(score) || 0;
  return [Math.max(base - 2, 1), Math.max(base - 1, 1), Math.max(base, 1), Math.min(base + 1, 10)].map((value, index) => ({
    id: index,
    value: Math.max(12, value * 10),
  }));
}

export function QualityStocksPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState("");
  const [allReports, setAllReports] = useState([]);
  const [savedReports, setSavedReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadPortfolios() {
      try {
        const [portfolioTypeData, groupedPortfolioData] = await Promise.all([
          portfolioApi.listTypes(),
          portfolioApi.groupedSectorPortfolio(),
        ]);
        if (cancelled) {
          return;
        }

        const nextPortfolioTypes = Array.isArray(portfolioTypeData) ? portfolioTypeData : [];
        const groupedPortfolios = Array.isArray(groupedPortfolioData) ? groupedPortfolioData : [];

        const nextPortfolios = nextPortfolioTypes.length
          ? nextPortfolioTypes.map((item) => ({
              id: String(item.id),
              name: item.name,
              source: "portfolioType",
            }))
          : groupedPortfolios.map((group) => ({
              id: `sector:${group.sector.id}`,
              name: group.sector.name,
              source: "groupedSector",
            }));

        setPortfolios(nextPortfolios);

        const requestedId = searchParams.get("portfolio") || "";
        const requestedExists = nextPortfolios.some((item) => item.id === requestedId);
        const initialId = requestedExists ? requestedId : nextPortfolios[0]?.id || "";

        setSelectedPortfolioId(initialId);
        setError("");
      } catch (_err) {
        if (!cancelled) {
          setPortfolios([]);
          setSelectedPortfolioId("");
          setError("Failed to fetch analysis");
        }
      }
    }

    loadPortfolios();
    return () => {
      cancelled = true;
    };
  }, [searchParams]);

  useEffect(() => {
    if (!selectedPortfolioId) {
      setAllReports([]);
      setSavedReports([]);
      setLoading(false);
      return;
    }

    const selected = portfolios.find((item) => item.id === selectedPortfolioId);
    if (!selected) {
      setAllReports([]);
      setSavedReports([]);
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function loadReports() {
      try {
        setLoading(true);
        const reports = selected.source === "portfolioType"
          ? await qualityStocksApi.list(Number(selectedPortfolioId))
          : await qualityStocksApi.list();

        if (!cancelled) {
          const nextReports = Array.isArray(reports) ? reports : [];
          setAllReports(nextReports);
          setError("");
        }
      } catch (_err) {
        if (!cancelled) {
          setAllReports([]);
          setSavedReports([]);
          setError("Failed to fetch analysis");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadReports();
    return () => {
      cancelled = true;
    };
  }, [portfolios, selectedPortfolioId]);

  useEffect(() => {
    const selected = portfolios.find((item) => item.id === selectedPortfolioId);
    if (!selected) {
      setSavedReports([]);
      return;
    }

    if (selected.source === "portfolioType") {
      setSavedReports(allReports);
      return;
    }

    setSavedReports(
      allReports.filter(
        (item) => String(item.portfolio_name || "").trim().toLowerCase() === String(selected.name || "").trim().toLowerCase(),
      ),
    );
  }, [allReports, portfolios, selectedPortfolioId]);

  const selectedPortfolio = useMemo(
    () => portfolios.find((item) => item.id === selectedPortfolioId) || null,
    [portfolios, selectedPortfolioId],
  );

  const topReports = useMemo(
    () => [...savedReports].sort((left, right) => (Number(right.ai_rating) || 0) - (Number(left.ai_rating) || 0)).slice(0, 3),
    [savedReports],
  );

  async function refreshReports() {
    if (!selectedPortfolioId || !selectedPortfolio) {
      setSavedReports([]);
      return;
    }

    const refreshed = selectedPortfolio.source === "portfolioType"
      ? await qualityStocksApi.list(Number(selectedPortfolioId))
      : await qualityStocksApi.list();

    const nextReports = Array.isArray(refreshed) ? refreshed : [];
    setAllReports(nextReports);
  }

  return (
    <>
      <Card className="quality-page-hero">
        <div className="stocks-page-hero__header">
          <div>
            <p className="eyebrow">Portfolio Quality</p>
            <h1 style={{ marginBottom: 6 }}>Quality Stock Analysis</h1>
            <p className="muted" style={{ margin: 0 }}>
              Saved AI-generated research reports for your selected portfolio.
            </p>
          </div>
          <Link to="/portfolio" className="ghost-btn">Back to Portfolio</Link>
        </div>

        <div className="metric-grid">
          <MetricCard label="Portfolios" value={portfolios.length} meta="Available quality research contexts" tone="primary" />
          <MetricCard label="Saved Reports" value={savedReports.length} meta={selectedPortfolio?.name || "Choose a portfolio"} tone="primary" />
          <MetricCard label="Top Score" value={topReports[0] ? `${topReports[0].ai_rating}/10` : "--"} meta={topReports[0]?.stock_symbol || "No reports yet"} tone="success" />
        </div>
      </Card>

      <Card>
        <label className="stocks-page-hero__select" style={{ maxWidth: 340 }}>
          <span className="muted" style={{ fontSize: 13 }}>Portfolio</span>
          <select
            value={selectedPortfolioId}
            onChange={(event) => {
              const value = event.target.value;
              setSelectedPortfolioId(value);
              setSearchParams((current) => {
                const next = new URLSearchParams(current);
                if (value) {
                  next.set("portfolio", value);
                } else {
                  next.delete("portfolio");
                }
                return next;
              });
            }}
          >
            <option value="">Select portfolio</option>
            {portfolios.map((portfolio) => (
              <option key={portfolio.id} value={portfolio.id}>
                {portfolio.name}
              </option>
            ))}
          </select>
        </label>

        {!portfolios.length ? (
          <p className="muted" style={{ margin: "12px 0 0" }}>
            No portfolios were found for Quality Stocks yet.
          </p>
        ) : null}

        {selectedPortfolio?.source === "groupedSector" ? (
          <div className="sector-card__progress">
            <p className="muted" style={{ margin: 0 }}>
              This portfolio comes from your sector-based holdings on the Portfolio page. Saved reports shown here are matched to that sector name.
            </p>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <button
                type="button"
                className="ghost-btn"
                onClick={() => navigate(`/portfolio/sector/${encodeURIComponent(selectedPortfolio.name)}`)}
              >
                Open Sector Portfolio
              </button>
            </div>
          </div>
        ) : null}
      </Card>

      <Card>
        <div className="card__header">
          <div>
            <h2 style={{ margin: 0 }}>Top 3 Quality Stocks</h2>
            <p className="muted" style={{ margin: "8px 0 0" }}>
              Highest-rated saved reports for the selected portfolio.
            </p>
          </div>
        </div>

        {!loading && !!topReports.length ? (
          <div className="quality-top-grid">
            {topReports.map((item) => (
              <Card key={`top-${item.id}`} as="article" className="quality-top-card" interactive>
                <div className="sector-card__title-row">
                  <div>
                    <p style={{ margin: 0, fontSize: 18, fontWeight: 800 }}>{item.stock_name || item.stock_symbol}</p>
                    <p className="muted" style={{ margin: "6px 0 0" }}>{item.stock_symbol}</p>
                  </div>
                  <span className="badge badge--primary">{item.ai_rating}/10</span>
                </div>
                <div className="sector-card__stats">
                  <span className="badge">{signalTone(item.buy_signal)}</span>
                  <span className="muted">{item.buy_signal}</span>
                </div>
                <div className="quality-mini-chart" aria-hidden="true">
                  {miniSeries(item.ai_rating).map((bar) => (
                    <span key={bar.id} className="quality-mini-chart__bar" style={{ height: `${bar.value}%` }} />
                  ))}
                </div>
                <p className="muted" style={{ margin: 0 }}>{item.explanation || "No explanation available."}</p>
              </Card>
            ))}
          </div>
        ) : (
          !loading ? <p className="muted" style={{ margin: 0 }}>No saved reports yet.</p> : null
        )}
      </Card>

      <Card>
        <div className="card__header">
          <div>
            <h2 style={{ margin: 0 }}>Saved Reports</h2>
            <p className="muted" style={{ margin: "8px 0 0" }}>
              {selectedPortfolioId
                ? `Saved quality reports for ${selectedPortfolio?.name || "the selected portfolio"}.`
                : "Choose a portfolio to review generated reports."}
            </p>
          </div>
        </div>

        {loading ? <p style={{ margin: 0 }}>Loading saved reports...</p> : null}
        {!loading && error ? <p className="form-error">{error}</p> : null}
        {!loading && selectedPortfolioId && !savedReports.length ? <p style={{ margin: 0 }}>No saved reports yet.</p> : null}

        {!loading && !!savedReports.length ? (
          <div className="quality-report-list">
            {savedReports.map((item) => (
              <article key={item.id} className="quality-report-card">
                <div>
                  <div className="sector-card__title-row">
                    <p style={{ margin: 0, fontWeight: 700, fontSize: 18 }}>{item.stock_name || item.stock_symbol}</p>
                    <span className="badge badge--primary">{item.ai_rating}/10</span>
                  </div>
                  <p className="muted" style={{ margin: "6px 0 0" }}>
                    {item.stock_symbol} · {item.buy_signal} · Predicted Price: {item.predicted_price ?? "N/A"}
                  </p>
                  <p className="muted" style={{ margin: "6px 0 0" }}>
                    {item.explanation || "No explanation available."}
                  </p>
                </div>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <button type="button" className="btn" onClick={() => navigate(`/quality-stocks/${item.id}`)}>View Report</button>
                  <button
                    type="button"
                    className="ghost-btn"
                    onClick={async () => {
                      await qualityStocksApi.rerun(item.id);
                      await refreshReports();
                    }}
                  >
                    Re-run
                  </button>
                  <button
                    type="button"
                    className="ghost-btn"
                    onClick={async () => {
                      await qualityStocksApi.remove(item.id);
                      setAllReports((current) => current.filter((report) => report.id !== item.id));
                    }}
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        ) : null}
      </Card>
    </>
  );
}
