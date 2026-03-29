import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { qualityStocksApi } from "../quality-stocks/services/qualityStocksApi";
import { SectorList } from "./SectorList";
import { stocksService } from "./stocksService";

export function StocksPage() {
  const navigate = useNavigate();
  const [markets, setMarkets] = useState([]);
  const [selectedMarket, setSelectedMarket] = useState("");
  const [sectors, setSectors] = useState([]);
  const [qualityReports, setQualityReports] = useState([]);
  const [loadingMarkets, setLoadingMarkets] = useState(true);
  const [loadingSectors, setLoadingSectors] = useState(false);
  const [error, setError] = useState("");

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
        setError("");
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
          setSectors([]);
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
    let cancelled = false;

    async function loadQualityReports() {
      try {
        const data = await qualityStocksApi.list();
        if (!cancelled) {
          setQualityReports(Array.isArray(data) ? data : []);
        }
      } catch (_err) {
        if (!cancelled) {
          setQualityReports([]);
        }
      }
    }

    loadQualityReports();
    return () => {
      cancelled = true;
    };
  }, []);

  const selectedMarketLabel = useMemo(
    () => markets.find((market) => market.code === selectedMarket)?.name || "Stocks",
    [markets, selectedMarket],
  );

  const sectorCards = useMemo(
    () =>
      sectors.map((sector) => ({
        ...sector,
        qualityCount: qualityReports.filter(
          (item) => String(item.portfolio_name || "").trim().toLowerCase() === String(sector.name || "").trim().toLowerCase(),
        ).length,
      })),
    [qualityReports, sectors],
  );

  function handleOpenSector(sector) {
    navigate(`/stocks/sector/${sector.id}`);
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
      </section>

      <section>
        <SectorList
          loading={loadingMarkets || loadingSectors}
          sectors={sectorCards}
          marketLabel={selectedMarketLabel}
          onOpenSector={handleOpenSector}
        />
      </section>
    </>
  );
}
