import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { qualityStocksApi } from "../quality-stocks/services/qualityStocksApi";
import { Card } from "../../components/ui/Card";
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
      <Card className="stocks-page-hero">
        <div className="stocks-page-hero__header">
          <div>
            <p className="eyebrow">Stocks Browser</p>
            <h1 style={{ marginBottom: 6 }}>Explore Stocks</h1>
            <p className="muted" style={{ margin: 0 }}>
              Browse live-priced stocks by market and sector using the curated dataset mapped on the backend.
            </p>
          </div>
          <label className="stocks-page-hero__select">
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
        <div className="metric-grid">
          <article className="metric-tile metric-tile--primary">
            <p className="metric-tile__label">Selected Market</p>
            <p className="metric-tile__value">{selectedMarket || "--"}</p>
            <p className="metric-tile__meta">{selectedMarketLabel}</p>
          </article>
          <article className="metric-tile metric-tile--primary">
            <p className="metric-tile__label">Available Sectors</p>
            <p className="metric-tile__value">{sectorCards.length}</p>
            <p className="metric-tile__meta">Curated sector universe</p>
          </article>
          <article className="metric-tile metric-tile--success">
            <p className="metric-tile__label">Quality Coverage</p>
            <p className="metric-tile__value">{sectorCards.reduce((sum, sector) => sum + (sector.qualityCount || 0), 0)}</p>
            <p className="metric-tile__meta">Linked research reports</p>
          </article>
        </div>
        {error ? <p className="form-error">{error}</p> : null}
      </Card>

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
