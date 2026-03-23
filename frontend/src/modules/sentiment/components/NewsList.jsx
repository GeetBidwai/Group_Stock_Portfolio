import { NewsCard } from "./NewsCard";

export function NewsList({ articles }) {
  return (
    <section
      style={{
        display: "grid",
        gap: 14,
        gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
      }}
    >
      {articles.map((article) => (
        <NewsCard key={`${article.url || article.title}-${article.published_at || ""}`} article={article} />
      ))}
    </section>
  );
}
