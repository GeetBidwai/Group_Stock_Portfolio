import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = {
  Low: "#2f9e44",
  Medium: "#f08c00",
  High: "#d94841",
  Unknown: "#7b8b8e",
};

export function RiskDistributionChart({ items, loading }) {
  const counts = items.reduce(
    (accumulator, item) => {
      const key = item.risk || "Unknown";
      accumulator[key] = (accumulator[key] || 0) + 1;
      return accumulator;
    },
    { Low: 0, Medium: 0, High: 0, Unknown: 0 },
  );

  const data = Object.entries(counts)
    .filter(([, value]) => value > 0)
    .map(([name, value]) => ({ name, value }));

  if (loading) {
    return <p className="muted" style={{ margin: 0 }}>Loading risk distribution...</p>;
  }

  if (!data.length) {
    return <p className="muted" style={{ margin: 0 }}>No risk data available yet.</p>;
  }

  return (
    <div className="risk-chart-shell">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={64} outerRadius={108} paddingAngle={3}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name]} />
            ))}
          </Pie>
          <Tooltip formatter={(value, _name, entry) => [`${value} stocks`, entry.payload.name]} />
          <Legend verticalAlign="bottom" height={24} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
