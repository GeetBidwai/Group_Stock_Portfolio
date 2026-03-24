import { RiskBadge } from "../../portfolio/components/RiskBadge";

export function RiskStockTable({ items, loading }) {
  if (loading) {
    return <p className="muted" style={{ margin: 0 }}>Loading tracked stocks...</p>;
  }

  if (!items.length) {
    return <p className="muted" style={{ margin: 0 }}>No stocks match the selected filter.</p>;
  }

  return (
    <div className="risk-table-shell">
      <table className="table risk-table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Company</th>
            <th>Price</th>
            <th>Risk</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.symbol}>
              <td style={{ fontWeight: 700 }}>{item.symbol}</td>
              <td>{item.stock_name}</td>
              <td>{item.price != null ? `Rs ${Number(item.price).toLocaleString("en-IN")}` : "N/A"}</td>
              <td>
                <RiskBadge risk={item.risk || "Unknown"} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
