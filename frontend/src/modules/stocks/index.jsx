import { useEffect, useMemo, useState } from "react";

import { SectorList } from "./SectorList";
import { StockList } from "./StockList";
import { stocksService } from "./stocksService";

export function StocksPage() {
  const [markets, setMarkets] = useState([]);
  const [selectedMarket, setSelectedMarket] = useState("");
  const [sectors, setSectors] = useState([]);
  const [selectedSectorId, setSelectedSectorId] = useState(null);
  const [stocksPayload, setStocksPayload] = useState({ sector: null, items: [] });
  const [loadingMarkets, setLoadingMarkets] = useState(true);
  const [loadingSectors, setLoadingSectors] = useState(false);
  const [loadingStocks, setLoadingStocks] = useState(false);
  const [pendingStockId, setPendingStockId] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadMarkets() {
      try {
        setLoadingMarkets(true);
        const data = await stocksService.listMarkets();
        if (cancelled) {
          return;
        }
        const nextMarkets = Array.isArray(data) ? data : [];
        setMarkets(nextMarkets);
        const defaultMarket = nextMarkets[0]?.code || "";
        setSelectedMarket(defaultMarket);
        setError("");
        setSuccess("");
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoadingMarkets(false);
        }
      }
    }

    loadMarkets();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedMarket) {
      setSectors([]);
      setSelectedSectorId(null);
      return;
    }

    let cancelled = false;

    async function loadSectors() {
      try {
        setLoadingSectors(true);
        const data = await stocksService.listSectors(selectedMarket);
        if (cancelled) {
          return;
        }
        const nextSectors = Array.isArray(data) ? data : [];
        setSectors(nextSectors);
        setSelectedSectorId(nextSectors[0]?.id ?? null);
        setError("");
        setSuccess("");
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
          setSectors([]);
          setSelectedSectorId(null);
        }
      } finally {
        if (!cancelled) {
          setLoadingSectors(false);
        }
      }
    }

    loadSectors();
    return () => {
      cancelled = true;
    };
  }, [selectedMarket]);

  useEffect(() => {
    if (!selectedSectorId) {
      setStocksPayload({ sector: null, items: [] });
      return;
    }

    let cancelled = false;

    async function loadStocks() {
      try {
        setLoadingStocks(true);
        const data = await stocksService.listStocks(selectedSectorId);
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
  }, [selectedSectorId]);

  const selectedMarketLabel = useMemo(
    () => markets.find((market) => market.code === selectedMarket)?.name || "Stocks",
    [markets, selectedMarket],
  );

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
              Stocks Browser
            </p>
            <h1 style={{ marginBottom: 6 }}>Explore Stocks</h1>
            <p className="muted" style={{ margin: 0 }}>
              Browse live-priced stocks by market and sector using the curated dataset mapped on the backend.
            </p>
          </div>
          <label style={{ display: "grid", gap: 8, minWidth: 220 }}>
            <span className="muted" style={{ fontSize: 13 }}>Market</span>
            <select value={selectedMarket} onChange={(event) => setSelectedMarket(event.target.value)} disabled={loadingMarkets}>
              {markets.map((market) => (
                <option key={market.code} value={market.code}>
                  {market.name}
                </option>
              ))}
            </select>
          </label>
        </div>
        {error ? <p style={{ color: "#c05353", marginBottom: 0 }}>{error}</p> : null}
        {success ? <p style={{ color: "var(--accent-soft)", marginBottom: 0 }}>{success}</p> : null}
      </section>

      <section className="grid two">
        <SectorList
          loading={loadingMarkets || loadingSectors}
          sectors={sectors}
          selectedSectorId={selectedSectorId}
          marketLabel={selectedMarketLabel}
          onSelect={setSelectedSectorId}
        />
        <StockList
          loading={loadingStocks}
          sector={stocksPayload.sector}
          items={stocksPayload.items}
          pendingStockId={pendingStockId}
          onAddToPortfolio={handleAddToPortfolio}
        />
      </section>
    </>
  );
}
