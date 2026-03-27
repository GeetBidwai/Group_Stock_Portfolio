import { useMemo, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const VIEW_OPTIONS = [
  { key: "overview", label: "Overview", days: null },
  { key: "3m", label: "3M", days: 66 },
  { key: "6m", label: "6M", days: 132 },
  { key: "1y", label: "1Y", days: 252 },
];

export function GoldSection({ data }) {
  const [selectedView, setSelectedView] = useState("overview");
  const unitSuffix = data.unit.replace("Rs / ", "");
  const activeView = VIEW_OPTIONS.find((option) => option.key === selectedView) || VIEW_OPTIONS[0];
  const chartData = useMemo(() => buildCommodityChartData(data, activeView), [data, activeView]);
  const selectedForecast = selectedView === "overview" ? null : data.forecasts?.[selectedView];

  return (
    <section className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", flexWrap: "wrap", marginBottom: 16 }}>
        <div>
          <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.16em", fontSize: 12 }}>Gold</p>
          <h2 style={{ marginBottom: 6 }}>Gold Analytics</h2>
          <p className="muted" style={{ margin: 0 }}>Converted to Indian-format pricing with linear-regression forecasts.</p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(148px, 1fr))", gap: 10, flex: "1 1 620px", maxWidth: 820 }}>
          <div style={{ minWidth: 0, padding: "14px 16px", borderRadius: 18, background: "rgba(255, 215, 0, 0.12)", border: "1px solid rgba(181, 137, 0, 0.18)" }}>
            <div className="muted">Latest Rate</div>
            <strong style={{ display: "block", marginTop: 8, fontSize: 24, lineHeight: 1.08 }}>
              Rs {formatCommodityValue(data.current_price)}
            </strong>
            <span className="muted" style={{ display: "block", marginTop: 6, fontSize: 12 }}>{unitSuffix}</span>
          </div>
          {VIEW_OPTIONS.map((option) => (
            <button
              key={option.key}
              type="button"
              onClick={() => setSelectedView(option.key)}
              aria-pressed={selectedView === option.key}
              style={{
                minWidth: 0,
                padding: "14px 16px",
                borderRadius: 18,
                background: selectedView === option.key ? "rgba(181, 137, 0, 0.16)" : "rgba(255, 249, 226, 0.68)",
                border: selectedView === option.key ? "2px solid rgba(181, 137, 0, 0.45)" : "1px solid rgba(181, 137, 0, 0.14)",
                textAlign: "left",
                cursor: "pointer",
                transition: "all 160ms ease",
              }}
            >
              <div className="muted">{option.label === "Overview" ? "Original Graph" : `${option.label} Forecast`}</div>
              <strong style={{ display: "block", marginTop: 8, fontSize: 20, lineHeight: 1.05 }}>
                {selectedView === option.key && option.key !== "overview"
                  ? `Rs ${formatCommodityValue(data.forecasts?.[option.key])}`
                  : option.label}
              </strong>
              <span className="muted" style={{ display: "block", marginTop: 6, fontSize: 12 }}>
                {option.key === "overview"
                  ? "Tap to return to the original chart"
                  : selectedView === option.key
                    ? `Projected ${option.label} value`
                    : `Tap to reveal ${option.label} forecast`}
              </span>
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: 14, display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
        <p className="muted" style={{ margin: 0 }}>
          {selectedView === "overview"
            ? "Viewing the full original price graph with the historical trend line."
            : `Selected ${activeView.label} forecast. Predicted price: Rs ${formatCommodityValue(selectedForecast)} ${unitSuffix}.`}
        </p>
        {selectedView !== "overview" ? (
          <button
            type="button"
            onClick={() => setSelectedView("overview")}
            style={{
              padding: "10px 14px",
              borderRadius: 999,
              border: "1px solid rgba(181, 137, 0, 0.24)",
              background: "rgba(255, 249, 226, 0.9)",
              cursor: "pointer",
            }}
          >
            Back to Original Graph
          </button>
        ) : null}
      </div>

      <div style={{ height: 340 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 12, left: 2, bottom: 0 }}>
            <XAxis dataKey="label" minTickGap={28} tick={{ fill: "#5f6b6d", fontSize: 12 }} />
            <YAxis tick={{ fill: "#5f6b6d", fontSize: 12 }} domain={["auto", "auto"]} />
            <Tooltip formatter={(value, name) => [`Rs ${Number(value).toLocaleString("en-IN")} ${unitSuffix}`, name]} />
            <Line type="monotone" dataKey="price" name="Price" stroke="#b58900" dot={false} strokeWidth={2.5} connectNulls />
            <Line type="monotone" dataKey="regression" name="Trend" stroke="#8f7a29" dot={false} strokeDasharray="5 5" strokeWidth={1.5} connectNulls />
            {selectedView !== "overview" ? (
              <Line type="monotone" dataKey="projection" name="Projection" stroke="#8a6a00" strokeWidth={0} dot={{ r: 5, strokeWidth: 2 }} connectNulls />
            ) : null}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <p className="muted" style={{ marginTop: 12, marginBottom: 0, fontSize: 12 }}>
        Source: {data.source}. Displayed as {data.unit}.
      </p>
    </section>
  );
}

function formatCommodityValue(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "N/A";
  }
  return Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

function buildCommodityChartData(data, activeView) {
  const historical = Array.isArray(data?.historical) ? data.historical : [];
  const regression = Array.isArray(data?.regression) ? data.regression : [];
  const visibleHistorical = activeView.days ? historical.slice(-activeView.days) : historical;
  const startIndex = Math.max(historical.length - visibleHistorical.length, 0);
  const visibleRegression = regression.slice(startIndex, startIndex + visibleHistorical.length);

  const rows = visibleHistorical.map((item, index) => ({
    label: new Date(item.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }),
    price: item.close,
    regression: visibleRegression[index]?.price ?? item.close,
    projection: null,
  }));

  if (activeView.key !== "overview") {
    const forecastValue = data?.forecasts?.[activeView.key];
    const lastDate = visibleHistorical.at(-1)?.date;
    if (forecastValue != null && lastDate) {
      rows.push({
        label: formatProjectedLabel(lastDate, activeView.key),
        price: null,
        regression: forecastValue,
        projection: forecastValue,
      });
    }
  }

  return rows;
}

function formatProjectedLabel(dateString, horizonKey) {
  const date = new Date(dateString);
  const monthsToAdd = horizonKey === "6m" ? 6 : horizonKey === "1y" ? 12 : 3;
  date.setMonth(date.getMonth() + monthsToAdd);
  return date.toLocaleDateString("en-IN", { month: "short", year: "2-digit" });
}
