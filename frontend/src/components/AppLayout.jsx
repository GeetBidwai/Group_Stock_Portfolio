import { NavLink, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../modules/auth/hooks/useAuth";
import { featureFlags } from "../utils/featureFlags";
import { Logo } from "./Logo";
import { PersonalAssistant } from "./PersonalAssistant";

function NavIcon({ path }) {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={path} />
    </svg>
  );
}

const ICONS = {
  stocks: "M3 17l6-6 4 4 7-8M3 7h5M16 7h5M3 21h18",
  portfolio: "M4 7h16M6 4h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z",
  quality: "M12 3l2.6 5.3 5.9.9-4.2 4.1 1 5.8L12 16.8 6.7 19l1-5.8L3.5 9.2l5.9-.9L12 3z",
  compare: "M6 5h4v14H6zM14 9h4v10h-4z",
  risk: "M12 3l8 4v5c0 5-3.4 8.7-8 10-4.6-1.3-8-5-8-10V7l8-4z",
  clustering: "M6 6h5v5H6zM13 6h5v5h-5zM6 13h5v5H6zM16 16h.01",
  forecast: "M4 19V5M4 19h16M8 15l3-3 3 2 5-6",
  sentiment: "M5 18h14M7 15V9M12 15V5M17 15v-3",
  commodities: "M12 3v18M6 8c0-2 1.8-3 4-3h4c2.2 0 4 1 4 3s-1.8 3-4 3h-4c-2.2 0-4 1-4 3s1.8 3 4 3h4c2.2 0 4-1 4-3",
  btc: "M10 4v16M14 4v16M7 7h8a3 3 0 0 1 0 6H7h9a3 3 0 0 1 0 6H7",
};

export function AppLayout() {
  const location = useLocation();
  const { logout, user } = useAuth();
  const navItems = [
    { to: "/stocks", label: "Stocks", description: "Curated market browser", icon: "stocks" },
    { to: "/portfolio", label: "Portfolio", description: "Sector and holdings view", icon: "portfolio" },
    { to: "/quality-stocks", label: "Quality Stocks", description: "AI research reports", icon: "quality" },
    { to: "/compare", label: "Compare", description: "Side-by-side stock analysis", icon: "compare" },
    { to: "/risk", label: "Risk", description: "Stability and exposure signals", icon: "risk" },
    { to: "/clustering", label: "Clustering", description: "Portfolio grouping insights", icon: "clustering" },
    { to: "/forecast", label: "Forecast", description: "Projection studio", icon: "forecast" },
    ...(featureFlags.sentiment ? [{ to: "/sentiment", label: "Sentiment", description: "News-based market tone", icon: "sentiment" }] : []),
    ...(featureFlags.commodities ? [{ to: "/commodities", label: "Gold/Silver", description: "Commodity intelligence", icon: "commodities" }] : []),
    ...(featureFlags.crypto ? [{ to: "/btc", label: "BTC Forecast", description: "Crypto outlook", icon: "btc" }] : []),
  ];
  const currentSection = navItems.find((item) => location.pathname === item.to || location.pathname.startsWith(`${item.to}/`));
  const initials = String(user?.username || "U").slice(0, 1).toUpperCase();

  return (
    <div className="page-shell">
      <div className="nav-shell app-shell">
        <aside className="panel sidebar app-sidebar">
          <div className="sidebar-brand app-sidebar__brand">
            <Logo />
            <div className="app-sidebar__identity">
              <p className="muted app-sidebar__caption">Market Atlas Workspace</p>
              <p className="app-nav__label">{user?.username || "Guest"}</p>
            </div>
          </div>
          <div className="app-sidebar__section">
            <p className="app-sidebar__section-title">Navigation</p>
            <nav className="app-nav" aria-label="Primary">
              {navItems.map((item) => (
                <NavLink key={item.to} to={item.to} className={({ isActive }) => `app-nav__link${isActive ? " active" : ""}`}>
                  <span className="app-nav__icon">
                    <NavIcon path={ICONS[item.icon]} />
                  </span>
                  <span className="app-nav__text">
                    <span className="app-nav__label">{item.label}</span>
                    <span className="app-nav__meta">{item.description}</span>
                  </span>
                  <span className="app-nav__indicator" />
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
              <p className="muted app-topbar__summary">A cleaner premium dashboard shell on top of the same working flows.</p>
            </div>
            <div className="app-topbar__actions">
              <span className="app-chip">Live workspace</span>
              <div className="app-profile" aria-label="Profile">
                {initials}
              </div>
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
