import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const LABEL_COLORS = {
  Positive: "#1a936f",
  Negative: "#c05353",
  Neutral: "#7b8485",
};

export function SentimentSummaryCard({ result }) {
  const accent = LABEL_COLORS[result?.overall_sentiment] || "var(--accent)";
  const chartData = [
    { name: "Positive", value: result.summary?.positive ?? 0, color: LABEL_COLORS.Positive },
    { name: "Neutral", value: result.summary?.neutral ?? 0, color: LABEL_COLORS.Neutral },
    { name: "Negative", value: result.summary?.negative ?? 0, color: LABEL_COLORS.Negative },
  ];

  return (
    <section className="panel">
      <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>
        Sentiment Snapshot
      </p>

      <div style={{ display: "grid", gap: 18, marginTop: 14 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap", alignItems: "end" }}>
          <div>
            <h2 style={{ margin: 0 }}>{result.stock_name || result.stock}</h2>
            <p className="muted" style={{ margin: "6px 0 0" }}>{result.stock}</p>
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))",
            gap: 12,
            alignItems: "stretch",
          }}
        >
          <div style={{ padding: 16, border: "1px solid var(--border)", borderRadius: 18, background: "rgba(255,255,255,0.55)" }}>
            <p className="muted" style={{ marginTop: 0, marginBottom: 10 }}>Overall Sentiment</p>
            <h3 style={{ margin: 0, color: accent }}>{result.overall_sentiment}</h3>
          </div>
          <div style={{ padding: 16, border: "1px solid var(--border)", borderRadius: 18, background: "rgba(255,255,255,0.55)" }}>
            <p className="muted" style={{ marginTop: 0 }}>Average Score</p>
            <h3 style={{ marginBottom: 0 }}>{result.score}</h3>
          </div>
          <div style={{ padding: 16, border: "1px solid var(--border)", borderRadius: 18, background: "rgba(255,255,255,0.55)" }}>
            <p className="muted" style={{ marginTop: 0 }}>Positive</p>
            <h3 style={{ marginBottom: 0, color: LABEL_COLORS.Positive }}>{result.summary?.positive ?? 0}%</h3>
          </div>
          <div style={{ padding: 16, border: "1px solid var(--border)", borderRadius: 18, background: "rgba(255,255,255,0.55)" }}>
            <p className="muted" style={{ marginTop: 0 }}>Neutral</p>
            <h3 style={{ marginBottom: 0, color: LABEL_COLORS.Neutral }}>{result.summary?.neutral ?? 0}%</h3>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "minmax(180px, 220px) minmax(140px, 220px)", gap: 16, alignItems: "center", justifyContent: "start" }}>
          <div style={{ width: "100%", height: 180 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={42} outerRadius={68} paddingAngle={2}>
                  {chartData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} stroke="#ffffff" strokeWidth={3} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value}%`} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div style={{ display: "grid", gap: 8 }}>
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
    </section>
  );
}
