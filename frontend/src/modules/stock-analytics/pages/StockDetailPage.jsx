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
        <div className="grid three">
          <div><strong>Current Price</strong><div>{data.current_price ?? "N/A"}</div></div>
          <div><strong>PE Ratio</strong><div>{data.trailing_pe ?? "N/A"}</div></div>
          <div><strong>EPS</strong><div>{data.eps ?? "N/A"}</div></div>
          <div><strong>Intrinsic Value</strong><div>{data.intrinsic_value ?? "N/A"}</div></div>
          <div><strong>Discount %</strong><div>{data.discount_percentage ?? "N/A"}</div></div>
          <div><strong>Opportunity</strong><div>{data.opportunity_signal}</div></div>
        </div>
      </section>
      <section className="panel" style={{ height: 360 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data.price_series}>
            <XAxis dataKey="date" hide />
            <YAxis domain={["auto", "auto"]} />
            <Tooltip />
            <Line type="monotone" dataKey="close" stroke="#114b5f" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </section>
    </>
  );
}
