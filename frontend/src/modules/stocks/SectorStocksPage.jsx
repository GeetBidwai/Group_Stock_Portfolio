import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { StockList } from "./StockList";
import { stocksService } from "./stocksService";

export function SectorStocksPage() {
  const navigate = useNavigate();
  const { sectorId } = useParams();
  const [stocksPayload, setStocksPayload] = useState({ sector: null, items: [] });
  const [loadingStocks, setLoadingStocks] = useState(true);
  const [pendingStockId, setPendingStockId] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!sectorId) {
      setStocksPayload({ sector: null, items: [] });
      setLoadingStocks(false);
      return;
    }

    let cancelled = false;

    async function loadStocks() {
      try {
        setLoadingStocks(true);
        const data = await stocksService.listStocks(sectorId);
        if (cancelled) {
          return;
        }
        setStocksPayload({
          sector: data?.sector || null,
          items: Array.isArray(data?.items) ? data.items : [],
        });
        setError("");
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
          setStocksPayload({ sector: null, items: [] });
        }
      } finally {
        if (!cancelled) {
          setLoadingStocks(false);
        }
      }
    }

    loadStocks();
    return () => {
      cancelled = true;
    };
  }, [sectorId]);

  async function handleAddToPortfolio(stockId) {
    try {
      setPendingStockId(stockId);
      setError("");
      const payload = await stocksService.addToPortfolio(stockId);
      setSuccess(payload.message || "Stock added to portfolio.");
    } catch (err) {
      setError(err.message);
      setSuccess("");
    } finally {
      setPendingStockId(null);
    }
  }

  return (
    <>
      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>
              Sector Stocks
            </p>
            <h1 style={{ marginBottom: 6 }}>{stocksPayload.sector?.name || "Sector Details"}</h1>
            <p className="muted" style={{ margin: 0 }}>
              Browse all stocks listed under this sector and add them to your portfolio when needed.
            </p>
          </div>
          <button type="button" className="ghost-btn" onClick={() => navigate("/stocks")}>
            ← Back to Sectors
          </button>
        </div>
        {error ? <p style={{ color: "#c05353", marginBottom: 0 }}>{error}</p> : null}
        {success ? <p style={{ color: "var(--accent-soft)", marginBottom: 0 }}>{success}</p> : null}
      </section>

      <StockList
        loading={loadingStocks}
        sector={stocksPayload.sector}
        items={stocksPayload.items}
        pendingStockId={pendingStockId}
        onAddToPortfolio={handleAddToPortfolio}
      />
    </>
  );
}
