import { useState } from "react";

import { DownloadReportButton } from "../components/DownloadReportButton";
import { NewsList } from "../components/NewsList";
import { SentimentSummaryCard } from "../components/SentimentSummaryCard";
import { StockSearch } from "../components/StockSearch";
import { sentimentApi } from "../services/sentimentApi";

export function SentimentPage() {
  const [query, setQuery] = useState("");
  const [selectedStock, setSelectedStock] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");

  const canAnalyze = Boolean(selectedStock?.symbol);

  async function handleAnalyze(event) {
    event.preventDefault();
    if (!canAnalyze) {
      return;
    }

    try {
      setLoading(true);
      setError("");
      const payload = await sentimentApi.analyze({ stock: selectedStock.symbol });
      setResult(payload);
      setError("");
    } catch (err) {
      setResult(null);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDownloadReport() {
    if (!result?.stock) {
      return;
    }

    try {
      setDownloading(true);
      setError("");
      await sentimentApi.downloadReport(result.stock);
    } catch (err) {
      setError(err.message);
    } finally {
      setDownloading(false);
    }
  }

  return (
    <>
      <section className="panel">
        <p className="muted" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.18em", fontSize: 12 }}>
          Sentiment Studio
        </p>
        <h1 style={{ marginBottom: 6 }}>News-based Sentiment Analysis</h1>
        <p className="muted" style={{ margin: 0 }}>
          Search a stock, analyze recent news coverage, and generate a report without leaving the platform.
        </p>
      </section>

      <section className="panel" style={{ marginTop: 18 }}>
        <form className="form" onSubmit={handleAnalyze}>
          <StockSearch
            value={query}
            onChange={(nextValue) => {
              setQuery(nextValue);
              if (selectedStock && nextValue !== selectedStock.symbol) {
                setSelectedStock(null);
              }
            }}
            onSelect={(stock) => {
              setSelectedStock(stock);
              setQuery(stock.symbol);
            }}
          />
          <button className="btn" type="submit" disabled={!canAnalyze || loading} style={{ opacity: !canAnalyze || loading ? 0.7 : 1 }}>
            {loading ? "Analyzing..." : "Analyze Sentiment"}
          </button>
        </form>

        {selectedStock?.name && (
          <p className="muted" style={{ marginTop: 14, marginBottom: 0 }}>
            Selected: <strong style={{ color: "var(--text)" }}>{selectedStock.symbol}</strong> - {selectedStock.name}
          </p>
        )}
        {error && <p style={{ color: "#c05353", marginTop: 14, marginBottom: 0 }}>{error}</p>}
        {!error && result?.message && (
          <p style={{ color: result?.articles?.length ? "#8b6a1d" : "#5f6b6d", marginTop: 14, marginBottom: 0 }}>
            {result.message}
          </p>
        )}
      </section>

      {result && (
        <>
          <div style={{ marginTop: 18 }}>
            <SentimentSummaryCard result={result} />
          </div>

          <section className="panel" style={{ marginTop: 18, paddingTop: 20, paddingBottom: 20 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
              <div>
                <h2 style={{ marginBottom: 6 }}>Recent News Coverage</h2>
                <p className="muted" style={{ margin: 0 }}>
                  Articles used to compute the sentiment signal for the selected stock.
                </p>
              </div>
              <DownloadReportButton disabled={!result?.stock || !(result?.articles || []).length} loading={downloading} onClick={handleDownloadReport} />
            </div>
          </section>

          {(result.articles || []).length ? (
            <div style={{ marginTop: 14 }}>
              <NewsList articles={result.articles || []} />
            </div>
          ) : (
            <section className="panel" style={{ marginTop: 14 }}>
              <p className="muted" style={{ margin: 0 }}>
                No live news articles are available right now. The sentiment card is being kept neutral until a news source responds.
              </p>
            </section>
          )}
        </>
      )}
    </>
  );
}
