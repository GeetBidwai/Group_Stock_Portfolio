import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function CorrelationSection({ data }) {
  const silverByDate = new Map((data?.silver_prices || []).map((item) => [item.date, item.price]));
  const chartData = (data?.gold_prices || []).map((item) => ({
    date: item.date,
    gold: item.price,
    silver: silverByDate.get(item.date),
  }));

  return (
    <section className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap", marginBottom: 16 }}>
        <div>
          <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.16em", fontSize: 12 }}>Correlation</p>
          <h2 style={{ marginBottom: 6 }}>Gold vs Silver</h2>
        </div>
        <div style={{ padding: "12px 16px", borderRadius: 16, background: "rgba(17, 75, 95, 0.08)", border: "1px solid rgba(17, 75, 95, 0.12)" }}>
          <div className="muted">Correlation</div>
          <strong>{data.correlation}</strong>
        </div>
      </div>

      <div style={{ height: 340 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <XAxis dataKey="date" hide />
            <YAxis />
            <Tooltip />
            <Line dataKey="gold" stroke="#b58900" dot={false} strokeWidth={2.5} />
            <Line dataKey="silver" stroke="#7c7f85" dot={false} strokeWidth={2.5} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

