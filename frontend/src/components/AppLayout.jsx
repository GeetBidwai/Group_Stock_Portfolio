import { NavLink, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../modules/auth/hooks/useAuth";
import { featureFlags } from "../utils/featureFlags";
import { Logo } from "./Logo";
import { PersonalAssistant } from "./PersonalAssistant";

export function AppLayout() {
  const location = useLocation();
  const { logout, user } = useAuth();
  const navItems = [
    { to: "/stocks", label: "Stocks", description: "Curated market browser" },
    { to: "/portfolio", label: "Portfolio", description: "Sector and holdings view" },
    { to: "/quality-stocks", label: "Quality Stocks", description: "AI research reports" },
    { to: "/compare", label: "Compare", description: "Side-by-side stock analysis" },
    { to: "/risk", label: "Risk", description: "Stability and exposure signals" },
    { to: "/clustering", label: "Clustering", description: "Portfolio grouping insights" },
    { to: "/forecast", label: "Forecast", description: "Projection studio" },
    ...(featureFlags.sentiment ? [{ to: "/sentiment", label: "Sentiment", description: "News-based market tone" }] : []),
    ...(featureFlags.commodities ? [{ to: "/commodities", label: "Gold/Silver", description: "Commodity intelligence" }] : []),
    ...(featureFlags.crypto ? [{ to: "/btc", label: "BTC Forecast", description: "Crypto outlook" }] : []),
  ];
  const currentSection = navItems.find((item) => location.pathname === item.to || location.pathname.startsWith(`${item.to}/`));

  return (
    <div className="page-shell">
      <div className="nav-shell app-shell">
        <aside className="panel sidebar app-sidebar">
          <div className="sidebar-brand app-sidebar__brand">
            <Logo />
            <div className="app-sidebar__identity">
              <p className="muted app-sidebar__caption">Market Atlas Workspace</p>
              <p className="app-sidebar__user">{user?.username}</p>
            </div>
          </div>
          <div className="app-sidebar__section">
            <p className="app-sidebar__section-title">Navigation</p>
            <nav className="app-nav" aria-label="Primary">
              {navItems.map((item) => (
                <NavLink key={item.to} to={item.to} className="app-nav__link">
                  <span className="app-nav__label">{item.label}</span>
                  <span className="app-nav__meta">{item.description}</span>
                </NavLink>
              ))}
            </nav>
          </div>
          <div className="app-sidebar__foot">
            <div className="app-sidebar__status">
              <span className="app-sidebar__status-dot" />
              Stable project flow preserved
            </div>
            <button type="button" className="app-sidebar__logout" onClick={logout}>Logout</button>
          </div>
        </aside>
        <main className="grid app-main" style={{ alignContent: "start" }}>
          <section className="panel app-topbar">
            <div>
              <p className="app-topbar__eyebrow">{currentSection?.label || "Analytics Workspace"}</p>
              <h1 className="app-topbar__title">{currentSection?.description || "Stable stock intelligence platform"}</h1>
              <p className="muted app-topbar__summary">
                Professional analytics surfaces with the existing functional flow kept intact.
              </p>
            </div>
            <div className="app-topbar__chips" aria-label="Workspace highlights">
              <span className="app-chip">Secure session</span>
              <span className="app-chip">Live analytics</span>
              <span className="app-chip">Premium UI refresh</span>
            </div>
          </section>
          <div className="app-content">
            <Outlet />
          </div>
        </main>
      </div>
      <PersonalAssistant />
    </div>
  );
}
