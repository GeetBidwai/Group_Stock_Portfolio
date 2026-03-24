const SUMMARY_CARDS = [
  { key: "total", label: "Total Stocks" },
  { key: "High", label: "High Risk" },
  { key: "Medium", label: "Medium Risk" },
  { key: "Low", label: "Low Risk" },
];

export function RiskSummaryCards({ summary, loading }) {
  return (
    <div className="risk-summary-grid">
      {SUMMARY_CARDS.map((card) => (
        <article key={card.key} className={`risk-summary-card risk-summary-card--${card.key.toLowerCase()}`}>
          <p>{card.label}</p>
          <strong>{loading ? "--" : summary[card.key] ?? 0}</strong>
        </article>
      ))}
    </div>
  );
}
