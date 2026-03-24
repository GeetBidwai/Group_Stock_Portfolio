import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../modules/auth/hooks/useAuth";
import { featureFlags } from "../utils/featureFlags";

export function AppLayout() {
  const { logout, user } = useAuth();

  return (
    <div className="page-shell">
      <div className="nav-shell">
        <aside className="panel sidebar">
          <div>
            <h2>Market Atlas</h2>
            <p className="muted">{user?.username}</p>
          </div>
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/portfolio">Portfolio</NavLink>
          <NavLink to="/compare">Compare Stocks</NavLink>
          <NavLink to="/risk">Risk</NavLink>
          <NavLink to="/clustering">Clustering</NavLink>
          <NavLink to="/forecast">Forecast</NavLink>
          {featureFlags.sentiment && <NavLink to="/sentiment">Sentiment</NavLink>}
          {featureFlags.commodities && <NavLink to="/commodities">Gold/Silver</NavLink>}
          {featureFlags.crypto && <NavLink to="/btc">BTC Forecast</NavLink>}
          <button type="button" onClick={logout}>Logout</button>
        </aside>
        <main className="grid" style={{ alignContent: "start" }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
