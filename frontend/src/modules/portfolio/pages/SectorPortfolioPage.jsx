import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { portfolioApi } from "../services/portfolioApi";

export function SectorPortfolioPage() {
  const navigate = useNavigate();
  const { sectorName } = useParams();
  const decodedSectorName = decodeURIComponent(sectorName);
  const [groupedPortfolio, setGroupedPortfolio] = useState([]);
  const [removingEntryId, setRemovingEntryId] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    try {
      const groupedData = await portfolioApi.groupedSectorPortfolio();
      setGroupedPortfolio(Array.isArray(groupedData) ? groupedData : []);
      setError("");
    } catch (err) {
      setError(err.message);
      setGroupedPortfolio([]);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const sectorGroup = useMemo(
    () => groupedPortfolio.find((group) => group.sector.name === decodedSectorName) || null,
    [decodedSectorName, groupedPortfolio],
  );

  async function handleRemove(event, entryId) {
    event.stopPropagation();
    try {
      setRemovingEntryId(entryId);
      setError("");
      await portfolioApi.removeGroupedSectorEntry(entryId);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setRemovingEntryId(null);
    }
  }

  return (
    <>
      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Sector Level</p>
            <h1 style={{ marginBottom: 6 }}>{decodedSectorName}</h1>
            <p className="muted" style={{ margin: 0 }}>Click any stock to open the full detail view.</p>
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
            &larr; Back to Sectors
          </Link>
        </div>
        {error ? <p>{error}</p> : null}
      </section>

      <section className="panel">
        <h3>Stocks</h3>
        {!sectorGroup?.items?.length ? (
          <p className="muted">No stocks added in this sector yet.</p>
        ) : (
          <div style={{ display: "grid", gap: 12 }}>
            {sectorGroup.items.map((item) => (
              <div
                key={item.id}
                onClick={() => navigate(`/stock/${encodeURIComponent(item.symbol)}`)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    navigate(`/stock/${encodeURIComponent(item.symbol)}`);
                  }
                }}
                role="button"
                tabIndex={0}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
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
                  <p style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>{item.symbol}</p>
                  <p className="muted" style={{ margin: "6px 0 0" }}>{item.name}</p>
                  <p className="muted" style={{ margin: "6px 0 0" }}>{item.exchange || "-"}</p>
                </div>
                <button
                  type="button"
                  className="btn"
                  onClick={(event) => handleRemove(event, item.id)}
                  disabled={removingEntryId === item.id}
                  style={{ minWidth: 120 }}
                >
                  {removingEntryId === item.id ? "Removing..." : "Remove"}
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
