import { PolarAngleAxis, RadialBar, RadialBarChart, ResponsiveContainer } from "recharts";

function scoreTone(score) {
  if (score >= 70) {
    return { label: "Buy", fill: "#1a936f" };
  }
  if (score >= 45) {
    return { label: "Hold", fill: "#f2bf5e" };
  }
  return { label: "Sell", fill: "#ef6f6c" };
}

export function OpportunityScoreChart({ score }) {
  const clampedScore = Math.max(0, Math.min(100, Number(score) || 0));
  const tone = scoreTone(clampedScore);
  const data = [{ name: "Opportunity", value: clampedScore, fill: tone.fill }];

  return (
    <div style={{ height: 280 }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          cx="50%"
          cy="72%"
          innerRadius="55%"
          outerRadius="100%"
          data={data}
          startAngle={180}
          endAngle={0}
          barSize={28}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar background dataKey="value" cornerRadius={14} />
          <text x="18%" y="78%" textAnchor="middle" style={{ fontSize: 12, fill: "#a95250", fontWeight: 700 }}>
            SELL
          </text>
          <text x="50%" y="28%" textAnchor="middle" style={{ fontSize: 12, fill: "#8c6b2f", fontWeight: 700 }}>
            HOLD
          </text>
          <text x="82%" y="78%" textAnchor="middle" style={{ fontSize: 12, fill: "#157256", fontWeight: 700 }}>
            BUY
          </text>
          <text x="50%" y="60%" textAnchor="middle" dominantBaseline="middle" style={{ fontSize: 30, fontWeight: 700, fill: "#172121" }}>
            {clampedScore.toFixed(1)}
          </text>
          <text x="50%" y="74%" textAnchor="middle" style={{ fontSize: 14, fontWeight: 700, fill: tone.fill }}>
            {tone.label} Signal
          </text>
        </RadialBarChart>
      </ResponsiveContainer>
    </div>
  );
}
