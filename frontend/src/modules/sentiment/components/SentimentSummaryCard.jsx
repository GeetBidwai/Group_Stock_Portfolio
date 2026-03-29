import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { Card } from "../../../components/ui/Card";

const LABEL_COLORS = {
  Positive: "#22c55e",
  Negative: "#ef4444",
  Neutral: "#64748b",
};

export function SentimentSummaryCard({ result }) {
  const accent = LABEL_COLORS[result?.overall_sentiment] || "var(--primary)";
  const chartData = [
    { name: "Positive", value: result.summary?.positive ?? 0, color: LABEL_COLORS.Positive },
    { name: "Neutral", value: result.summary?.neutral ?? 0, color: LABEL_COLORS.Neutral },
    { name: "Negative", value: result.summary?.negative ?? 0, color: LABEL_COLORS.Negative },
  ];

  return (
    <Card className="sentiment-summary-card">
      <p className="eyebrow">Sentiment Snapshot</p>

      <div className="sentiment-summary-card__layout">
        <div className="sentiment-summary-card__content">
          <div>
            <h2 style={{ margin: 0 }}>{result.stock_name || result.stock}</h2>
            <p className="muted" style={{ margin: "6px 0 0" }}>{result.stock}</p>
          </div>

          <div className="sentiment-summary-card__metrics">
            <div className="sentiment-summary-card__metric">
              <p className="muted" style={{ marginTop: 0, marginBottom: 10 }}>Overall Sentiment</p>
              <h3 style={{ margin: 0, color: accent }}>{result.overall_sentiment}</h3>
            </div>
            <div className="sentiment-summary-card__metric">
              <p className="muted" style={{ marginTop: 0 }}>Average Score</p>
              <h3 style={{ marginBottom: 0 }}>{result.score}</h3>
            </div>
            <div className="sentiment-summary-card__metric">
              <p className="muted" style={{ marginTop: 0 }}>Positive</p>
              <h3 style={{ marginBottom: 0, color: LABEL_COLORS.Positive }}>{result.summary?.positive ?? 0}%</h3>
            </div>
            <div className="sentiment-summary-card__metric">
              <p className="muted" style={{ marginTop: 0 }}>Neutral</p>
              <h3 style={{ marginBottom: 0, color: LABEL_COLORS.Neutral }}>{result.summary?.neutral ?? 0}%</h3>
            </div>
          </div>
        </div>

        <div className="sentiment-summary-card__chart">
          <div style={{ width: "100%", height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={46} outerRadius={76} paddingAngle={2}>
                  {chartData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} stroke="#ffffff" strokeWidth={3} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value}%`} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div style={{ display: "grid", gap: 8, width: "100%" }}>
            {chartData.map((item) => (
              <div key={item.name} style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ width: 10, height: 10, borderRadius: 999, background: item.color, display: "inline-block" }} />
                  <span>{item.name}</span>
                </div>
                <span className="muted">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
