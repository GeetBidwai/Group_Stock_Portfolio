import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { stockApi } from "../../stock-search/services/stockApi";

export function StockDetailPage() {
  const { symbol } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    stockApi.analytics(symbol).then(setData).catch((err) => setError(err.message));
  }, [symbol]);

  if (error) {
    return <section className="panel"><p>{error}</p></section>;
  }

  if (!data) {
    return <section className="panel"><p>Loading analytics...</p></section>;
  }

  return (
    <>
      <section className="panel">
        <h1>{data.name}</h1>
        <div className="metric-grid">
          <div className="metric-tile"><p className="metric-tile__label">Current Price</p><p className="metric-tile__value">{data.current_price ?? "N/A"}</p></div>
          <div className="metric-tile"><p className="metric-tile__label">PE Ratio</p><p className="metric-tile__value">{data.trailing_pe ?? "N/A"}</p></div>
          <div className="metric-tile"><p className="metric-tile__label">EPS</p><p className="metric-tile__value">{data.eps ?? "N/A"}</p></div>
          <div className="metric-tile"><p className="metric-tile__label">Intrinsic Value</p><p className="metric-tile__value">{data.intrinsic_value ?? "N/A"}</p></div>
          <div className="metric-tile"><p className="metric-tile__label">Discount %</p><p className="metric-tile__value">{data.discount_percentage ?? "N/A"}</p></div>
          <div className="metric-tile"><p className="metric-tile__label">Opportunity</p><p className="metric-tile__value">{data.opportunity_signal}</p></div>
        </div>
      </section>
      <section className="panel">
        <div className="chart-panel" style={{ height: 360 }}>
          <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data.price_series}>
            <XAxis dataKey="date" hide />
            <YAxis domain={["auto", "auto"]} />
            <Tooltip />
            <Line type="monotone" dataKey="close" stroke="#114b5f" dot={false} />
          </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </>
  );
}
