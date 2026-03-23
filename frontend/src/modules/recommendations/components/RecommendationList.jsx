export function RecommendationList({ title, description, items, tone }) {
  const accent = tone === "positive" ? "#1a936f" : "#c05353";

  return (
    <section className="panel">
      <div style={{ marginBottom: 18 }}>
        <h2 style={{ marginBottom: 6 }}>{title}</h2>
        <p className="muted" style={{ margin: 0 }}>{description}</p>
      </div>
      <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))" }}>
        {items.map((item, index) => (
          <div
            key={item.ticker}
            style={{
              display: "grid",
              gridTemplateColumns: "40px minmax(0, 1fr) auto auto",
              gap: 12,
              alignItems: "center",
              padding: "12px 14px",
              borderRadius: 16,
              border: "1px solid var(--border)",
              background: "rgba(255,255,255,0.55)",
            }}
          >
            <strong style={{ color: accent }}>{index + 1}.</strong>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontWeight: 700 }}>{item.name}</div>
              <div className="muted" style={{ fontSize: 14 }}>{item.ticker}</div>
            </div>
            <div className="muted" style={{ whiteSpace: "nowrap" }}>Rs {item.price}</div>
            <div style={{ fontWeight: 700, color: accent, whiteSpace: "nowrap" }}>{item.score}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
