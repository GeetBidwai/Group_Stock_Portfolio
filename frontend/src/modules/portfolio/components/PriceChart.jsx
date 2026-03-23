import { Area, AreaChart, CartesianGrid, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function formatCurrency(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 2,
  }).format(value);
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) {
    return null;
  }

  const pricePoint = payload.find((item) => item.dataKey === "price");
  const regressionPoint = payload.find((item) => item.dataKey === "regression");

  return (
    <div
      style={{
        padding: "12px 14px",
        borderRadius: 16,
        background: "rgba(255, 255, 255, 0.96)",
        border: "1px solid rgba(17, 75, 95, 0.08)",
        boxShadow: "0 18px 34px rgba(17, 75, 95, 0.12)",
      }}
    >
      <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 6 }}>{label}</div>
      <div style={{ fontWeight: 700, color: "#155e63" }}>Price: Rs {formatCurrency(pricePoint?.value)}</div>
      <div style={{ marginTop: 4, fontSize: 13, color: "#c58d1f" }}>Trend: Rs {formatCurrency(regressionPoint?.value)}</div>
    </div>
  );
}

export function PriceChart({ data, trendDirection }) {
  const points = data || [];
  const firstPrice = points[0]?.price ?? null;
  const latestPrice = points[points.length - 1]?.price ?? null;
  const change = latestPrice !== null && firstPrice !== null ? latestPrice - firstPrice : null;
  const changePct = firstPrice ? (change / firstPrice) * 100 : null;
  const isPositive = (change ?? 0) >= 0;

  return (
    <div
      style={{
        padding: 22,
        borderRadius: 24,
        background: "linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(248, 251, 248, 0.76))",
        border: "1px solid rgba(17, 75, 95, 0.08)",
        boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.6)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", flexWrap: "wrap", marginBottom: 18 }}>
        <div>
          <div className="muted" style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.12em" }}>Price Snapshot</div>
          <div style={{ marginTop: 8, fontSize: 40, fontWeight: 700, lineHeight: 1 }}>Rs {formatCurrency(latestPrice)}</div>
          <div style={{ marginTop: 10, fontSize: 16, fontWeight: 700, color: isPositive ? "#1a936f" : "#d16666" }}>
            {change === null ? "N/A" : `${isPositive ? "+" : ""}${formatCurrency(change)} (${changePct?.toFixed(2)}%)`}
          </div>
        </div>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <div
            style={{
              padding: "8px 12px",
              borderRadius: 999,
              background: "rgba(11, 99, 214, 0.08)",
              color: "#0b63d6",
              fontWeight: 700,
              fontSize: 13,
            }}
          >
            Price
          </div>
          <div
            style={{
              padding: "8px 12px",
              borderRadius: 999,
              background: "rgba(242, 191, 94, 0.14)",
              color: "#b67800",
              fontWeight: 700,
              fontSize: 13,
            }}
          >
            Regression ({trendDirection})
          </div>
        </div>
      </div>

      <div style={{ height: 360 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={points} margin={{ top: 10, right: 18, left: -18, bottom: 8 }}>
            <defs>
              <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="rgba(39, 110, 241, 0.28)" />
                <stop offset="60%" stopColor="rgba(39, 110, 241, 0.12)" />
                <stop offset="100%" stopColor="rgba(39, 110, 241, 0.02)" />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="4 4" stroke="rgba(17, 75, 95, 0.10)" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12, fill: "#6b7274" }}
              tickLine={false}
              axisLine={false}
              dy={8}
            />
            <YAxis
              domain={["auto", "auto"]}
              orientation="right"
              tick={{ fontSize: 12, fill: "#6b7274" }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `Rs ${formatCurrency(value)}`}
              width={92}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: "rgba(11, 99, 214, 0.18)", strokeWidth: 1 }} />

            <Area
              type="monotone"
              dataKey="price"
              stroke="#1557d6"
              strokeWidth={3}
              fill="url(#priceFill)"
              activeDot={{ r: 5, stroke: "#1557d6", strokeWidth: 2, fill: "#ffffff" }}
            />
            <Line
              type="monotone"
              dataKey="regression"
              stroke="#f0b341"
              strokeWidth={2}
              dot={false}
              strokeDasharray="7 5"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
