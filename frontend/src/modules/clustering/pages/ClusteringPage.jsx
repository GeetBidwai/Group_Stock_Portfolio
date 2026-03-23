import { useEffect, useState } from "react";

import { portfolioApi } from "../../portfolio/services/portfolioApi";

export function ClusteringPage() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    portfolioApi.clustering().then(setResult).catch((err) => setError(err.message));
  }, []);

  return (
    <>
      <section className="panel">
        <h1>Portfolio Clustering</h1>
        {error && <p>{error}</p>}
        {result && <p>{result.interpretation}</p>}
      </section>
      {result && <section className="panel"><pre>{JSON.stringify(result.clusters, null, 2)}</pre></section>}
    </>
  );
}
