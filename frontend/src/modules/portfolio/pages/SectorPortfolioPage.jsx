import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { portfolioApi } from "../services/portfolioApi";

export function SectorPortfolioPage() {
  const navigate = useNavigate();
  const { sectorName } = useParams();
  const decodedSectorName = decodeURIComponent(sectorName);
  const [portfolios, setPortfolios] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [error, setError] = useState("");

  async function load() {
    try {
      const [portfolioData, stockData] = await Promise.all([
        portfolioApi.listTypes(),
        portfolioApi.listStocks(),
      ]);
      setPortfolios(portfolioData);
      setStocks(stockData);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const stockCountByPortfolio = useMemo(() => {
    return stocks.reduce((accumulator, stock) => {
      accumulator[stock.portfolio_type] = (accumulator[stock.portfolio_type] || 0) + 1;
      return accumulator;
    }, {});
  }, [stocks]);

  const filteredPortfolios = useMemo(
    () => portfolios.filter((portfolio) => (portfolio.sector_name || "Unassigned") === decodedSectorName),
    [decodedSectorName, portfolios],
  );

  return (
    <>
      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Sector Level</p>
            <h1 style={{ marginBottom: 6 }}>{decodedSectorName}</h1>
            <p className="muted" style={{ margin: 0 }}>Portfolios grouped under this sector.</p>
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
            ← Back to Sectors
          </Link>
        </div>
        {error && <p>{error}</p>}
      </section>

      <section className="panel">
        <h3>Portfolios</h3>
        {!filteredPortfolios.length ? (
          <p className="muted">No portfolios in this sector.</p>
        ) : (
          <div style={{ display: "grid", gap: 12 }}>
            {filteredPortfolios.map((portfolio) => (
              <button
                key={portfolio.id}
                type="button"
                onClick={() => navigate(`/portfolio/${portfolio.id}`)}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 16,
                  padding: "16px 18px",
                  borderRadius: 18,
                  border: "1px solid rgba(17, 75, 95, 0.08)",
                  background: "rgba(17, 75, 95, 0.07)",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                <div>
                  <p style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>
                    {portfolio.name} <span className="muted" style={{ fontWeight: 400 }}>({stockCountByPortfolio[portfolio.id] || 0} stocks)</span>
                  </p>
                  <p className="muted" style={{ margin: "6px 0 0" }}>{portfolio.sector_name || decodedSectorName}</p>
                </div>
                <span style={{ fontSize: 20 }}>→</span>
              </button>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
