import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { DiscountChart } from "../components/DiscountChart";
import { OpportunityScoreChart } from "../components/OpportunityScoreChart";
import { PriceChart } from "../components/PriceChart";
import { stockApi } from "../../stock-search/services/stockApi";

function round(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return null;
  }
  return Math.round(value * 100) / 100;
}

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(value);
}

function buildPriceTrendSeries(priceSeries, maxPoints = 50) {
  if (!priceSeries.length) {
    return [];
  }

  const step = Math.max(1, Math.ceil(priceSeries.length / maxPoints));
  const sampled = priceSeries.filter((_, index) => index % step === 0 || index === priceSeries.length - 1);
  const lastIndex = Math.max(sampled.length - 1, 1);
  const closes = sampled.map((point) => point.close ?? 0);
  const start = closes[0] ?? 0;
  const end = closes[closes.length - 1] ?? start;

  return sampled.map((point, index) => ({
    date: point.date.slice(5, 10),
    price: round(point.close),
    regression: round(start + ((end - start) * index) / lastIndex),
  }));
}

export function StockDetailPage() {
  const { symbol } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    stockApi.analytics(symbol).then(setData).catch((err) => setError(err.message));
  }, [symbol]);

  const metrics = useMemo(() => {
    if (!data) {
      return null;
    }

    const maxPrice = data.fifty_two_week_high ?? data.current_price ?? 0;
    const currentPrice = data.current_price ?? 0;
    const minPrice = data.fifty_two_week_low ?? 0;
    const peRatio = data.trailing_pe ?? 0;
    const discountPercentage = maxPrice > 0 ? ((maxPrice - currentPrice) / maxPrice) * 100 : 0;
    const priceSeries = data.price_series || [];
    const normalizedPEScore = peRatio > 0 ? Math.max(0, Math.min(100, (35 - peRatio) * 4)) : 50;
    const firstClose = priceSeries[0]?.close ?? currentPrice;
    const lastClose = priceSeries[priceSeries.length - 1]?.close ?? currentPrice;
    const trendPercentage = firstClose ? ((lastClose - firstClose) / firstClose) * 100 : 0;
    const trendScore = trendPercentage > 8 ? 75 : trendPercentage > 0 ? 60 : trendPercentage < -8 ? 25 : 40;
    const opportunityScore = Math.max(
      0,
      Math.min(100, round(discountPercentage * 0.4 + normalizedPEScore * 0.3 + trendScore * 0.3) ?? 0),
    );
    const intrinsicValue = data.intrinsic_value ?? currentPrice;
    const intrinsicGap = currentPrice && intrinsicValue
      ? ((intrinsicValue - currentPrice) / currentPrice) * 100
      : null;
    const latestPoint = priceSeries[priceSeries.length - 1] || {};

    return {
      minPrice,
      maxPrice,
      currentPrice,
      peRatio,
      intrinsicValue,
      marketCap: data.market_cap,
      openPrice: data.latest_open ?? latestPoint.open ?? null,
      closePrice: data.latest_close ?? latestPoint.close ?? currentPrice,
      opportunitySignal: data.opportunity_signal,
      opportunityScore,
      discountPercentage: round(discountPercentage),
      intrinsicGap: round(intrinsicGap),
      valuationStatus: discountPercentage > 20 ? "Undervalued" : discountPercentage < 5 ? "Fully priced" : "Watchlist",
      trendDirection: trendPercentage >= 0 ? "Uptrend" : "Downtrend",
      priceTrendSeries: buildPriceTrendSeries(priceSeries),
    };
  }, [data]);

  if (error) {
    return <section className="panel"><p>{error}</p></section>;
  }

  if (!data || !metrics) {
    return <section className="panel"><p>Loading stock analytics...</p></section>;
  }

  const valuationTone = metrics.discountPercentage > 20 ? "#25b381" : metrics.discountPercentage < 5 ? "#d16666" : "#f2bf5e";
  const stockSummaryItems = [
    { title: "Close", value: `Rs ${formatNumber(metrics.closePrice)}` },
    { title: "Open", value: `Rs ${formatNumber(metrics.openPrice)}` },
    { title: "Symbol", value: data.symbol || "N/A" },
    { title: "Sector", value: data.sector || "Unassigned" },
    { title: "Current Price", value: `Rs ${formatNumber(metrics.currentPrice)}` },
    { title: "1Y Min / Max", value: `Rs ${formatNumber(metrics.minPrice)} / Rs ${formatNumber(metrics.maxPrice)}` },
    { title: "P/E Ratio", value: formatNumber(metrics.peRatio) },
    { title: "Market Cap", value: metrics.marketCap ? `Rs ${formatNumber(metrics.marketCap)}` : "N/A" },
    { title: "Discount %", value: `${formatNumber(metrics.discountPercentage)}%`, tone: valuationTone },
  ];

  return (
    <>
      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Stock Analytics</p>
            <h1 style={{ marginBottom: 6 }}>{data.name || data.symbol}</h1>
            <p className="muted" style={{ margin: 0 }}>
              {data.symbol} · {data.sector || "Unassigned sector"} · {metrics.valuationStatus}
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
            ← Back
          </Link>
        </div>
      </section>

      <section className="panel">
        <div style={{ marginBottom: 20 }}>
          <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Selected Stock</p>
          <h2 style={{ margin: "10px 0 6px" }}>{data.name || data.symbol}</h2>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: 16,
          }}
        >
          {stockSummaryItems.map((card) => (
            <article
              key={card.title}
              style={{
                padding: 18,
                borderRadius: 18,
                background: "rgba(255, 255, 255, 0.66)",
                border: "1px solid rgba(17, 75, 95, 0.08)",
              }}
            >
              <div className="muted" style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.14em" }}>{card.title}</div>
              <div style={{ marginTop: 10, fontSize: 22, fontWeight: 700, color: card.tone || "var(--text)", wordBreak: "break-word", lineHeight: 1.25 }}>{card.value}</div>
            </article>
          ))}
        </div>
      </section>

      <section className="panel" style={{ marginTop: 8 }}>
        <h3>Overall Price Trend</h3>
        <p className="muted" style={{ marginTop: 0 }}>Recent closing trend with a simple direction line to help read momentum.</p>
        <PriceChart data={metrics.priceTrendSeries} trendDirection={metrics.trendDirection} />
      </section>

      <section className="grid two" style={{ gap: 28, marginTop: 8 }}>
        <div className="panel" style={{ paddingBottom: 30 }}>
          <h3>Opportunity Score Graph</h3>
          <p className="muted" style={{ marginTop: 0 }}>Composite signal from discount, P/E quality, and direction bias, with buy, hold, and sell indication.</p>
          <OpportunityScoreChart score={metrics.opportunityScore} />
        </div>

        <div className="panel" style={{ paddingBottom: 30 }}>
          <h3>Discount Graph</h3>
          <p className="muted" style={{ marginTop: 0 }}>Current price against intrinsic value and 1-year high.</p>
          <DiscountChart currentPrice={metrics.currentPrice} intrinsicValue={metrics.intrinsicValue} maxPrice={metrics.maxPrice} />
        </div>
      </section>
    </>
  );
}
