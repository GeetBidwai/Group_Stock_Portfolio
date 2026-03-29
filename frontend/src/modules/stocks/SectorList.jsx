import { Card } from "../../components/ui/Card";

export function SectorList({ loading, sectors, marketLabel, onOpenSector }) {
  return (
    <Card>
      <div className="card__header">
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
        <div className="stocks-sector-grid">
          {sectors.map((sector) => (
            <Card key={sector.id} as="article" className="stocks-sector-card" interactive>
              <button
                type="button"
                onClick={() => onOpenSector(sector)}
                className="stocks-sector-card__button"
              >
                <div className="stocks-sector-card__top">
                  <div>
                    <div className="stocks-sector-card__title-row">
                      <strong style={{ fontSize: 18 }}>{sector.name}</strong>
                      <span className="badge">[{sector.market_code || "IN"}]</span>
                      <span className="badge badge--primary">QS {sector.qualityCount || 0}</span>
                    </div>
                    <p className="muted" style={{ margin: "6px 0 0" }}>
                      {sector.code || sector.name} sector stocks currently available in this market.
                    </p>
                  </div>
                  <span className="stocks-sector-card__arrow">Open</span>
                </div>

                <div className="stocks-sector-card__metrics">
                  <div className="stocks-sector-card__metric-row">
                    <span className="muted" style={{ fontSize: 12, fontWeight: 700, letterSpacing: "0.06em" }}>SECTOR STATUS</span>
                    <strong style={{ color: "#2563eb" }}>Available</strong>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-bar__fill" style={{ width: "56%" }} />
                  </div>
                  <div className="stocks-sector-card__metric-row">
                    <span className="muted">Quality reports: {sector.qualityCount || 0}</span>
                    <span className="muted">Open stocks →</span>
                  </div>
                </div>
              </button>
            </Card>
          ))}
        </div>
      )}
    </Card>
  );
}
