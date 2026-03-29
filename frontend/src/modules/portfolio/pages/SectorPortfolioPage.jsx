import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { QualityResearchModal } from "../../quality-stocks/components/QualityResearchModal";
import { stocksService } from "../../stocks/stocksService";
import { portfolioApi } from "../services/portfolioApi";

function formatPrice(value, currency = "INR") {
  if (value == null || Number.isNaN(value)) {
    return "Unavailable";
  }
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

const RISK_STYLE = {
  Low: { background: "rgba(37, 179, 129, 0.12)", color: "#25b381" },
  Medium: { background: "rgba(242, 191, 94, 0.16)", color: "#c28719" },
  High: { background: "rgba(209, 102, 102, 0.12)", color: "#d16666" },
  Unknown: { background: "rgba(17, 75, 95, 0.08)", color: "#4f6278" },
};

export function SectorPortfolioPage() {
  const navigate = useNavigate();
  const { sectorName } = useParams();
  const decodedSectorName = decodeURIComponent(sectorName);
  const [groupedPortfolio, setGroupedPortfolio] = useState([]);
  const [portfolioTypes, setPortfolioTypes] = useState([]);
  const [sectorStocks, setSectorStocks] = useState([]);
  const [portfolioRiskItems, setPortfolioRiskItems] = useState([]);
  const [removingEntryId, setRemovingEntryId] = useState(null);
  const [showResearchModal, setShowResearchModal] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    try {
      const [groupedData, typeData, riskData] = await Promise.all([
        portfolioApi.groupedSectorPortfolio(),
        portfolioApi.listTypes(),
        portfolioApi.portfolioRiskList(),
      ]);
      setGroupedPortfolio(Array.isArray(groupedData) ? groupedData : []);
      setPortfolioTypes(Array.isArray(typeData) ? typeData : []);
      setPortfolioRiskItems(Array.isArray(riskData) ? riskData : []);
      setError("");
    } catch (err) {
      setError(err.message);
      setGroupedPortfolio([]);
      setPortfolioTypes([]);
      setPortfolioRiskItems([]);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const sectorGroup = useMemo(
    () => groupedPortfolio.find((group) => group.sector.name === decodedSectorName) || null,
    [decodedSectorName, groupedPortfolio],
  );

  useEffect(() => {
    let cancelled = false;

    async function loadSectorStocks() {
      if (!sectorGroup?.sector?.id) {
        setSectorStocks([]);
        return;
      }
      try {
        const payload = await stocksService.listStocks(sectorGroup.sector.id);
        if (!cancelled) {
          setSectorStocks(Array.isArray(payload?.items) ? payload.items : []);
        }
      } catch (_err) {
        if (!cancelled) {
          setSectorStocks([]);
        }
      }
    }

    loadSectorStocks();
    return () => {
      cancelled = true;
    };
  }, [sectorGroup?.sector?.id]);

  const linkedPortfolioType = useMemo(() => {
    const normalizedSector = String(decodedSectorName || "").trim().toLowerCase();
    return (
      portfolioTypes.find((item) => String(item?.sector_name || "").trim().toLowerCase() === normalizedSector) ||
      portfolioTypes.find((item) => String(item?.name || "").trim().toLowerCase() === normalizedSector) ||
      null
    );
  }, [decodedSectorName, portfolioTypes]);

  const stockSnapshotsBySymbol = useMemo(
    () => Object.fromEntries(sectorStocks.map((item) => [String(item.symbol || "").toUpperCase(), item])),
    [sectorStocks],
  );

  const riskBySymbol = useMemo(
    () => Object.fromEntries(portfolioRiskItems.map((item) => [String(item.symbol || "").toUpperCase(), item])),
    [portfolioRiskItems],
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
            <p className="muted" style={{ margin: 0 }}>
              Explore the stocks in this sector and launch Quality research from here.
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
            ← Back to Sectors
          </Link>
        </div>
        {error ? <p>{error}</p> : null}
      </section>

      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap", marginBottom: 12 }}>
          <div>
            <h3 style={{ margin: 0 }}>Stocks</h3>
            <p className="muted" style={{ margin: "6px 0 0" }}>
              {sectorGroup?.items?.length ? `${sectorGroup.items.length} holdings in this sector.` : "No holdings in this sector yet."}
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowResearchModal(true)}
            disabled={!sectorGroup?.items?.length}
          >
            Research
          </button>
        </div>
        {!sectorGroup?.items?.length ? (
          <p className="muted">No stocks added in this sector yet.</p>
        ) : (
          <div style={{ display: "grid", gap: 14 }}>
            {sectorGroup.items.map((item) => {
              const snapshot = stockSnapshotsBySymbol[String(item.symbol || "").toUpperCase()] || null;
              const riskItem = riskBySymbol[String(item.symbol || "").toUpperCase()] || null;
              const riskLabel = riskItem?.risk || "Unknown";
              const riskStyle = RISK_STYLE[riskLabel] || RISK_STYLE.Unknown;

              return (
                <article
                  key={item.id}
                  role="button"
                  tabIndex={0}
                  onClick={() => navigate(`/stock/${encodeURIComponent(item.symbol)}`)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      navigate(`/stock/${encodeURIComponent(item.symbol)}`);
                    }
                  }}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "minmax(0, 2.2fr) repeat(3, minmax(120px, 1fr)) auto",
                    gap: 16,
                    alignItems: "center",
                    padding: "18px 20px",
                    borderRadius: 20,
                    border: "1px solid rgba(17, 75, 95, 0.08)",
                    background: "rgba(255, 255, 255, 0.82)",
                    cursor: "pointer",
                  }}
                >
                  <div style={{ minWidth: 0 }}>
                    <p style={{ margin: 0, fontSize: 18, fontWeight: 800 }}>{item.symbol}</p>
                    <p className="muted" style={{ margin: "6px 0 0" }}>{item.name}</p>
                    <p className="muted" style={{ margin: "6px 0 0" }}>{item.exchange || "-"}</p>
                  </div>

                  <div>
                    <p className="muted" style={{ margin: 0, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>Price</p>
                    <p style={{ margin: "6px 0 0", fontWeight: 700 }}>{formatPrice(snapshot?.current_price, snapshot?.currency || "INR")}</p>
                  </div>

                  <div>
                    <p className="muted" style={{ margin: 0, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>Risk</p>
                    <div style={{ marginTop: 8 }}>
                      <span
                        style={{
                          display: "inline-flex",
                          padding: "6px 10px",
                          borderRadius: 999,
                          fontWeight: 700,
                          ...riskStyle,
                        }}
                      >
                        {riskLabel}
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="muted" style={{ margin: 0, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>Status</p>
                    <p style={{ margin: "6px 0 0", fontWeight: 700 }}>{snapshot ? "Live tracked" : "Portfolio only"}</p>
                  </div>

                  <div style={{ display: "flex", justifyContent: "flex-end" }}>
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
                </article>
              );
            })}
          </div>
        )}
      </section>

      <QualityResearchModal
        isOpen={showResearchModal}
        portfolioId={linkedPortfolioType?.id || null}
        portfolioName={linkedPortfolioType?.name || decodedSectorName}
        sectorName={decodedSectorName}
        sectorId={sectorGroup?.sector?.id || null}
        forceSectorMode
        onClose={() => setShowResearchModal(false)}
      />
    </>
  );
}
