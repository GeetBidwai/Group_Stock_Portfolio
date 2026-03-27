import { useEffect, useMemo, useState } from "react";

import { recommendationApi } from "../services/recommendationApi";

const EMPTY_RECOMMENDATIONS = {
  top_buy: [],
  bottom_buy: [],
  updated_at: "",
};

function normalizeItems(items, fallbackReason) {
  return (Array.isArray(items) ? items : []).map((item) => ({
    symbol: item.symbol || item.ticker || "-",
    name: item.name || "Unknown Company",
    price: Number(item.price ?? 0),
    change_percent: Number(item.change_percent ?? item.score ?? 0),
    reason: item.reason || fallbackReason,
  }));
}

function formatPrice(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function StockCard({ item }) {
  const isPositive = item.change_percent >= 0;
  return (
    <article className="recommendation-modal__card">
      <div className="recommendation-modal__card-header">
        <div>
          <p className="recommendation-modal__symbol">{item.symbol}</p>
          <p className="muted recommendation-modal__company">{item.name}</p>
        </div>
        <span className={`recommendation-modal__tag ${item.reason === "High Momentum" ? "is-positive" : "is-value"}`}>
          {item.reason}
        </span>
      </div>
      <div className="recommendation-modal__stats">
        <span><strong>Price:</strong> {formatPrice(item.price)}</span>
        <span className={isPositive ? "is-positive-text" : "is-negative-text"}>
          <strong>1D:</strong> {formatPercent(item.change_percent)}
        </span>
      </div>
    </article>
  );
}

function RecommendationSection({ title, items, emptyText }) {
  return (
    <section className="recommendation-modal__section">
      <h3>{title}</h3>
      {!items.length ? (
        <p className="muted">{emptyText}</p>
      ) : (
        <div className="recommendation-modal__grid">
          {items.map((item) => (
            <StockCard key={`${item.symbol}-${item.reason}`} item={item} />
          ))}
        </div>
      )}
    </section>
  );
}

export function RecommendationModal({ isOpen, onClose }) {
  const [payload, setPayload] = useState(EMPTY_RECOMMENDATIONS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const topBuy = useMemo(
    () => normalizeItems(payload.top_buy, "High Momentum"),
    [payload.top_buy],
  );
  const bottomBuy = useMemo(
    () => normalizeItems(payload.bottom_buy, "Undervalued Opportunity"),
    [payload.bottom_buy],
  );

  async function loadRecommendations() {
    try {
      setLoading(true);
      setError("");
      const data = await recommendationApi.list();
      setPayload({
        top_buy: data?.top_buy || [],
        bottom_buy: data?.bottom_buy || [],
        updated_at: data?.updated_at || "",
      });
    } catch (_error) {
      setError("Unable to fetch recommendations");
      setPayload(EMPTY_RECOMMENDATIONS);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!isOpen) {
      return;
    }
    loadRecommendations();
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }
    const onEscape = (event) => {
      if (event.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", onEscape);
    return () => window.removeEventListener("keydown", onEscape);
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  const updatedLabel = payload.updated_at
    ? new Date(payload.updated_at).toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "short",
    })
    : "";

  return (
    <div
      className="recommendation-modal__overlay"
      onClick={onClose}
      role="presentation"
    >
      <section
        className="recommendation-modal panel"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Today's Stock Recommendations"
      >
        <div className="recommendation-modal__top">
          <div>
            <h2 style={{ margin: 0 }}>Today&apos;s Stock Recommendations</h2>
            <p className="muted" style={{ margin: "8px 0 0" }}>
              {updatedLabel ? `Last updated at ${updatedLabel}` : "Live market snapshot"}
            </p>
          </div>
          <div className="recommendation-modal__actions">
            <button type="button" className="btn" onClick={loadRecommendations} disabled={loading}>
              {loading ? "Refreshing..." : "Refresh"}
            </button>
            <button type="button" className="recommendation-modal__close" onClick={onClose} aria-label="Close recommendations">
              x
            </button>
          </div>
        </div>

        {loading ? (
          <div className="recommendation-modal__loading">
            <span className="recommendation-modal__spinner" aria-hidden="true" />
            <p className="muted" style={{ margin: 0 }}>Fetching latest recommendations...</p>
          </div>
        ) : null}

        {!loading && error ? (
          <div className="recommendation-modal__error">
            <p style={{ margin: 0 }}>{error}</p>
          </div>
        ) : null}

        {!loading && !error ? (
          <div className="recommendation-modal__content">
            <RecommendationSection
              title="Top 10 Stocks to BUY Today (Momentum-based)"
              items={topBuy}
              emptyText="No momentum recommendations available right now."
            />
            <RecommendationSection
              title="Bottom 10 Stocks to BUY Today (Value-based)"
              items={bottomBuy}
              emptyText="No value recommendations available right now."
            />
            <p className="muted recommendation-modal__disclaimer">
              Recommendations are based on market trends and not financial advice.
            </p>
          </div>
        ) : null}
      </section>
    </div>
  );
}
