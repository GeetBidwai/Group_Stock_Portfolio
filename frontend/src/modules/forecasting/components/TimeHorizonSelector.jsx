const HORIZONS = ["3M", "6M", "1Y"];

export function TimeHorizonSelector({ value, onChange }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div className="muted" style={{ fontSize: 13 }}>Time Horizon</div>
      <div className="forecast-horizon-group">
        {HORIZONS.map((horizon) => {
          const active = value === horizon;

          return (
            <button
              key={horizon}
              type="button"
              onClick={() => onChange(horizon)}
              className={`forecast-horizon-button${active ? " is-active" : ""}`}
            >
              {horizon}
            </button>
          );
        })}
      </div>
    </div>
  );
}
