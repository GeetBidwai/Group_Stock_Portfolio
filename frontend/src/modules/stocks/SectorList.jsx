export function SectorList({ loading, sectors, selectedSectorId, marketLabel, onSelect }) {
  return (
    <section className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "baseline", marginBottom: 16 }}>
        <div>
          <h2 style={{ marginBottom: 6 }}>Sectors</h2>
          <p className="muted" style={{ margin: 0 }}>{marketLabel} market sectors currently available in the stocks browser.</p>
        </div>
      </div>

      {loading ? (
        <p className="muted" style={{ margin: 0 }}>Loading sectors...</p>
      ) : !sectors.length ? (
        <p className="muted" style={{ margin: 0 }}>No sectors available for this market.</p>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {sectors.map((sector) => (
            <button
              key={sector.id}
              type="button"
              onClick={() => onSelect(sector.id)}
              className={`dashboard-card dashboard-card--selectable ${selectedSectorId === sector.id ? "dashboard-card--active" : ""}`}
              style={{
                textAlign: "left",
                background: selectedSectorId === sector.id ? "var(--gradient-accent)" : undefined,
                color: selectedSectorId === sector.id ? "#ffffff" : undefined,
              }}
            >
              <strong>{sector.name}</strong>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
