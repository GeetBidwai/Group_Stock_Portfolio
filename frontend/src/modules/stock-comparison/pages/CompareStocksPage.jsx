import { useState } from "react";

import { stockApi } from "../../stock-search/services/stockApi";

export function CompareStocksPage() {
  const [form, setForm] = useState({ primary_symbol: "", secondary_symbol: "" });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  return (
    <>
      <section className="panel">
        <h1>Compare Stocks</h1>
        <form className="form" onSubmit={async (e) => {
          e.preventDefault();
          try {
            const data = await stockApi.compare(form);
            setResult(data);
            setError("");
          } catch (err) {
            setError(err.message);
          }
        }}>
          <input placeholder="Primary symbol" value={form.primary_symbol} onChange={(e) => setForm({ ...form, primary_symbol: e.target.value })} />
          <input placeholder="Secondary symbol" value={form.secondary_symbol} onChange={(e) => setForm({ ...form, secondary_symbol: e.target.value })} />
          <button className="btn" type="submit">Compare</button>
        </form>
        {error && <p>{error}</p>}
      </section>
      {result && (
        <section className="grid two">
          <div className="panel"><pre>{JSON.stringify(result.primary, null, 2)}</pre></div>
          <div className="panel"><pre>{JSON.stringify(result.secondary, null, 2)}</pre></div>
          <div className="panel" style={{ gridColumn: "1 / -1" }}><p>{result.summary}</p></div>
        </section>
      )}
    </>
  );
}
