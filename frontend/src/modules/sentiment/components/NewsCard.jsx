const LABEL_STYLES = {
  Positive: { color: "#1a936f", background: "rgba(26, 147, 111, 0.12)" },
  Negative: { color: "#c05353", background: "rgba(192, 83, 83, 0.12)" },
  Neutral: { color: "#7b8485", background: "rgba(123, 132, 133, 0.12)" },
};

export function NewsCard({ article }) {
  const sentimentLabel = article.sentiment?.label || "Neutral";
  const badgeStyle = LABEL_STYLES[sentimentLabel] || LABEL_STYLES.Neutral;
  const publishedAt = article.published_at ? new Date(article.published_at).toLocaleString() : "Unknown publish time";

  return (
    <article className="panel" style={{ padding: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "start", flexWrap: "wrap" }}>
        <h3
          style={{
            margin: 0,
            flex: 1,
            fontSize: 20,
            lineHeight: 1.3,
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
          title={article.title}
        >
          {article.title}
        </h3>
        <span style={{ padding: "6px 12px", borderRadius: 999, fontSize: 13, fontWeight: 700, ...badgeStyle }}>
          {sentimentLabel}
        </span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center", marginTop: 12 }}>
        <div className="muted" style={{ fontSize: 14 }}>{publishedAt}</div>
        {article.url && (
          <a href={article.url} target="_blank" rel="noreferrer" style={{ color: "var(--accent)", fontWeight: 700 }}>
            Read article
          </a>
        )}
      </div>
    </article>
  );
}
