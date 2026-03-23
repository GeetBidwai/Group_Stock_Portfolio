import { useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { cryptoApi } from "../services/cryptoApi";

export function CryptoPage() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    cryptoApi.btcHourly().then(setResult).catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <section className="panel"><p>{error}</p></section>;
  }

  if (!result) {
    return <section className="panel"><p>Loading BTC forecast...</p></section>;
  }

  return (
    <>
      <section className="panel">
        <h1>BTC-USD Hourly Forecast</h1>
        <p>Current price: {result.current_price}</p>
        <p>Next-hour forecast: {result.forecast_next_hour}</p>
      </section>
      <section className="panel" style={{ height: 360 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={result.history}>
            <XAxis dataKey="date" hide />
            <YAxis />
            <Tooltip />
            <Line dataKey="value" stroke="#c05621" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </section>
    </>
  );
}
