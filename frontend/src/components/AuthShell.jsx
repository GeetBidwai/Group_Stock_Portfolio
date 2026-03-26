import { Logo } from "./Logo";
import { AuthAssistant } from "./AuthAssistant";

export function AuthShell({ children, panelClassName = "", assistantPage = "login" }) {
  const panelClasses = ["panel", "auth-panel", panelClassName].filter(Boolean).join(" ");

  return (
    <div className="page-shell auth-shell">
      <header className="auth-header">
        <Logo />
      </header>
      <div className="auth-content">
        <div className="auth-stage">
          <div className={panelClasses}>
            {children}
          </div>
          <AuthAssistant page={assistantPage} />
        </div>
      </div>
    </div>
  );
}
