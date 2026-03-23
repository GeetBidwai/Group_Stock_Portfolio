import { useEffect, useState } from "react";

import { RecommendationList } from "../components/RecommendationList";
import { recommendationApi } from "../services/recommendationApi";

export function RecommendationPage() {
  const [data, setData] = useState({ top_stocks: [], bottom_stocks: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadRecommendations() {
      try {
        setLoading(true);
        const payload = await recommendationApi.list();
        if (isMounted) {
          setData(payload);
          setError("");
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadRecommendations();
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return <section className="panel"><p>Loading recommendations...</p></section>;
  }

  if (error) {
    return <section className="panel"><p>{error}</p></section>;
  }

  return (
    <>
      <section className="panel">
        <h1>Stock Recommendations</h1>
        <p className="muted">A ranked snapshot of the strongest and weakest names based on sentiment and short-term trend.</p>
      </section>

      <div className="grid" style={{ marginTop: 20 }}>
        <RecommendationList
          title="Top 10 Stocks to Buy"
          description="Highest combined sentiment and short-term momentum scores."
          items={data.top_stocks || []}
          tone="positive"
        />
        <RecommendationList
          title="Stocks to Avoid"
          description="Lowest combined sentiment and short-term momentum scores."
          items={data.bottom_stocks || []}
          tone="negative"
        />
      </div>
    </>
  );
}
