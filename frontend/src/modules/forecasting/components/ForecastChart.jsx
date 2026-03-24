import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function formatCurrency(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }

  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 2,
  }).format(value);
}

function buildChartData(result) {
  if (!result) {
    return [];
  }

  const historical = result.historical || [];
  const forecast = result.forecast || [];
  const connectorPoint = historical.length
    ? [{
        date: historical[historical.length - 1].date,
        historicalPrice: historical[historical.length - 1].price,
        forecastPrice: historical[historical.length - 1].price,
      }]
    : [];

  return [
    ...historical.map((point) => ({
      date: point.date,
      historicalPrice: point.price,
      forecastPrice: null,
    })),
    ...connectorPoint,
    ...forecast.map((point) => ({
      date: point.date,
      historicalPrice: null,
      forecastPrice: point.price,
    })),
  ];
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) {
    return null;
  }

  const historicalValue = payload.find((item) => item.dataKey === "historicalPrice")?.value;
  const forecastValue = payload.find((item) => item.dataKey === "forecastPrice")?.value;

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
      <div className="muted" style={{ fontSize: 12, marginBottom: 8 }}>{label}</div>
      {historicalValue !== undefined && historicalValue !== null && (
        <div style={{ color: "#114b5f", fontWeight: 700 }}>Historical: Rs {formatCurrency(historicalValue)}</div>
      )}
      {forecastValue !== undefined && forecastValue !== null && (
        <div style={{ marginTop: 4, color: "#1a936f", fontWeight: 700 }}>Forecast: Rs {formatCurrency(forecastValue)}</div>
      )}
    </div>
  );
}

export function ForecastChart({ result }) {
  const chartData = buildChartData(result);

  if (!result) {
    return null;
  }

  const hasChartData = (result.historical?.length || 0) > 0 || (result.forecast?.length || 0) > 0;
  const historical = result.historical || [];
  const forecast = result.forecast || [];
  const forecastStartDate = forecast[0]?.date || historical[historical.length - 1]?.date;

  if (!hasChartData) {
    return (
      <section className="panel" style={{ marginTop: 20 }}>
        <p className="muted" style={{ margin: 0 }}>{result.message || "No forecast data available for this selection."}</p>
      </section>
    );
  }

  return (
    <section className="panel" style={{ marginTop: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", flexWrap: "wrap", marginBottom: 20 }}>
        <div>
          <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Forecast Result</p>
          <h2 style={{ margin: "10px 0 6px" }}>{result.symbol}</h2>
          <p className="muted" style={{ margin: 0 }}>{result.model} model | {result.horizon} horizon</p>
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <span style={{ padding: "8px 12px", borderRadius: 999, background: "rgba(17, 75, 95, 0.08)", color: "#114b5f", fontWeight: 700, fontSize: 13 }}>
            Historical
          </span>
          <span style={{ padding: "8px 12px", borderRadius: 999, background: "rgba(26, 147, 111, 0.10)", color: "#1a936f", fontWeight: 700, fontSize: 13 }}>
            Forecast
          </span>
        </div>
      </div>

      <div style={{ height: 380 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 16, right: 18, left: 12, bottom: 8 }}>
            <CartesianGrid stroke="rgba(17, 75, 95, 0.08)" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12, fill: "#5f6b6d" }}
              tickLine={false}
              axisLine={{ stroke: "rgba(23, 33, 33, 0.24)", strokeWidth: 1 }}
              minTickGap={28}
              dy={8}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#5f6b6d" }}
              tickLine={false}
              axisLine={{ stroke: "rgba(23, 33, 33, 0.24)", strokeWidth: 1 }}
              tickFormatter={(value) => `Rs ${formatCurrency(value)}`}
              width={96}
            />
            <Tooltip content={<CustomTooltip />} />
            {forecastStartDate && (
              <ReferenceLine
                x={forecastStartDate}
                stroke="rgba(17, 75, 95, 0.18)"
                strokeDasharray="3 5"
              />
            )}
            <Line type="monotone" dataKey="historicalPrice" stroke="#114b5f" strokeWidth={3} dot={false} connectNulls={false} />
            <Line type="monotone" dataKey="forecastPrice" stroke="#1a936f" strokeWidth={3} strokeDasharray="8 6" dot={false} connectNulls />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
