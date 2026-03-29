import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { portfolioApi } from "../modules/portfolio/services/portfolioApi";
import { qualityStocksApi } from "../modules/quality-stocks/services/qualityStocksApi";

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
      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Portfolio Quality</p>
            <h1 style={{ marginBottom: 6 }}>Quality Stock Analysis</h1>
            <p className="muted" style={{ margin: 0 }}>
              Saved AI-generated research reports for your selected portfolio.
            </p>
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
            Back to Portfolio
          </Link>
        </div>
      </section>

      <section className="panel">
        <label style={{ display: "grid", gap: 8, maxWidth: 340 }}>
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
          <div
            style={{
              marginTop: 16,
              padding: "14px 16px",
              borderRadius: 16,
              background: "rgba(123, 110, 230, 0.08)",
              border: "1px solid rgba(123, 110, 230, 0.16)",
              display: "grid",
              gap: 10,
            }}
          >
            <p className="muted" style={{ margin: 0 }}>
              This portfolio comes from your sector-based holdings on the Portfolio page. Saved reports shown here are matched to that sector name.
            </p>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <button
                type="button"
                onClick={() => navigate(`/portfolio/sector/${encodeURIComponent(selectedPortfolio.name)}`)}
              >
                Open Sector Portfolio
              </button>
            </div>
          </div>
        ) : null}
      </section>

      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap", marginBottom: 16 }}>
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
        {!loading && error ? <p style={{ margin: 0 }}>{error}</p> : null}
        {!loading && selectedPortfolioId && !savedReports.length ? <p style={{ margin: 0 }}>No saved reports yet.</p> : null}

        {!loading && !!savedReports.length ? (
          <div style={{ display: "grid", gap: 12 }}>
            {savedReports.map((item) => (
              <article
                key={item.id}
                style={{
                  padding: "16px 18px",
                  borderRadius: 16,
                  border: "1px solid rgba(17, 75, 95, 0.08)",
                  background: "rgba(255,255,255,0.78)",
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 16,
                  alignItems: "center",
                  flexWrap: "wrap",
                }}
              >
                <div>
                  <p style={{ margin: 0, fontWeight: 700, fontSize: 18 }}>{item.stock_name || item.stock_symbol}</p>
                  <p className="muted" style={{ margin: "6px 0 0" }}>
                    {item.stock_symbol} · AI Rating {item.ai_rating}/10 · {item.buy_signal}
                  </p>
                  <p className="muted" style={{ margin: "6px 0 0" }}>
                    Predicted Price: {item.predicted_price ?? "N/A"}
                  </p>
                  <p className="muted" style={{ margin: "6px 0 0" }}>
                    {item.explanation || "No explanation available."}
                  </p>
                </div>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <button type="button" onClick={() => navigate(`/quality-stocks/${item.id}`)}>View Report</button>
                  <button
                    type="button"
                    onClick={async () => {
                      await qualityStocksApi.rerun(item.id);
                      await refreshReports();
                    }}
                  >
                    Re-run
                  </button>
                  <button
                    type="button"
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
      </section>
    </>
  );
}
