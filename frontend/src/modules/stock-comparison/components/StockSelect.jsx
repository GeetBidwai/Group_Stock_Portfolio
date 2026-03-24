import { useEffect, useMemo, useRef, useState } from "react";

export function StockSelect({
  label,
  placeholder,
  options,
  value,
  onChange,
  disabledSymbol,
}) {
  const containerRef = useRef(null);
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");

  const selectedOption = useMemo(
    () => options.find((option) => option.symbol === value) || null,
    [options, value],
  );

  const filteredOptions = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return options.filter((option) => {
      if (disabledSymbol && option.symbol === disabledSymbol) {
        return false;
      }
      if (!normalizedQuery) {
        return true;
      }
      return (
        option.symbol.toLowerCase().includes(normalizedQuery) ||
        option.name.toLowerCase().includes(normalizedQuery)
      );
    });
  }, [disabledSymbol, options, query]);

  useEffect(() => {
    function handleOutsideClick(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
        setQuery("");
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  return (
    <div className="compare-select" ref={containerRef}>
      <label className="compare-select__label">{label}</label>
      <button
        type="button"
        className="compare-select__trigger"
        onClick={() => setIsOpen((current) => !current)}
      >
        <span>
          {selectedOption ? `${selectedOption.symbol} - ${selectedOption.name}` : placeholder}
        </span>
        <span className="compare-select__chevron">v</span>
      </button>

      {isOpen && (
        <div className="compare-select__menu">
          <input
            className="compare-select__search"
            placeholder="Search stock"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <div className="compare-select__options">
            {filteredOptions.length > 0 ? (
              filteredOptions.map((option) => (
                <button
                  key={option.symbol}
                  type="button"
                  className={`compare-select__option${option.symbol === value ? " is-selected" : ""}`}
                  onClick={() => {
                    onChange(option.symbol);
                    setIsOpen(false);
                    setQuery("");
                  }}
                >
                  <span className="compare-select__symbol">{option.symbol}</span>
                  <span className="compare-select__name">{option.name}</span>
                </button>
              ))
            ) : (
              <div className="compare-select__empty">No matching portfolio stocks.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
