import { useState } from "react";

import { stockApi } from "../../stock-search/services/stockApi";

export function RiskPage() {
  const [symbol, setSymbol] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  return (
    <>
      <section className="panel">
        <h1>Risk Categorization</h1>
        <form className="form" onSubmit={async (e) => {
          e.preventDefault();
          try {
            setResult(await stockApi.risk({ symbol }));
            setError("");
          } catch (err) {
            setError(err.message);
          }
        }}>
          <input placeholder="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)} />
          <button className="btn" type="submit">Classify Risk</button>
        </form>
        {error && <p>{error}</p>}
      </section>
      {result && <section className="panel"><pre>{JSON.stringify(result, null, 2)}</pre></section>}
    </>
  );
}
