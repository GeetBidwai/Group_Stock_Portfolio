export function BTCStatsCard({ label, value, tone = "default" }) {
  const color = tone === "positive" ? "#1a936f" : tone === "negative" ? "#c05621" : "var(--accent)";

  return (
    <article className="panel">
      <p className="muted" style={{ marginTop: 0, marginBottom: 8 }}>
        {label}
      </p>
      <h3 style={{ margin: 0, color }}>{value}</h3>
    </article>
  );
}
