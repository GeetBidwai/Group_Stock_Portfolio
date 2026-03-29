import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { qualityStocksApi } from "../modules/quality-stocks/services/qualityStocksApi";

const SIGNAL_STYLES = {
  BUY: { background: "rgba(37, 179, 129, 0.12)", color: "#25b381", border: "1px solid rgba(37, 179, 129, 0.2)" },
  HOLD: { background: "rgba(242, 191, 94, 0.14)", color: "#c28719", border: "1px solid rgba(242, 191, 94, 0.22)" },
  SELL: { background: "rgba(209, 102, 102, 0.12)", color: "#d16666", border: "1px solid rgba(209, 102, 102, 0.2)" },
};

export function QualityStockReportPage() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setLoading(true);
        const payload = await qualityStocksApi.detail(id);
        if (!cancelled) {
          setData(payload);
          setError("");
        }
      } catch (_err) {
        if (!cancelled) {
          setData(null);
          setError("Failed to fetch analysis");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [id]);

  const historySeries = useMemo(() => {
    const items = data?.graphs_data?.history || [];
    return items.map((point) => ({
      date: point.date?.slice?.(5, 10) || point.date,
      close: point.close,
    }));
  }, [data]);

  const forecastSeries = useMemo(() => {
    const items = data?.graphs_data?.forecast || [];
    return items.map((point) => ({
      date: point.date?.slice?.(5, 10) || point.date,
      value: point.value,
    }));
  }, [data]);

  return (
    <>
      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Quality Report</p>
            <h1 style={{ marginBottom: 6 }}>{data?.stock_name || "Quality Stock Report"}</h1>
            <p className="muted" style={{ margin: 0 }}>
              {data?.stock_symbol || ""} {data?.portfolio_name ? `· ${data.portfolio_name}` : ""}
            </p>
          </div>
          <Link
            to={data?.portfolio ? `/quality-stocks?portfolio=${encodeURIComponent(data.portfolio)}` : "/quality-stocks"}
            style={{
              padding: "12px 16px",
              borderRadius: 14,
              border: "1px solid rgba(17, 75, 95, 0.12)",
              background: "rgba(255, 255, 255, 0.72)",
            }}
          >
            Back to Quality Stocks
          </Link>
        </div>
      </section>

      <section className="panel">
        {loading ? <p style={{ margin: 0 }}>Loading report...</p> : null}
        {!loading && error ? <p style={{ margin: 0 }}>{error}</p> : null}

        {!loading && !error && data ? (
          <div style={{ display: "grid", gap: 20 }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 14 }}>
              <article className="dashboard-card">
                <p className="muted" style={{ margin: 0 }}>AI Rating</p>
                <h2 style={{ margin: "8px 0 0" }}>{data.ai_rating}/10</h2>
              </article>
              <article className="dashboard-card">
                <p className="muted" style={{ margin: 0 }}>Signal</p>
                <div style={{ marginTop: 10 }}>
                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      padding: "8px 12px",
                      borderRadius: 999,
                      fontWeight: 700,
                      ...(SIGNAL_STYLES[data.buy_signal] || SIGNAL_STYLES.HOLD),
                    }}
                  >
                    {data.buy_signal}
                  </span>
                </div>
              </article>
            </div>

            <article className="dashboard-card">
              <h3 style={{ marginTop: 0 }}>Summary</h3>
              <p style={{ margin: 0 }}>{data.report_json?.summary || "No summary available."}</p>
            </article>

            <div className="grid two" style={{ gap: 20 }}>
              <article className="dashboard-card">
                <h3 style={{ marginTop: 0 }}>Risks</h3>
                <div style={{ display: "grid", gap: 10 }}>
                  {(data.report_json?.risks || []).map((risk, index) => (
                    <p key={index} style={{ margin: 0 }}>{risk}</p>
                  ))}
                </div>
              </article>
              <article className="dashboard-card">
                <h3 style={{ marginTop: 0 }}>Catalysts</h3>
                <div style={{ display: "grid", gap: 10 }}>
                  {(data.report_json?.catalysts || []).map((item, index) => (
                    <p key={index} style={{ margin: 0 }}>{item}</p>
                  ))}
                </div>
              </article>
            </div>

            <article className="dashboard-card">
              <h3 style={{ marginTop: 0 }}>Metrics</h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
                {Object.entries(data.report_json?.metrics || {}).map(([key, value]) => (
                  <div key={key}>
                    <p className="muted" style={{ margin: 0, textTransform: "uppercase", fontSize: 12 }}>{key.replaceAll("_", " ")}</p>
                    <p style={{ margin: "6px 0 0", fontWeight: 700 }}>{value ?? "N/A"}</p>
                  </div>
                ))}
              </div>
            </article>

            <div className="grid two" style={{ gap: 20 }}>
              <article className="dashboard-card">
                <h3 style={{ marginTop: 0 }}>Price History</h3>
                <div style={{ height: 260 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={historySeries}>
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="close" stroke="#167c80" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </article>
              <article className="dashboard-card">
                <h3 style={{ marginTop: 0 }}>Forecast</h3>
                <div style={{ height: 260 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={forecastSeries}>
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="value" stroke="#7b6ee6" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </article>
            </div>
          </div>
        ) : null}
      </section>
    </>
  );
}
