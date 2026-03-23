import { useState } from "react";
import { Link } from "react-router-dom";

import { stockApi } from "../services/stockApi";

export function StockSearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  async function handleSearch(event) {
    event.preventDefault();
    try {
      const data = await stockApi.search(query);
      setResults(data.results);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <section className="panel">
        <h1>Stock Explore</h1>
        <form className="form" onSubmit={handleSearch}>
          <input placeholder="Search Indian stocks by ticker or company" value={query} onChange={(e) => setQuery(e.target.value)} />
          <button className="btn" type="submit">Search</button>
        </form>
        {error && <p>{error}</p>}
      </section>
      <section className="grid two">
        {results.map((item) => (
          <Link key={item.symbol} to={`/stocks/${item.symbol}`} className="panel">
            <h3>{item.symbol}</h3>
            <p>{item.name}</p>
            <p className="muted">{item.exchange}</p>
          </Link>
        ))}
      </section>
    </>
  );
}
