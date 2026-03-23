import { useEffect, useMemo, useRef, useState } from "react";

import { StockAutocomplete } from "../../portfolio/components/StockAutocomplete";
import { ModelToggle } from "./ModelToggle";
import { TimeHorizonSelector } from "./TimeHorizonSelector";

function PortfolioSymbolAutocomplete({ options, value, onChange, onSelect, placeholder }) {
  const containerRef = useRef(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    function handleOutsideClick(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const suggestions = useMemo(() => {
    const query = value.trim().toLowerCase();
    if (!query) {
      return options.slice(0, 8);
    }
    return options
      .filter((item) => item.symbol.toLowerCase().includes(query) || item.name.toLowerCase().includes(query))
      .slice(0, 8);
  }, [options, value]);

  return (
    <div className="stock-autocomplete" ref={containerRef}>
      <input
        className="stock-autocomplete__input"
        placeholder={placeholder}
        value={value}
        onChange={(event) => {
          onChange(event.target.value);
          setIsOpen(true);
        }}
        onFocus={() => setIsOpen(true)}
      />

      {isOpen && (
        <div className="stock-autocomplete__dropdown" role="listbox">
          {suggestions.length ? (
            suggestions.map((stock) => (
              <button
                key={stock.symbol}
                className="stock-autocomplete__option"
                type="button"
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => {
                  onChange(stock.symbol);
                  onSelect(stock);
                  setIsOpen(false);
                }}
              >
                <span className="stock-autocomplete__symbol">{stock.symbol}</span>
                <span className="stock-autocomplete__name"> - {stock.name}</span>
              </button>
            ))
          ) : (
            <div className="stock-autocomplete__empty">No portfolio stocks found.</div>
          )}
        </div>
      )}
    </div>
  );
}

export function ForecastCard({
  title,
  description,
  mode,
  portfolioOptions = [],
  onForecast,
}) {
  const [query, setQuery] = useState("");
  const [selectedStock, setSelectedStock] = useState(null);
  const [model, setModel] = useState("");
  const [horizon, setHorizon] = useState("3M");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const canSubmit = Boolean(selectedStock?.symbol && model);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!canSubmit) {
      return;
    }

    const symbol = selectedStock?.symbol;

    try {
      setLoading(true);
      setError("");
      await onForecast({ symbol, model, horizon });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <div style={{ marginBottom: 18 }}>
        <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Forecast Module</p>
        <h2 style={{ margin: "10px 0 6px" }}>{title}</h2>
        <p className="muted" style={{ margin: 0 }}>{description}</p>
      </div>

      <form className="form" onSubmit={handleSubmit}>
        <div style={{ display: "grid", gap: 10 }}>
          <div className="muted" style={{ fontSize: 13 }}>{mode === "portfolio" ? "Stock Name" : "Stock Search"}</div>
          {mode === "portfolio" ? (
            <PortfolioSymbolAutocomplete
              options={portfolioOptions}
              value={query}
              onChange={(nextValue) => {
                setQuery(nextValue);
                if (selectedStock && nextValue !== selectedStock.symbol) {
                  setSelectedStock(null);
                }
              }}
              onSelect={setSelectedStock}
              placeholder="Select a stock from your portfolio"
            />
          ) : (
            <StockAutocomplete
              value={query}
              onChange={(nextValue) => {
                setQuery(nextValue);
                if (selectedStock && nextValue !== selectedStock.symbol) {
                  setSelectedStock(null);
                }
              }}
              onSelect={(stock) => {
                setSelectedStock(stock);
                setQuery(stock.symbol);
              }}
              placeholder="Search any stock symbol"
              noResultsText="No matching stocks found"
            />
          )}
        </div>

        <ModelToggle value={model} onChange={setModel} />
        <TimeHorizonSelector value={horizon} onChange={setHorizon} />

        <button className="btn" type="submit" disabled={!canSubmit || loading} style={{ opacity: !canSubmit || loading ? 0.7 : 1 }}>
          {loading ? "Forecasting..." : "Forecast"}
        </button>
      </form>

      {selectedStock?.name && (
        <p className="muted" style={{ marginTop: 14, marginBottom: 0 }}>
          Selected: <strong style={{ color: "var(--text)" }}>{selectedStock.symbol}</strong> - {selectedStock.name}
        </p>
      )}
      {error && <p style={{ color: "#c05353", marginTop: 14, marginBottom: 0 }}>{error}</p>}
    </section>
  );
}
