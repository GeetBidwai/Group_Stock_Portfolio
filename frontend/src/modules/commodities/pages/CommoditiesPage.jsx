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
      try {
        const [gold, silver, correlation] = await Promise.all([
          commoditiesApi.gold(),
          commoditiesApi.silver(),
          commoditiesApi.enhancedCorrelation(),
        ]);
        setResult({ gold, silver, correlation });
      } catch (err) {
        setError(err.message);
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
        <p className="muted">Track one-year price behavior, next-day linear estimates, and cross-commodity correlation.</p>
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
