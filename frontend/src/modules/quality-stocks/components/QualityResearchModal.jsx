import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { qualityStocksApi } from "../services/qualityStocksApi";

const SIGNAL_STYLES = {
  BUY: { background: "rgba(37, 179, 129, 0.12)", color: "#25b381", border: "1px solid rgba(37, 179, 129, 0.2)" },
  HOLD: { background: "rgba(242, 191, 94, 0.14)", color: "#c28719", border: "1px solid rgba(242, 191, 94, 0.22)" },
  SELL: { background: "rgba(209, 102, 102, 0.12)", color: "#d16666", border: "1px solid rgba(209, 102, 102, 0.2)" },
};

export function QualityResearchModal({ isOpen, portfolioId, portfolioName, sectorName, sectorId, forceSectorMode = false, onClose }) {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  const isSectorMode = (forceSectorMode || !portfolioId) && !!sectorName;

  useEffect(() => {
    if (!isOpen || (!portfolioId && !sectorName)) {
      return;
    }

    let cancelled = false;

    async function loadSnapshot() {
      try {
        setLoading(true);
        const payload = isSectorMode
          ? await qualityStocksApi.sectorSnapshot(sectorName)
          : await qualityStocksApi.snapshot(portfolioId);

        if (!cancelled) {
          const nextItems = Array.isArray(payload) ? payload : [];
          setItems(nextItems);
          setSelectedIds(nextItems.map((item) => item.stock_id));
          setError("");
        }
      } catch (_err) {
        if (!cancelled) {
          setItems([]);
          setSelectedIds([]);
          setError("Failed to fetch analysis");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadSnapshot();
    return () => {
      cancelled = true;
    };
  }, [isOpen, isSectorMode, portfolioId, sectorName]);

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

  return (
    <div className="recommendation-modal__overlay" onClick={onClose} role="presentation">
      <section
        className="recommendation-modal panel"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Quality stocks research"
      >
        <div className="recommendation-modal__top">
          <div>
            <h2 style={{ margin: 0 }}>Quality Stocks Research</h2>
            <p className="muted" style={{ margin: "8px 0 0" }}>
              {portfolioName || sectorName
                ? `Top quality candidates for ${portfolioName || sectorName}.`
                : "Top quality candidates from this portfolio."}
            </p>
          </div>
          <div className="recommendation-modal__actions">
            <button type="button" className="recommendation-modal__close" onClick={onClose} aria-label="Close quality research">
              x
            </button>
          </div>
        </div>

        {loading ? <p style={{ margin: 0 }}>Analyzing your portfolio...</p> : null}
        {!loading && error ? <p style={{ margin: 0 }}>{error}</p> : null}
        {!loading && !error && !items.length ? <p style={{ margin: 0 }}>No stocks found in portfolio</p> : null}

        {!loading && !error && items.length ? (
          <div style={{ display: "grid", gap: 14 }}>
            {items.map((item) => (
              <article
                key={item.stock_id}
                style={{
                  padding: "18px 20px",
                  borderRadius: 18,
                  border: "1px solid rgba(17, 75, 95, 0.08)",
                  background: "rgba(255,255,255,0.78)",
                  display: "grid",
                  gap: 12,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
                  <label style={{ display: "flex", gap: 12, alignItems: "flex-start", cursor: "pointer" }}>
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(item.stock_id)}
                      onChange={(event) => {
                        setSelectedIds((current) =>
                          event.target.checked
                            ? [...current, item.stock_id]
                            : current.filter((value) => value !== item.stock_id),
                        );
                      }}
                    />
                    <div>
                      <h3 style={{ margin: 0 }}>{item.company}</h3>
                      <p className="muted" style={{ margin: "6px 0 0" }}>{item.symbol}</p>
                    </div>
                  </label>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 28, fontWeight: 700 }}>{item.quality_score}/10</div>
                    <span
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: "6px 10px",
                        borderRadius: 999,
                        fontWeight: 700,
                        ...(SIGNAL_STYLES[item.signal] || SIGNAL_STYLES.HOLD),
                      }}
                    >
                      {item.signal}
                    </span>
                  </div>
                </div>
                <p className="muted" style={{ margin: 0 }}>
                  Price: {item.price ?? "N/A"} · Predicted: {item.predicted_price ?? "N/A"} · Expected change: {item.expected_change_pct ?? "N/A"}%
                </p>
              </article>
            ))}

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, flexWrap: "wrap" }}>
              <button type="button" onClick={onClose}>Cancel</button>
              <button
                className="btn"
                type="button"
                disabled={generating || !selectedIds.length}
                onClick={async () => {
                  try {
                    setGenerating(true);
                    if (isSectorMode) {
                      await qualityStocksApi.sectorGenerate(sectorName, selectedIds);
                    } else {
                      await qualityStocksApi.generate(portfolioId, selectedIds);
                    }
                    onClose();
                    if (isSectorMode && sectorId) {
                      navigate(`/quality-stocks?portfolio=${encodeURIComponent(`sector:${sectorId}`)}`);
                    } else {
                      navigate(`/quality-stocks?portfolio=${encodeURIComponent(portfolioId)}`);
                    }
                  } catch (_err) {
                    setError("Failed to fetch analysis");
                  } finally {
                    setGenerating(false);
                  }
                }}
              >
                {generating ? "Generating..." : "Generate Report"}
              </button>
            </div>
          </div>
        ) : null}
      </section>
    </div>
  );
}
