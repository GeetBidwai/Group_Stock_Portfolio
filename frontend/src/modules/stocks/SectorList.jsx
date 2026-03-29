export function SectorList({ loading, sectors, marketLabel, onOpenSector }) {
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
        <div style={{ display: "grid", gap: 16 }}>
          {sectors.map((sector) => (
            <article
              key={sector.id}
              style={{
                padding: "18px 18px 16px",
                borderRadius: 22,
                border: "1px solid rgba(17, 75, 95, 0.08)",
                background: "linear-gradient(180deg, rgba(255,255,255,0.92), rgba(248,250,255,0.92))",
                boxShadow: "0 10px 24px rgba(17, 75, 95, 0.05)",
                display: "grid",
                gap: 14,
              }}
            >
              <button
                type="button"
                onClick={() => onOpenSector(sector)}
                style={{
                  textAlign: "left",
                  background: "transparent",
                  border: "none",
                  padding: 0,
                  cursor: "pointer",
                  display: "grid",
                  gap: 14,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 14, alignItems: "flex-start" }}>
                  <div>
                    <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                      <strong style={{ fontSize: 18 }}>{sector.name}</strong>
                      <span
                        className="muted"
                        style={{
                          padding: "4px 8px",
                          borderRadius: 999,
                          background: "rgba(17, 75, 95, 0.06)",
                          fontSize: 12,
                          fontWeight: 700,
                        }}
                      >
                        [{sector.market_code || "IN"}]
                      </span>
                      <span
                        style={{
                          padding: "4px 8px",
                          borderRadius: 999,
                          background: "rgba(123, 110, 230, 0.10)",
                          color: "#6a5be2",
                          fontSize: 12,
                          fontWeight: 700,
                        }}
                      >
                        QS: {sector.qualityCount || 0}
                      </span>
                    </div>
                    <p className="muted" style={{ margin: "6px 0 0" }}>
                      {sector.code || sector.name} sector stocks currently available in this market.
                    </p>
                  </div>
                </div>

                <div
                  style={{
                    padding: "14px 16px",
                    borderRadius: 18,
                    background: "rgba(255, 255, 255, 0.78)",
                    border: "1px solid rgba(17, 75, 95, 0.06)",
                    display: "grid",
                    gap: 10,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                    <span className="muted" style={{ fontSize: 12, fontWeight: 700, letterSpacing: "0.06em" }}>SECTOR STATUS</span>
                    <strong style={{ color: "#4f6278" }}>Available</strong>
                  </div>
                  <div style={{ height: 6, borderRadius: 999, background: "rgba(17, 75, 95, 0.08)", overflow: "hidden" }}>
                    <div
                      style={{
                        width: "56%",
                        height: "100%",
                        background: "linear-gradient(90deg, #f59f00, #f2bf5e)",
                        borderRadius: 999,
                      }}
                    />
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                    <span className="muted">Quality reports: {sector.qualityCount || 0}</span>
                    <span className="muted">Open stocks →</span>
                  </div>
                </div>
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
