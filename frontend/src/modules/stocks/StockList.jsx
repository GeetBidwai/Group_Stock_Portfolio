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
    <section className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "baseline", marginBottom: 16, flexWrap: "wrap" }}>
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
        <div className="chart-panel" style={{ overflowX: "auto" }}>
          <table className="table fin-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Name</th>
                <th>Exchange</th>
                <th>Price</th>
                <th style={{ width: 76 }}>Add</th>
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
                      className="btn"
                      style={{
                        width: 40,
                        height: 40,
                        fontSize: 24,
                        lineHeight: 1,
                        opacity: pendingStockId === item.id ? 0.7 : 1,
                        padding: 0,
                      }}
                      aria-label={`Add ${item.symbol} to portfolio`}
                    >
                      +
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
