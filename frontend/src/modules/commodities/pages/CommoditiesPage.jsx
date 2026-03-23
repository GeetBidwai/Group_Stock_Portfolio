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

  if (result.gold?.error || result.silver?.error || result.correlation?.error) {
    return <section className="panel"><p>Data unavailable</p></section>;
  }

  return (
    <>
      <section className="panel">
        <h1>Gold & Silver Analytics</h1>
        <p className="muted">Track one-year price behavior, next-day linear estimates, and cross-commodity correlation.</p>
      </section>
      <div className="grid" style={{ marginTop: 20 }}>
        <GoldSection data={result.gold} />
        <SilverSection data={result.silver} />
        <CorrelationSection data={result.correlation} />
      </div>
    </>
  );
}
