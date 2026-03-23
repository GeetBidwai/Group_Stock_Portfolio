export function StockCard({ item, tone }) {
  const accent = tone === "positive" ? "#1a936f" : "#c05353";
  const background = tone === "positive" ? "rgba(26, 147, 111, 0.08)" : "rgba(192, 83, 83, 0.08)";

  return (
    <article className="panel" style={{ padding: 20, borderColor: accent, background }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "start" }}>
        <div>
          <h3 style={{ margin: 0 }}>{item.name}</h3>
          <p className="muted" style={{ margin: "6px 0 0" }}>{item.ticker}</p>
        </div>
        <div style={{ textAlign: "right" }}>
          <p className="muted" style={{ margin: 0 }}>Score</p>
          <div style={{ fontSize: 26, fontWeight: 700, color: accent }}>{item.score}</div>
        </div>
      </div>

      <div style={{ display: "grid", gap: 8, marginTop: 14 }}>
        <p style={{ margin: 0 }}><strong>Price:</strong> Rs {item.price}</p>
        <p className="muted" style={{ margin: 0 }}>{item.reason}</p>
      </div>
    </article>
  );
}

