export function RiskFilter({ value, onChange }) {
  return (
    <label className="muted" style={{ display: "grid", gap: 6 }}>
      Risk Filter
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {["All", "Low", "Medium", "High"].map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
