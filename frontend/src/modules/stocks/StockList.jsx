import { Card } from "../../components/ui/Card";

function formatPrice(value, currency) {
  if (value == null) {
    return "Unavailable";
  }
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: currency || "USD",
    maximumFractionDigits: 2,
  }).format(value);
}

export function StockList({ loading, sector, items, pendingStockId, onAddToPortfolio }) {
  return (
    <Card>
      <div className="card__header">
        <div>
          <h2 style={{ marginBottom: 6 }}>Stocks</h2>
          <p className="muted" style={{ margin: 0 }}>
            {sector ? `Live prices for ${sector.name}.` : "Choose a sector to inspect its stocks."}
          </p>
        </div>
      </div>

      {loading ? (
        <p className="muted" style={{ margin: 0 }}>Loading stocks...</p>
      ) : !items.length ? (
        <p className="muted" style={{ margin: 0 }}>No stocks available for the selected sector.</p>
      ) : (
        <div className="chart-panel stocks-table-shell" style={{ overflowX: "auto" }}>
          <table className="table fin-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Name</th>
                <th>Exchange</th>
                <th>Price</th>
                <th style={{ width: 96 }}>Add</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td><strong>{item.symbol}</strong></td>
                  <td>{item.name}</td>
                  <td>{item.exchange || "-"}</td>
                  <td>{formatPrice(item.current_price, item.currency)}</td>
                  <td>
                    <button
                      type="button"
                      onClick={() => onAddToPortfolio(item.id)}
                      disabled={pendingStockId === item.id}
                      className="btn stocks-table__add-btn"
                      aria-label={`Add ${item.symbol} to portfolio`}
                    >
                      {pendingStockId === item.id ? "..." : "+"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
