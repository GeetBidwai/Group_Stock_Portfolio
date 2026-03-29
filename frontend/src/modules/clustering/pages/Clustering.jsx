import { useEffect, useMemo, useState } from "react";
import { CartesianGrid, Cell, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";

import { MetricCard } from "../../../components/ui/Card";
import { clusteringApi } from "../services/clusteringApi";

const CLUSTER_COLORS = ["#114b5f", "#1a936f", "#c05621", "#7f5539", "#2b6cb0", "#b83280", "#718096", "#805ad5"];

function ClusterTooltip({ active, payload }) {
  if (!active || !payload?.length) {
    return null;
  }

  const point = payload[0]?.payload;
  if (!point) {
    return null;
  }

  return (
    <div
      style={{
        padding: "12px 14px",
        borderRadius: 16,
        background: "rgba(255, 255, 255, 0.97)",
        border: "1px solid rgba(17, 75, 95, 0.08)",
        boxShadow: "0 18px 34px rgba(17, 75, 95, 0.12)",
      }}
    >
      <div style={{ fontWeight: 700 }}>{point.stock}</div>
      <div className="muted" style={{ marginTop: 4 }}>Cluster {point.cluster}</div>
      <div className="muted" style={{ marginTop: 2 }}>{point.sector}</div>
    </div>
  );
}

export function ClusteringPage() {
  const [method, setMethod] = useState("pca");
  const [clusterCount, setClusterCount] = useState(3);
  const [points, setPoints] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError("");

    clusteringApi
      .listClusters({ method, k: clusterCount })
      .then((data) => {
        if (!isMounted) {
          return;
        }
        setPoints(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        if (!isMounted) {
          return;
        }
        setPoints([]);
        setError(err.message || "Clustering data unavailable.");
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [method, clusterCount]);

  const clusterSummary = useMemo(() => {
    const grouped = new Map();
    for (const point of points) {
      grouped.set(point.cluster, (grouped.get(point.cluster) || 0) + 1);
    }
    return Array.from(grouped.entries()).sort((a, b) => a[0] - b[0]);
  }, [points]);

  return (
    <div className="grid" style={{ gap: 20 }}>
      <section className="panel">
        <div className="grid two" style={{ alignItems: "start", gap: 28 }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>
              Cluster Studio
            </p>
            <h1 style={{ marginBottom: 8 }}>Stock Clustering</h1>
            <p className="muted" style={{ margin: 0, maxWidth: 760 }}>
              Explore the stocks in your portfolio using normalized return, volatility, volume, PE ratio, and market-cap features.
            </p>
          </div>

          <div
            style={{
              justifySelf: "end",
              width: "100%",
              maxWidth: 380,
              padding: 22,
              borderRadius: 28,
              border: "1px solid rgba(23, 33, 33, 0.08)",
              background:
                "radial-gradient(circle at top right, rgba(26, 147, 111, 0.12), transparent 32%), rgba(255, 255, 255, 0.78)",
              boxShadow: "inset 0 1px 0 rgba(255,255,255,0.65)",
            }}
          >
            <p className="muted" style={{ marginTop: 0, marginBottom: 16, fontSize: 13, textTransform: "uppercase", letterSpacing: "0.16em" }}>
              Controls
            </p>

            <div style={{ display: "grid", gap: 16 }}>
              <div>
                <p className="muted" style={{ marginTop: 0, marginBottom: 10, fontSize: 13 }}>Projection Method</p>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 8,
                    padding: 8,
                    borderRadius: 999,
                    background: "rgba(17, 75, 95, 0.07)",
                    border: "1px solid rgba(17, 75, 95, 0.08)",
                  }}
                >
                  {["pca", "umap"].map((option) => (
                    <button
                      key={option}
                      type="button"
                      className={method === option ? "btn" : ""}
                      onClick={() => setMethod(option)}
                      style={
                        method === option
                          ? { padding: "12px 14px", borderRadius: 999, fontWeight: 700 }
                          : {
                              padding: "12px 14px",
                              borderRadius: 999,
                              border: "1px solid rgba(23, 33, 33, 0.08)",
                              background: "rgba(255,255,255,0.88)",
                              cursor: "pointer",
                              fontWeight: 700,
                            }
                      }
                    >
                      {option.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 16,
                  padding: "14px 16px",
                  borderRadius: 18,
                  background: "rgba(255,255,255,0.62)",
                  border: "1px solid rgba(23, 33, 33, 0.06)",
                }}
              >
                <div>
                  <p className="muted" style={{ margin: 0, marginBottom: 4, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    Cluster Count
                  </p>
                  <p style={{ margin: 0, fontWeight: 700 }}>Choose K</p>
                </div>
                <select value={clusterCount} onChange={(event) => setClusterCount(Number(event.target.value))}>
                  {[2, 3, 4, 5, 6].map((value) => (
                    <option key={value} value={value}>
                      K = {value}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="panel">
        {loading ? (
          <p style={{ margin: 0 }}>Loading clustering map...</p>
        ) : error ? (
          <p style={{ margin: 0, color: "#c05353" }}>{error}</p>
        ) : points.length < 2 ? (
          <p className="muted" style={{ margin: 0 }}>Add at least two portfolio stocks with sufficient history to build clusters.</p>
        ) : (
          <>
            <div style={{ marginBottom: 18 }}>
              <h2 style={{ marginTop: 0, marginBottom: 8 }}>Cluster Map</h2>
              <p className="muted" style={{ margin: 0 }}>
                {method.toUpperCase()} projection with KMeans groups. Hover a point to inspect each stock and sector.
              </p>
            </div>

            <div className="chart-panel" style={{ height: 500 }}>
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 16, right: 24, bottom: 20, left: 12 }}>
                  <CartesianGrid stroke="rgba(17, 75, 95, 0.08)" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name="Component 1"
                    tick={{ fontSize: 12, fill: "#5f6b6d" }}
                    tickLine={false}
                    axisLine={{ stroke: "rgba(23, 33, 33, 0.24)", strokeWidth: 1 }}
                    label={{ value: method === "umap" ? "UMAP 1" : "PCA 1", position: "insideBottom", offset: -10 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    name="Component 2"
                    tick={{ fontSize: 12, fill: "#5f6b6d" }}
                    tickLine={false}
                    axisLine={{ stroke: "rgba(23, 33, 33, 0.24)", strokeWidth: 1 }}
                    label={{ value: method === "umap" ? "UMAP 2" : "PCA 2", angle: -90, position: "insideLeft" }}
                  />
                  <Tooltip content={<ClusterTooltip />} cursor={{ strokeDasharray: "3 5" }} />
                  <Scatter data={points}>
                    {points.map((point, index) => (
                      <Cell key={`${point.stock}-${index}`} fill={CLUSTER_COLORS[point.cluster % CLUSTER_COLORS.length]} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))",
                gap: 14,
                marginTop: 18,
              }}
            >
              <MetricCard label="Projection" value={method.toUpperCase()} meta="Current 2D projection method" tone="primary" />
              <MetricCard label="Stocks Mapped" value={String(points.length)} meta="Stocks with enough data to cluster" tone="primary" />
              {clusterSummary.map(([cluster, count]) => (
                <MetricCard
                  key={cluster}
                  label={`Cluster ${cluster}`}
                  value={String(count)}
                  meta="Mapped stocks"
                  tone="primary"
                  style={{ borderLeft: `4px solid ${CLUSTER_COLORS[cluster % CLUSTER_COLORS.length]}` }}
                />
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  );
}
