import { Link } from "react-router-dom";

export function DashboardPage() {
  const cards = [
    { title: "Portfolio", path: "/portfolio", description: "Manage portfolio types and holdings." },
    { title: "Compare", path: "/compare", description: "Compare return, volatility, and Sharpe ratio." },
    { title: "Risk", path: "/risk", description: "Categorize stock risk using transparent rules." },
    { title: "Forecast", path: "/forecast", description: "Run explainable baseline forecasts." },
    { title: "Alternative Assets", path: "/commodities", description: "Study gold, silver, and BTC behavior." },
  ];

  return (
    <>
      <section className="panel">
        <h1>Dashboard</h1>
        <p className="muted">Protected feature hub with modular analytics paths.</p>
        <div style={{ marginTop: 16 }}>
          <Link to="/commodities" className="btn" style={{ display: "inline-flex", alignItems: "center" }}>
            Gold & Silver
          </Link>
        </div>
      </section>
      <section className="grid three">
        {cards.map((card) => (
          <Link key={card.path} to={card.path} className="panel">
            <h3>{card.title}</h3>
            <p className="muted">{card.description}</p>
          </Link>
        ))}
      </section>
    </>
  );
}
