const HORIZONS = ["3M", "6M", "1Y"];

export function TimeHorizonSelector({ value, onChange }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div className="muted" style={{ fontSize: 13 }}>Time Horizon</div>
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        {HORIZONS.map((horizon) => {
          const active = value === horizon;

          return (
            <button
              key={horizon}
              type="button"
              onClick={() => onChange(horizon)}
              style={{
                minWidth: 72,
                padding: "12px 16px",
                borderRadius: 14,
                border: active ? "1px solid rgba(17, 75, 95, 0.22)" : "1px solid rgba(17, 75, 95, 0.08)",
                background: active ? "rgba(17, 75, 95, 0.10)" : "rgba(255, 255, 255, 0.72)",
                cursor: "pointer",
                fontWeight: 700,
              }}
            >
              {horizon}
            </button>
          );
        })}
      </div>
    </div>
  );
}
