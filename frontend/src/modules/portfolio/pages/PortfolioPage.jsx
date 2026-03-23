import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { portfolioApi } from "../services/portfolioApi";

const CHART_COLORS = ["#167c80", "#28b8b0", "#77c9e3", "#f2bf5e", "#ef6f6c", "#7b6ee6"];

export function PortfolioPage() {
  const navigate = useNavigate();
  const [portfolios, setPortfolios] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [selectedSector, setSelectedSector] = useState("");
  const [selectedSectorCard, setSelectedSectorCard] = useState("");
  const [newSectorName, setNewSectorName] = useState("");
  const [showAddSectorInput, setShowAddSectorInput] = useState(false);
  const [typeForm, setTypeForm] = useState({ name: "", description: "" });
  const [error, setError] = useState("");

  async function load() {
    try {
      const [portfolioData, sectorData] = await Promise.all([
        portfolioApi.listTypes(),
        portfolioApi.listSectors(),
      ]);
      setPortfolios(portfolioData);
      setSectors(sectorData);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const chartData = useMemo(() => {
    const buckets = portfolios.reduce((accumulator, portfolio) => {
      const key = portfolio.sector_name || "Unassigned";
      accumulator[key] = (accumulator[key] || 0) + 1;
      return accumulator;
    }, {});

    const total = portfolios.length || 1;
    return Object.entries(buckets).map(([name, value]) => ({
      name,
      value,
      percentage: Math.round((value / total) * 100),
    }));
  }, [portfolios]);

  const sectorPortfolioCounts = useMemo(() => {
    return portfolios.reduce((accumulator, portfolio) => {
      const key = portfolio.sector_name || "Unassigned";
      accumulator[key] = (accumulator[key] || 0) + 1;
      return accumulator;
    }, {});
  }, [portfolios]);

  return (
    <>
      <section className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>Portfolio Studio</p>
            <h1 style={{ marginBottom: 6 }}>Portfolio Management</h1>
            <p className="muted" style={{ margin: 0 }}>Navigate your portfolio structure by sector first, then drill down into portfolios and stocks.</p>
          </div>
          <div style={{ display: "flex", gap: 14, flexWrap: "wrap", justifyContent: "flex-end" }}>
            <button
              type="button"
              onClick={() => navigate("/recommendations")}
              style={{
                minWidth: 220,
                padding: "16px 18px",
                borderRadius: 20,
                background: "linear-gradient(135deg, rgba(17, 75, 95, 0.08), rgba(26, 147, 111, 0.12))",
                border: "1px solid rgba(17, 75, 95, 0.08)",
                cursor: "pointer",
                textAlign: "left",
              }}
            >
              <p className="muted" style={{ margin: 0 }}>Recommendations</p>
              <p style={{ margin: "6px 0 0", fontSize: 18, fontWeight: 700 }}>View Stocks</p>
            </button>
            <div
              style={{
                minWidth: 220,
                padding: "16px 18px",
                borderRadius: 20,
                background: "linear-gradient(135deg, rgba(17, 75, 95, 0.08), rgba(26, 147, 111, 0.12))",
                border: "1px solid rgba(17, 75, 95, 0.08)",
              }}
            >
              <p className="muted" style={{ margin: 0 }}>Sectors</p>
              <p style={{ margin: "6px 0 0", fontSize: 32, fontWeight: 700 }}>{sectors.length}</p>
            </div>
          </div>
        </div>
        {error && <p>{error}</p>}
      </section>

      <section className="grid two">
        <div className="panel">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
            <div>
              <h3 style={{ margin: 0 }}>Create Portfolio Type</h3>
              <p className="muted" style={{ margin: "8px 0 0" }}>Select a sector first so the portfolio is automatically grouped in the right hierarchy.</p>
            </div>
            <button
              type="button"
              onClick={() => setShowAddSectorInput((current) => !current)}
              style={{
                padding: "10px 14px",
                borderRadius: 14,
                border: "1px solid rgba(17, 75, 95, 0.12)",
                background: "rgba(255, 255, 255, 0.72)",
                cursor: "pointer",
              }}
            >
              {showAddSectorInput ? "Close Sector" : "Add Sector"}
            </button>
          </div>

          <form className="form" onSubmit={async (e) => {
            e.preventDefault();
            await portfolioApi.createType({
              ...typeForm,
              sector: selectedSector ? Number(selectedSector) : null,
            });
            setTypeForm({ name: "", description: "" });
            setSelectedSector("");
            setNewSectorName("");
            setShowAddSectorInput(false);
            load();
          }}>
            <div style={{ display: "grid", gap: 10 }}>
              <label className="muted" htmlFor="portfolio-name" style={{ fontSize: 13 }}>Portfolio Name</label>
              <input id="portfolio-name" placeholder="Name" value={typeForm.name} onChange={(e) => setTypeForm({ ...typeForm, name: e.target.value })} />
            </div>

            <div style={{ display: "grid", gap: 10 }}>
              <label className="muted" htmlFor="portfolio-sector" style={{ fontSize: 13 }}>Sector</label>
              <select id="portfolio-sector" value={selectedSector} onChange={(e) => setSelectedSector(e.target.value)}>
                <option value="">Select sector</option>
                {sectors.map((sector) => <option key={sector.id} value={sector.id}>{sector.name}</option>)}
              </select>
            </div>

            {showAddSectorInput && (
              <div
                style={{
                  padding: 18,
                  borderRadius: 18,
                  background: "rgba(17, 75, 95, 0.04)",
                  border: "1px dashed rgba(17, 75, 95, 0.16)",
                }}
              >
                <div className="flex flex-col gap-3 md:flex-row" style={{ alignItems: "end" }}>
                  <div style={{ flex: 1, display: "grid", gap: 10 }}>
                    <label className="muted" htmlFor="new-sector-name" style={{ fontSize: 13 }}>New Sector</label>
                    <input
                      id="new-sector-name"
                      placeholder="New sector name"
                      value={newSectorName}
                      onChange={(e) => setNewSectorName(e.target.value)}
                    />
                  </div>
                  <button
                    className="btn"
                    type="button"
                    style={{ minWidth: 140 }}
                    onClick={async () => {
                      const trimmedName = newSectorName.trim();
                      if (!trimmedName) {
                        return;
                      }
                      const createdSector = await portfolioApi.createSector({ name: trimmedName });
                      const sectorData = await portfolioApi.listSectors();
                      setSectors(sectorData);
                      setSelectedSector(String(createdSector.id));
                      setNewSectorName("");
                      setShowAddSectorInput(false);
                    }}
                  >
                    Save Sector
                  </button>
                </div>
              </div>
            )}

            <div style={{ display: "grid", gap: 10 }}>
              <label className="muted" htmlFor="portfolio-description" style={{ fontSize: 13 }}>Description</label>
              <input id="portfolio-description" placeholder="Description" value={typeForm.description} onChange={(e) => setTypeForm({ ...typeForm, description: e.target.value })} />
            </div>

            <button className="btn" type="submit">Create Type</button>
          </form>
        </div>

        <div className="panel">
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", flexWrap: "wrap", marginBottom: 12 }}>
            <div>
              <h3 style={{ margin: 0 }}>Portfolio Analysis</h3>
              <p className="muted" style={{ margin: "8px 0 0" }}>Snapshot of portfolio distribution by sector.</p>
            </div>
          </div>

          {chartData.length ? (
            <>
              <div style={{ height: 250 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={56} outerRadius={96} paddingAngle={2}>
                      {chartData.map((entry, index) => (
                        <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} stroke="#ffffff" strokeWidth={3} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value, _name, entry) => [`${value} portfolios`, entry.payload.name]} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div style={{ display: "grid", gap: 10 }}>
                {chartData.map((item, index) => (
                  <div key={item.name} style={{ display: "grid", gridTemplateColumns: "16px 1fr auto", gap: 10, alignItems: "center" }}>
                    <span style={{ width: 12, height: 12, borderRadius: 999, background: CHART_COLORS[index % CHART_COLORS.length] }} />
                    <span className="muted">{item.name}</span>
                    <strong>{item.value} ({item.percentage}%)</strong>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div
              style={{
                minHeight: 260,
                display: "grid",
                placeItems: "center",
                borderRadius: 22,
                background: "linear-gradient(135deg, rgba(17, 75, 95, 0.05), rgba(26, 147, 111, 0.09))",
                border: "1px dashed rgba(17, 75, 95, 0.16)",
                textAlign: "center",
                padding: 24,
              }}
            >
              <p className="muted" style={{ margin: 0 }}>Create portfolios to generate analysis.</p>
            </div>
          )}
        </div>
      </section>

      <section className="panel">
        <h3>Sectors</h3>
        {!sectors.length ? (
          <p className="muted">No sectors created yet.</p>
        ) : (
          <div style={{ display: "grid", gap: 12 }}>
            {sectors.map((sector) => (
              <button
                key={sector.id}
                type="button"
                onClick={() => {
                  setSelectedSectorCard(sector.name);
                  navigate(`/portfolio/sector/${encodeURIComponent(sector.name)}`);
                }}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 16,
                  padding: "16px 18px",
                  borderRadius: 18,
                  border: "1px solid rgba(17, 75, 95, 0.08)",
                  background: selectedSectorCard === sector.name ? "rgba(17, 75, 95, 0.07)" : "rgba(255, 255, 255, 0.72)",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                <div>
                  <p style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>{sector.name}</p>
                  <p className="muted" style={{ margin: "6px 0 0" }}>{sectorPortfolioCounts[sector.name] || 0} portfolios</p>
                </div>
                <span style={{ fontSize: 20 }}>→</span>
              </button>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
