import { Card } from "../../../components/ui/Card";

const LABEL_STYLES = {
  Positive: { color: "#15803d", background: "rgba(34, 197, 94, 0.12)" },
  Negative: { color: "#b91c1c", background: "rgba(239, 68, 68, 0.12)" },
  Neutral: { color: "#475569", background: "rgba(100, 116, 139, 0.12)" },
};

export function NewsCard({ article }) {
  const sentimentLabel = article.sentiment?.label || "Neutral";
  const badgeStyle = LABEL_STYLES[sentimentLabel] || LABEL_STYLES.Neutral;
  const publishedAt = article.published_at ? new Date(article.published_at).toLocaleString() : "Unknown publish time";

  return (
    <Card as="article" className="sentiment-news-card" interactive>
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
        <span className="badge" style={{ ...badgeStyle, borderColor: "transparent" }}>
          {sentimentLabel}
        </span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
        <div className="muted" style={{ fontSize: 14 }}>{publishedAt}</div>
        {article.url ? (
          <a href={article.url} target="_blank" rel="noreferrer" style={{ color: "var(--primary)", fontWeight: 700 }}>
            Read article
          </a>
        ) : null}
      </div>
    </Card>
  );
}
