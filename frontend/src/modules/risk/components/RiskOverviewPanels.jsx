const PANEL_TONES = {
  High: "risk-panel--high",
  Medium: "risk-panel--medium",
  Low: "risk-panel--low",
  Unknown: "risk-panel--unknown",
};

export function RiskOverviewPanels({ categories }) {
  return (
    <div className="risk-overview-grid">
      {categories.map((category) => (
        <article key={category.risk} className={`risk-overview-card ${PANEL_TONES[category.risk] || PANEL_TONES.Unknown}`}>
          <div className="risk-overview-card__band">
            <div>
              <p>{category.title}</p>
              <strong>{category.count}</strong>
            </div>
          </div>
          <div className="risk-overview-card__body">
            <p className="risk-overview-card__description">{category.description}</p>
            <p className="muted" style={{ margin: 0 }}>
              <strong>Criteria:</strong> {category.criteria}
            </p>
          </div>
        </article>
      ))}
    </div>
  );
}
