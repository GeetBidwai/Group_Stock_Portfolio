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

  const metrics = Object.entries(data?.report_json?.metrics || {});
  const risks = data?.report_json?.risks || [];
  const catalysts = data?.report_json?.catalysts || [];

  return (
    <>
      <section className="panel">
        <div className="quality-report-hero">
          <div>
            <p className="eyebrow quality-report-hero__eyebrow">Quality Report</p>
            <h1 className="quality-report-hero__title">{data?.stock_name || "Quality Stock Report"}</h1>
            <p className="muted quality-report-hero__meta">
              {data?.stock_symbol || ""}
              {data?.portfolio_name ? ` · ${data.portfolio_name}` : ""}
            </p>
          </div>
          <Link
            to={data?.portfolio ? `/quality-stocks?portfolio=${encodeURIComponent(data.portfolio)}` : "/quality-stocks"}
            className="ghost-btn"
          >
            Back to Quality Stocks
          </Link>
        </div>
      </section>

      <section className="panel">
        {loading ? <p style={{ margin: 0 }}>Loading report...</p> : null}
        {!loading && error ? <p style={{ margin: 0 }}>{error}</p> : null}

        {!loading && !error && data ? (
          <div className="quality-report-layout">
            <div className="quality-report-summary-grid">
              <article className="dashboard-card quality-report-stat">
                <p className="eyebrow quality-report-stat__label">AI Rating</p>
                <h2 className="quality-report-stat__value">{data.ai_rating}/10</h2>
              </article>
              <article className="dashboard-card quality-report-stat">
                <p className="eyebrow quality-report-stat__label">Signal</p>
                <div className="quality-report-stat__signal">
                  <span className="quality-report-pill" style={SIGNAL_STYLES[data.buy_signal] || SIGNAL_STYLES.HOLD}>
                    {data.buy_signal}
                  </span>
                </div>
              </article>
            </div>

            <article className="dashboard-card quality-report-copy-card">
              <h3 className="quality-report-section-title">Summary</h3>
              <p className="quality-report-body">{data.report_json?.summary || "No summary available."}</p>
            </article>

            <div className="quality-report-copy-grid">
              <article className="dashboard-card quality-report-copy-card">
                <h3 className="quality-report-section-title">Risks</h3>
                {risks.length ? (
                  <div className="quality-report-list-block">
                    {risks.map((risk, index) => (
                      <p key={index} className="quality-report-body">{risk}</p>
                    ))}
                  </div>
                ) : (
                  <p className="quality-report-body">No major risk notes are available for this report.</p>
                )}
              </article>

              <article className="dashboard-card quality-report-copy-card">
                <h3 className="quality-report-section-title">Catalysts</h3>
                {catalysts.length ? (
                  <div className="quality-report-list-block">
                    {catalysts.map((item, index) => (
                      <p key={index} className="quality-report-body">{item}</p>
                    ))}
                  </div>
                ) : (
                  <p className="quality-report-body">No catalyst notes are available for this report.</p>
                )}
              </article>
            </div>

            <article className="dashboard-card quality-report-copy-card">
              <h3 className="quality-report-section-title">Metrics</h3>
              <div className="quality-report-metrics-grid">
                {metrics.map(([key, value]) => (
                  <div key={key} className="quality-report-metric">
                    <p className="eyebrow quality-report-metric__label">{key.replaceAll("_", " ")}</p>
                    <p className="quality-report-metric__value">{value ?? "N/A"}</p>
                  </div>
                ))}
              </div>
            </article>

            <div className="quality-report-chart-grid">
              <article className="dashboard-card quality-report-chart-card">
                <h3 className="quality-report-section-title">Price History</h3>
                <div className="quality-report-chart-shell">
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

              <article className="dashboard-card quality-report-chart-card">
                <h3 className="quality-report-section-title">Forecast</h3>
                <div className="quality-report-chart-shell">
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
