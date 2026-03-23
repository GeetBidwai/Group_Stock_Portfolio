import { useEffect, useMemo, useRef, useState } from "react";

const MODEL_OPTIONS = [
  { symbol: "ARIMA", name: "Linear short-term pattern model" },
  { symbol: "RNN", name: "Nonlinear sequence dependency model" },
];

export function ModelToggle({ value, onChange }) {
  const containerRef = useRef(null);
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState(value || "");

  useEffect(() => {
    setQuery(value || "");
  }, [value]);

  useEffect(() => {
    function handleOutsideClick(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
        setQuery(value || "");
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, [value]);

  const suggestions = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return MODEL_OPTIONS;
    }

    return MODEL_OPTIONS.filter((item) => item.symbol.toLowerCase().includes(normalizedQuery) || item.name.toLowerCase().includes(normalizedQuery));
  }, [query]);

  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div className="muted" style={{ fontSize: 13 }}>Apply Model</div>
      <div className="stock-autocomplete" ref={containerRef}>
        <input
          className="stock-autocomplete__input"
          placeholder="Select model"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setIsOpen(true);
            if (value && event.target.value !== value) {
              onChange("");
            }
          }}
          onFocus={() => setIsOpen(true)}
        />

        {isOpen && (
          <div className="stock-autocomplete__dropdown" role="listbox">
            {suggestions.length ? (
              suggestions.map((model) => (
                <button
                  key={model.symbol}
                  className={`stock-autocomplete__option${value === model.symbol ? " is-active" : ""}`}
                  type="button"
                  onMouseDown={(event) => event.preventDefault()}
                  onClick={() => {
                    onChange(model.symbol);
                    setQuery(model.symbol);
                    setIsOpen(false);
                  }}
                >
                  <span className="stock-autocomplete__symbol">{model.symbol}</span>
                  <span className="stock-autocomplete__name"> - {model.name}</span>
                </button>
              ))
            ) : (
              <div className="stock-autocomplete__empty">No matching model found.</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
