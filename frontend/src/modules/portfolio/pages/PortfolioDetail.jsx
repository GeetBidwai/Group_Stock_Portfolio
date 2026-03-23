import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { PEChart } from "../components/PEChart";
import { StockAutocomplete } from "../components/StockAutocomplete";
import { portfolioApi } from "../services/portfolioApi";
import { stockApi } from "../../stock-search/services/stockApi";

export function PortfolioDetailPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const portfolioId = Number(id);
  const [portfolios, setPortfolios] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [analyticsBySymbol, setAnalyticsBySymbol] = useState({});
  const [peComparison, setPeComparison] = useState({ items: [], portfolio_average_pe: null });
  const [selectedStock, setSelectedStock] = useState(null);
  const [showAddStockForm, setShowAddStockForm] = useState(false);
  const [stockForm, setStockForm] = useState({ symbol: "", company_name: "", quantity: 1, average_buy_price: "" });
  const [error, setError] = useState("");

  async function load() {
    try {
      const [portfolioData, stockData, peData] = await Promise.all([
        portfolioApi.listTypes(),
        portfolioApi.listStocks(),
        portfolioApi.peComparison(),
      ]);
      setPortfolios(portfolioData);
      setStocks(stockData);
      setPeComparison(peData);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const portfolio = useMemo(
    () => portfolios.find((item) => item.id === portfolioId),
    [portfolioId, portfolios],
  );

  const portfolioStocks = useMemo(
    () => stocks.filter((stock) => stock.portfolio_type === portfolioId),
    [portfolioId, stocks],
  );

  const portfolioPEItems = useMemo(() => {
    const symbols = new Set(portfolioStocks.map((stock) => stock.symbol));
    return (peComparison.items || []).filter((item) => symbols.has(item.symbol));
  }, [peComparison.items, portfolioStocks]);

  useEffect(() => {
    if (!portfolioStocks.length) {
      setAnalyticsBySymbol({});
      return;
    }

    let cancelled = false;

    async function loadAnalytics() {
      try {
        const entries = await Promise.all(
          portfolioStocks.map(async (stock) => {
            const analytics = await stockApi.analytics(stock.symbol);
            return [stock.symbol, analytics];
          }),
        );

        if (!cancelled) {
          setAnalyticsBySymbol(Object.fromEntries(entries));
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      }
    }

    loadAnalytics();

    return () => {
      cancelled = true;
    };
  }, [portfolioStocks]);

  return (
    <>
      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Stock Level</p>
            <h1 style={{ marginBottom: 6 }}>{portfolio?.name || "Portfolio Detail"}</h1>
            <p className="muted" style={{ margin: 0 }}>Sector: {portfolio?.sector_name || "Unassigned"}</p>
          </div>
          <Link
            to={portfolio?.sector_name ? `/portfolio/sector/${encodeURIComponent(portfolio.sector_name)}` : "/portfolio"}
            style={{
              padding: "12px 16px",
              borderRadius: 14,
              border: "1px solid rgba(17, 75, 95, 0.12)",
              background: "rgba(255, 255, 255, 0.72)",
            }}
          >
            ← Back
          </Link>
        </div>
        {error && <p>{error}</p>}
      </section>

      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <h3 style={{ margin: 0 }}>Stocks</h3>
          <button className="btn" type="button" onClick={() => setShowAddStockForm((current) => !current)}>
            + Add Stock
          </button>
        </div>

        {showAddStockForm && (
          <form
            className="form"
            style={{
              marginTop: 20,
              padding: 18,
              borderRadius: 18,
              background: "rgba(17, 75, 95, 0.05)",
              border: "1px dashed rgba(17, 75, 95, 0.18)",
            }}
            onSubmit={async (e) => {
              e.preventDefault();
              await portfolioApi.addStock({
                portfolio_type: portfolioId,
                symbol: stockForm.symbol,
                company_name: stockForm.company_name,
                quantity: Number(stockForm.quantity),
                average_buy_price: Number(stockForm.average_buy_price || 0),
              });
              setStockForm({ symbol: "", company_name: "", quantity: 1, average_buy_price: "" });
              setSelectedStock(null);
              setShowAddStockForm(false);
              load();
            }}
          >
            <StockAutocomplete
              value={stockForm.symbol}
              onChange={(symbolValue) => {
                setStockForm((current) => ({
                  ...current,
                  symbol: symbolValue,
                  company_name: selectedStock && symbolValue === selectedStock.symbol ? current.company_name : "",
                }));
                if (selectedStock && symbolValue !== selectedStock.symbol) {
                  setSelectedStock(null);
                }
              }}
              onSelect={(stock) => {
                setSelectedStock(stock);
                setStockForm((current) => ({
                  ...current,
                  symbol: stock.symbol,
                  company_name: stock.name,
                }));
              }}
              placeholder="Search symbol"
              noResultsText="No matching stocks in local search data"
            />
            <input placeholder="Company name" value={stockForm.company_name} onChange={(e) => setStockForm({ ...stockForm, company_name: e.target.value })} />
            <input type="number" placeholder="Quantity" value={stockForm.quantity} onChange={(e) => setStockForm({ ...stockForm, quantity: e.target.value })} />
            <input type="number" placeholder="Average buy price" value={stockForm.average_buy_price} onChange={(e) => setStockForm({ ...stockForm, average_buy_price: e.target.value })} />
            <button className="btn" type="submit">Add Stock</button>
          </form>
        )}

        {!portfolioStocks.length ? (
          <p className="muted" style={{ marginTop: 20 }}>No stocks added yet.</p>
        ) : (
          <div style={{ display: "grid", gap: 20, marginTop: 20 }}>
            <div style={{ display: "grid", gap: 14 }}>
              {portfolioStocks.map((stock) => {
                const peRatio = analyticsBySymbol[stock.symbol]?.trailing_pe;
                const currentPrice = analyticsBySymbol[stock.symbol]?.current_price;
                const companyName = stock.company_name || analyticsBySymbol[stock.symbol]?.name || stock.symbol;

                return (
                  <article
                    key={stock.id}
                    role="button"
                    tabIndex={0}
                    onClick={() => navigate(`/stock/${encodeURIComponent(stock.symbol)}`)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        navigate(`/stock/${encodeURIComponent(stock.symbol)}`);
                      }
                    }}
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
                      gap: 16,
                      alignItems: "center",
                      padding: "18px 20px",
                      borderRadius: 20,
                      border: "1px solid rgba(17, 75, 95, 0.08)",
                      background: "rgba(255, 255, 255, 0.78)",
                      cursor: "pointer",
                    }}
                  >
                    <div style={{ minWidth: 0, gridColumn: "span 2" }}>
                      <p style={{ margin: 0, fontWeight: 700, fontSize: 18 }}>{stock.symbol}</p>
                      <p className="muted" style={{ margin: "6px 0 0" }}>{companyName}</p>
                    </div>
                    <div>
                      <p className="muted" style={{ margin: 0, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>P/E</p>
                      <p style={{ margin: "6px 0 0", fontWeight: 700 }}>{peRatio ?? "N/A"}</p>
                    </div>
                    <div>
                      <p className="muted" style={{ margin: 0, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>Quantity</p>
                      <p style={{ margin: "6px 0 0", fontWeight: 700 }}>{stock.quantity}</p>
                    </div>
                    <div>
                      <p className="muted" style={{ margin: 0, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>Price</p>
                      <p style={{ margin: "6px 0 0", fontWeight: 700 }}>{currentPrice ? `Rs ${currentPrice}` : "N/A"}</p>
                    </div>
                    <div style={{ display: "flex", justifyContent: "flex-end" }}>
                      <button
                        type="button"
                        onClick={async (event) => {
                          event.stopPropagation();
                          await portfolioApi.deleteStock(stock.id);
                          load();
                        }}
                      >
                        Remove
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>

            <div
              style={{
                padding: 20,
                borderRadius: 20,
                background: "rgba(255, 255, 255, 0.72)",
                border: "1px solid rgba(17, 75, 95, 0.08)",
              }}
            >
              <div style={{ marginBottom: 10 }}>
                <h3 style={{ margin: 0 }}>P/E Ratio Graph</h3>
                <p className="muted" style={{ margin: "6px 0 0" }}>All available stocks from this portfolio are shown together here.</p>
              </div>
              <PEChart items={portfolioPEItems} />
            </div>
          </div>
        )}
      </section>
    </>
  );
}
