import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

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
          <LineChart data={result.history}>
            <XAxis dataKey="date" hide />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#1a936f" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </section>
    </>
  );
}
