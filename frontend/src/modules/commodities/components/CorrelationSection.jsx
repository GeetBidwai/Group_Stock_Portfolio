import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function CorrelationSection({ data }) {
  const silverByDate = new Map((data?.silver_prices || []).map((item) => [item.date, item.price]));
  const chartData = (data?.gold_prices || []).map((item) => ({
    date: item.date,
    label: new Date(item.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }),
    gold: item.price,
    silver: silverByDate.get(item.date),
  }));
  const correlation = Number(data.correlation || 0);
  const interpretation =
    correlation >= 0.8 ? "Strong positive correlation"
      : correlation >= 0.5 ? "Moderate positive correlation"
        : correlation <= -0.5 ? "Negative correlation"
          : "Weak correlation";

  return (
    <section className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", flexWrap: "wrap", marginBottom: 16 }}>
        <div>
          <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.16em", fontSize: 12 }}>Correlation</p>
          <h2 style={{ marginBottom: 6 }}>Gold vs Silver</h2>
          <p className="muted" style={{ margin: 0 }}>{interpretation} across the selected one-year period.</p>
        </div>
        <div style={{ minWidth: 150, padding: "10px 14px", borderRadius: 16, background: "rgba(17, 75, 95, 0.08)", border: "1px solid rgba(17, 75, 95, 0.12)" }}>
          <div className="muted">Correlation</div>
          <strong>{data.correlation}</strong>
        </div>
      </div>

      <div style={{ height: 340 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 12, left: 4, bottom: 0 }}>
            <XAxis dataKey="label" minTickGap={28} tick={{ fill: "#5f6b6d", fontSize: 12 }} />
            <YAxis yAxisId="gold" tick={{ fill: "#b58900", fontSize: 12 }} />
            <YAxis yAxisId="silver" orientation="right" tick={{ fill: "#7c7f85", fontSize: 12 }} />
            <Tooltip />
            <Line yAxisId="gold" type="monotone" dataKey="gold" name="Gold" stroke="#b58900" dot={false} strokeWidth={2.5} />
            <Line yAxisId="silver" type="monotone" dataKey="silver" name="Silver" stroke="#7c7f85" dot={false} strokeWidth={2.5} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
