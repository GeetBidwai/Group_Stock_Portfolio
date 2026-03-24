const RISK_STYLES = {
  Low: { color: "#1a936f", background: "rgba(26, 147, 111, 0.12)" },
  Medium: { color: "#c77d1f", background: "rgba(199, 125, 31, 0.12)" },
  High: { color: "#c05621", background: "rgba(192, 86, 33, 0.12)" },
  Unknown: { color: "#5f6b6d", background: "rgba(95, 107, 109, 0.12)" },
};

export function RiskBadge({ risk = "Unknown" }) {
  const style = RISK_STYLES[risk] || RISK_STYLES.Unknown;

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        padding: "8px 12px",
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 700,
        color: style.color,
        background: style.background,
      }}
    >
      {risk} Risk
    </span>
  );
}
