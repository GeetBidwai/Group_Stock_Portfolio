import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = {
  Low: "#1a936f",
  Medium: "#f2a541",
  High: "#c05621",
};

export function RiskChart({ items = [] }) {
  const counts = items.reduce(
    (accumulator, item) => {
      const key = item.risk || "Unknown";
      if (key === "Unknown") {
        return accumulator;
      }
      accumulator[key] = (accumulator[key] || 0) + 1;
      return accumulator;
    },
    { Low: 0, Medium: 0, High: 0 },
  );

  const data = Object.entries(counts)
    .filter(([, value]) => value > 0)
    .map(([name, value]) => ({ name, value }));

  if (!data.length) {
    return <p className="muted" style={{ margin: 0 }}>No risk distribution available yet.</p>;
  }

  return (
    <div style={{ height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={52} outerRadius={96} paddingAngle={2}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name]} />
            ))}
          </Pie>
          <Tooltip formatter={(value, _name, entry) => [`${value} stocks`, entry.payload.name]} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
