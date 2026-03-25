import { useState } from "react";
import { Link } from "react-router-dom";

export function Logo({ to = "/", className = "", showName = true }) {
  const [hasError, setHasError] = useState(false);
  const classes = ["brand-link", className].filter(Boolean).join(" ");

  return (
    <Link className={classes} to={to} aria-label="Go to dashboard">
      {hasError ? (
        <span className="brand-fallback">Stock Analytics Platform</span>
      ) : (
        <>
          <img
            className="brand-logo"
            src="/brand-logo.svg"
            alt="Stock Analytics Platform"
            loading="lazy"
            onError={() => setHasError(true)}
          />
          {showName ? <span className="brand-name">Stock Analytics Platform</span> : null}
        </>
      )}
    </Link>
  );
}
