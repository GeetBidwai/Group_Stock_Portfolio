import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function ForecastResultPage() {
  const result = JSON.parse(sessionStorage.getItem("stockForecastResult") || "null");

  if (!result) {
    return <section className="panel"><p>No forecast result available.</p></section>;
  }

  return (
    <>
      <section className="panel">
        <h1>Forecast Result</h1>
        <p>Predicted next value: {result.prediction ?? "N/A"}</p>
      </section>
      <section className="panel" style={{ height: 360 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={result.history} margin={{ top: 16, right: 18, left: 12, bottom: 8 }}>
            <CartesianGrid stroke="rgba(17, 75, 95, 0.08)" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12, fill: "#5f6b6d" }}
              tickLine={false}
              axisLine={{ stroke: "rgba(23, 33, 33, 0.24)", strokeWidth: 1 }}
              minTickGap={28}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#5f6b6d" }}
              tickLine={false}
              axisLine={{ stroke: "rgba(23, 33, 33, 0.24)", strokeWidth: 1 }}
            />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#1a936f" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </section>
    </>
  );
}
