import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function SilverSection({ data }) {
  const chartData = (data?.historical || []).map((item, index) => ({
    date: item.date,
    label: new Date(item.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }),
    price: item.close,
    regression: data?.regression?.[index]?.price ?? item.close,
  }));

  return (
    <section className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", flexWrap: "wrap", marginBottom: 16 }}>
        <div>
          <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.16em", fontSize: 12 }}>Silver</p>
          <h2 style={{ marginBottom: 6 }}>Silver Analytics</h2>
          <p className="muted" style={{ margin: 0 }}>Historical price with a simple linear trend estimate.</p>
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <div style={{ minWidth: 150, padding: "10px 14px", borderRadius: 16, background: "rgba(192, 192, 192, 0.18)", border: "1px solid rgba(124, 127, 133, 0.18)" }}>
            <div className="muted">Current Price</div>
            <strong>Rs {data.current_price}</strong>
          </div>
          <div style={{ minWidth: 150, padding: "10px 14px", borderRadius: 16, background: "rgba(192, 192, 192, 0.18)", border: "1px solid rgba(124, 127, 133, 0.18)" }}>
            <div className="muted">Predicted Price</div>
            <strong>Rs {data.predicted_price}</strong>
          </div>
        </div>
      </div>

      <div style={{ height: 340 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 8, left: 4, bottom: 0 }}>
            <XAxis dataKey="label" minTickGap={28} tick={{ fill: "#5f6b6d", fontSize: 12 }} />
            <YAxis tick={{ fill: "#5f6b6d", fontSize: 12 }} />
            <Tooltip />
            <Line type="monotone" dataKey="price" name="Price" stroke="#7c7f85" dot={false} strokeWidth={2.5} />
            <Line type="monotone" dataKey="regression" name="Trend" stroke="#495057" dot={false} strokeDasharray="6 4" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
