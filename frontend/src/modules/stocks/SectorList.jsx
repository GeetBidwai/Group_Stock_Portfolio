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
        <div style={{ display: "grid", gap: 10 }}>
          {sectors.map((sector) => (
            <button
              key={sector.id}
              type="button"
              onClick={() => onSelect(sector.id)}
              style={{
                border: "1px solid var(--border)",
                borderRadius: 16,
                padding: "14px 16px",
                textAlign: "left",
                cursor: "pointer",
                background: selectedSectorId === sector.id ? "rgba(17, 75, 95, 0.08)" : "rgba(255, 255, 255, 0.72)",
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

