import { useEffect, useState } from "react";

import { CorrelationSection } from "../components/CorrelationSection";
import { GoldSection } from "../components/GoldSection";
import { SilverSection } from "../components/SilverSection";
import { commoditiesApi } from "../services/commoditiesApi";

export function CommoditiesPage() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      const [goldResult, silverResult, correlationResult] = await Promise.allSettled([
        commoditiesApi.gold(),
        commoditiesApi.silver(),
        commoditiesApi.enhancedCorrelation(),
      ]);

      const gold = goldResult.status === "fulfilled" ? goldResult.value : { error: goldResult.reason?.message || "Data unavailable" };
      const silver = silverResult.status === "fulfilled" ? silverResult.value : { error: silverResult.reason?.message || "Data unavailable" };

      let correlation = correlationResult.status === "fulfilled"
        ? correlationResult.value
        : { error: correlationResult.reason?.message || "Data unavailable" };

      if (correlation?.error) {
        try {
          const fallback = await commoditiesApi.correlation();
          correlation = normalizeLegacyCorrelationPayload(fallback);
        } catch (_err) {
          correlation = { error: "Data unavailable" };
        }
      }

      setResult({ gold, silver, correlation });
      if (gold?.error && silver?.error && correlation?.error) {
        setError("Commodity data is unavailable right now.");
      } else {
        setError("");
      }
    }

    load();
  }, []);

  if (error) {
    return <section className="panel"><p>{error}</p></section>;
  }

  if (!result) {
    return <section className="panel"><p>Loading gold and silver analytics...</p></section>;
  }

  const hasGold = Boolean(result.gold && !result.gold.error);
  const hasSilver = Boolean(result.silver && !result.silver.error);
  const hasCorrelation = Boolean(result.correlation && !result.correlation.error);

  return (
    <>
      <section className="panel">
        <h1>Gold & Silver Analytics</h1>
        <p className="muted">Track gold and silver prices from Yahoo Finance using a consistent source per metal.</p>
      </section>
      <div className="grid" style={{ marginTop: 20 }}>
        {hasGold ? <GoldSection data={result.gold} /> : <section className="panel"><p>Gold data unavailable right now.</p></section>}
        {hasSilver ? <SilverSection data={result.silver} /> : <section className="panel"><p>Silver data unavailable right now.</p></section>}
        {hasCorrelation ? (
          <CorrelationSection data={result.correlation} />
        ) : (
          <section className="panel"><p>Correlation data unavailable right now.</p></section>
        )}
        {!hasGold && !hasSilver && !hasCorrelation ? (
          <section className="panel"><p>Data unavailable</p></section>
        ) : null}
      </div>
    </>
  );
}

function normalizeLegacyCorrelationPayload(payload) {
  if (!payload || payload.error) {
    return { error: payload?.error || "Data unavailable" };
  }

  if (Array.isArray(payload.gold_prices) && Array.isArray(payload.silver_prices)) {
    return payload;
  }

  const lineChart = Array.isArray(payload.line_chart) ? payload.line_chart : [];
  return {
    correlation: payload.correlation,
    gold_prices: lineChart.map((item) => ({ date: item.date, price: item.gold })),
    silver_prices: lineChart.map((item) => ({ date: item.date, price: item.silver })),
    source: payload.source || "Yahoo Finance",
  };
}
