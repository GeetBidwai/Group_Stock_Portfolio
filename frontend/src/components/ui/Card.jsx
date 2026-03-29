export function Card({ as: Component = "section", className = "", interactive = false, children, ...props }) {
  const classes = ["panel", "card", interactive ? "card--interactive" : "", className].filter(Boolean).join(" ");

  return (
    <Component className={classes} {...props}>
      {children}
    </Component>
  );
}

export function MetricCard({ label, value, meta, tone = "primary", className = "", ...props }) {
  const classes = ["metric-tile", `metric-tile--${tone}`, className].filter(Boolean).join(" ");

  return (
    <article className={classes} {...props}>
      <p className="metric-tile__label">{label}</p>
      <p className="metric-tile__value">{value}</p>
      {meta ? <p className="metric-tile__meta">{meta}</p> : null}
    </article>
  );
}

export function ChartCard({ title, description, action, children, className = "", ...props }) {
  const classes = ["panel", "chart-card", className].filter(Boolean).join(" ");

  return (
    <section className={classes} {...props}>
      {(title || description || action) ? (
        <div className="chart-card__header">
          <div>
            {title ? <h3 className="chart-card__title">{title}</h3> : null}
            {description ? <p className="chart-card__description">{description}</p> : null}
          </div>
          {action || null}
        </div>
      ) : null}
      <div className="chart-card__body">{children}</div>
    </section>
  );
}
