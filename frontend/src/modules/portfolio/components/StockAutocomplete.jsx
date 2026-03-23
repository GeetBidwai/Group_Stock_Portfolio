import { useEffect, useRef, useState } from "react";

import { apiClient } from "../../../services/apiClient";

function useDebouncedValue(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => window.clearTimeout(timeoutId);
  }, [delay, value]);

  return debouncedValue;
}

export function StockAutocomplete({
  value,
  onChange,
  onSelect,
  placeholder = "Search symbol",
  noResultsText = "No results found",
}) {
  const containerRef = useRef(null);
  const [suggestions, setSuggestions] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const debouncedQuery = useDebouncedValue(value.trim(), 300);

  useEffect(() => {
    function handleOutsideClick(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
        setActiveIndex(-1);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  useEffect(() => {
    if (!debouncedQuery) {
      setSuggestions([]);
      setIsLoading(false);
      setActiveIndex(-1);
      return;
    }

    let isCancelled = false;

    async function fetchSuggestions() {
      setIsLoading(true);
      try {
        const response = await apiClient.get(`/stocks/search?q=${encodeURIComponent(debouncedQuery)}`);
        if (isCancelled) {
          return;
        }
        const nextSuggestions = response.results || [];
        setSuggestions(nextSuggestions);
        setIsOpen(true);
        setActiveIndex(nextSuggestions.length > 0 ? 0 : -1);
      } catch {
        if (isCancelled) {
          return;
        }
        setSuggestions([]);
        setActiveIndex(-1);
        setIsOpen(true);
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }

    fetchSuggestions();

    return () => {
      isCancelled = true;
    };
  }, [debouncedQuery]);

  function handleSelection(stock) {
    onChange(stock.symbol);
    onSelect(stock);
    setIsOpen(false);
    setActiveIndex(-1);
  }

  function handleInputChange(event) {
    const nextValue = event.target.value;
    onChange(nextValue);
    setIsOpen(true);
    setActiveIndex(-1);
  }

  function handleKeyDown(event) {
    if (!isOpen || suggestions.length === 0) {
      if (event.key === "ArrowDown" && suggestions.length > 0) {
        event.preventDefault();
        setIsOpen(true);
        setActiveIndex(0);
      }
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveIndex((currentIndex) => (currentIndex < suggestions.length - 1 ? currentIndex + 1 : 0));
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex((currentIndex) => (currentIndex > 0 ? currentIndex - 1 : suggestions.length - 1));
      return;
    }

    if (event.key === "Enter" && activeIndex >= 0) {
      event.preventDefault();
      handleSelection(suggestions[activeIndex]);
      return;
    }

    if (event.key === "Escape") {
      setIsOpen(false);
      setActiveIndex(-1);
    }
  }

  const shouldShowDropdown = isOpen && value.trim().length > 0;

  return (
    <div className="stock-autocomplete" ref={containerRef}>
      <input
        aria-autocomplete="list"
        aria-expanded={shouldShowDropdown}
        aria-label="Symbol search"
        autoComplete="off"
        className="stock-autocomplete__input"
        placeholder={placeholder}
        value={value}
        onChange={handleInputChange}
        onFocus={() => {
          if (value.trim()) {
            setIsOpen(true);
          }
        }}
        onKeyDown={handleKeyDown}
      />

      {shouldShowDropdown && (
        <div className="stock-autocomplete__dropdown" role="listbox">
          {isLoading ? (
            <div className="stock-autocomplete__empty">Loading...</div>
          ) : suggestions.length > 0 ? (
            suggestions.map((stock, index) => (
              <button
                key={`${stock.symbol}-${stock.name}`}
                className={`stock-autocomplete__option${index === activeIndex ? " is-active" : ""}`}
                type="button"
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => handleSelection(stock)}
              >
                <span className="stock-autocomplete__symbol">{stock.symbol}</span>
                <span className="stock-autocomplete__name"> - {stock.name}</span>
              </button>
            ))
          ) : (
            <div className="stock-autocomplete__empty">{noResultsText}</div>
          )}
        </div>
      )}
    </div>
  );
}
