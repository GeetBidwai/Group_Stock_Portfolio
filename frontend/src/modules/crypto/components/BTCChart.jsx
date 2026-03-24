import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function BTCChart({ historicalData, forecastData, rangeLabel }) {
  const lastHistoricalPoint = historicalData[historicalData.length - 1];
  const chartData = [
    ...historicalData.map((point, index) => ({
      date: point.date,
      historical: point.close,
      forecast: index === historicalData.length - 1 ? point.close : null,
    })),
    ...forecastData.map((point, index) => ({
      date: point.date,
      historical: null,
      forecast: point.predicted_price,
    })),
  ];

  return (
    <section className="panel" style={{ height: 420 }}>
      <h2 style={{ marginTop: 0 }}>BTC Price Chart</h2>
      <p className="muted">
        {rangeLabel} of BTC/USD closes with a 30-day exponential smoothing forecast anchored to the latest real close.
      </p>
      <ResponsiveContainer width="100%" height="82%">
        <LineChart data={chartData} margin={{ top: 16, right: 12, left: 4, bottom: 0 }}>
          <XAxis dataKey="date" tick={{ fontSize: 12 }} minTickGap={32} />
          <YAxis tickFormatter={(value) => `$${Number(value).toLocaleString()}`} width={90} />
          <Tooltip
            formatter={(value, name, item) => {
              if (value == null) {
                return ["N/A", name];
              }
              const isAnchorPoint = item?.payload?.date === lastHistoricalPoint?.date && name === "Forecast";
              return [`$${Number(value).toLocaleString()}`, isAnchorPoint ? "Forecast Start" : name];
            }}
          />
          <Line type="monotone" dataKey="historical" name="Historical" stroke="#114b5f" strokeWidth={2.5} dot={false} />
          <Line
            type="monotone"
            dataKey="forecast"
            name="Forecast"
            stroke="#c05621"
            strokeWidth={2.5}
            strokeDasharray="6 6"
            dot={false}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}
