import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function DiscountChart({ currentPrice, intrinsicValue, maxPrice }) {
  const data = [
    { name: "Current", value: currentPrice ?? 0, fill: "#28b8b0" },
    { name: "Intrinsic", value: intrinsicValue ?? 0, fill: "#77c9e3" },
    { name: "1Y Max", value: maxPrice ?? 0, fill: "#f2bf5e" },
  ];

  return (
    <div style={{ height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(17, 75, 95, 0.12)" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="value" radius={[10, 10, 0, 0]}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
