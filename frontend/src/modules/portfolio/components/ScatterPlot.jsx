import { CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from "recharts";

export function ScatterPlot({ data }) {
  const points = data || [];

  return (
    <div style={{ height: 340 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 36, left: 12 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(17, 75, 95, 0.12)" />
          <XAxis
            type="number"
            dataKey="x"
            name="Date"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => points.find((point) => point.x === value)?.label || ""}
            label={{ value: "Date", position: "insideBottom", offset: -14 }}
            domain={["dataMin", "dataMax"]}
            ticks={points.map((point) => point.x)}
            interval="preserveStartEnd"
          />
          <YAxis
            type="number"
            dataKey="returns"
            name="Daily Returns (%)"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `${value}%`}
            label={{ value: "Daily Returns (%)", angle: -90, position: "insideLeft" }}
            domain={["auto", "auto"]}
          />
          <ZAxis range={[34, 34]} />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            formatter={(value) => [`${value}%`, "Daily Return"]}
            labelFormatter={(value) => points.find((point) => point.x === value)?.fullDate || ""}
          />
          <Scatter data={points} fill="#167c80" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
