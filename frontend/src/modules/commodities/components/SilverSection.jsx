import { Line, LineChart, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";

export function SilverSection({ data }) {
  const chartData = (data?.historical || []).map((item, index) => ({
    date: item.date,
    price: item.close,
    regression: data?.regression?.[index]?.price ?? item.close,
  }));

  return (
    <section className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap", marginBottom: 16 }}>
        <div>
          <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.16em", fontSize: 12 }}>Silver</p>
          <h2 style={{ marginBottom: 6 }}>Silver Analytics</h2>
        </div>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <div style={{ padding: "12px 16px", borderRadius: 16, background: "rgba(192, 192, 192, 0.18)", border: "1px solid rgba(124, 127, 133, 0.18)" }}>
            <div className="muted">Current Price</div>
            <strong>Rs {data.current_price}</strong>
          </div>
          <div style={{ padding: "12px 16px", borderRadius: 16, background: "rgba(192, 192, 192, 0.18)", border: "1px solid rgba(124, 127, 133, 0.18)" }}>
            <div className="muted">Predicted Price</div>
            <strong>Rs {data.predicted_price}</strong>
          </div>
        </div>
      </div>

      <div className="grid two">
        <div style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <XAxis dataKey="date" hide />
              <YAxis />
              <Tooltip />
              <Line dataKey="price" stroke="#7c7f85" dot={false} strokeWidth={2.5} />
              <Line dataKey="regression" stroke="#495057" dot={false} strokeDasharray="6 4" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart>
              <XAxis dataKey="x" name="Day" />
              <YAxis dataKey="y" name="Price" />
              <Tooltip />
              <Scatter data={data.scatter_data || []} fill="#7c7f85" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}

