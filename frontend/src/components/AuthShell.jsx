import { Logo } from "./Logo";

export function AuthShell({ children, panelClassName = "" }) {
  const panelClasses = ["panel", "auth-panel", panelClassName].filter(Boolean).join(" ");

  return (
    <div className="page-shell auth-shell">
      <header className="auth-header">
        <Logo />
      </header>
      <div className="auth-content">
        <div className={panelClasses}>
          {children}
        </div>
      </div>
    </div>
  );
}
