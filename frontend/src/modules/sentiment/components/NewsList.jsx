import { NewsCard } from "./NewsCard";

export function NewsList({ articles }) {
  return (
    <section className="sentiment-news-grid">
      {articles.map((article) => (
        <NewsCard key={`${article.url || article.title}-${article.published_at || ""}`} article={article} />
      ))}
    </section>
  );
}
