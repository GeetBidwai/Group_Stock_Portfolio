import { useState } from "react";

import { Card, MetricCard } from "../../../components/ui/Card";
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
      <Card className="sentiment-page-hero">
        <div>
          <p className="eyebrow">Sentiment Studio</p>
          <h1 style={{ marginBottom: 6 }}>News-based Sentiment Analysis</h1>
          <p className="muted" style={{ margin: 0 }}>
            Search a stock, analyze recent news coverage, and generate a report without leaving the platform.
          </p>
        </div>

        <form className="form sentiment-search-card" onSubmit={handleAnalyze}>
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

        <div className="metric-grid">
          <MetricCard label="Selected Stock" value={selectedStock?.symbol || "--"} meta={selectedStock?.name || "Choose a stock to analyze"} tone="primary" />
          <MetricCard label="Articles" value={(result?.articles || []).length} meta="Live news items used in the model output" tone="primary" />
          <MetricCard label="Overall Sentiment" value={result?.overall_sentiment || "Ready"} meta={result?.message || "Awaiting analysis"} tone="success" />
        </div>

        {selectedStock?.name && (
          <p className="muted" style={{ marginTop: 0, marginBottom: 0 }}>
            Selected: <strong style={{ color: "var(--text)" }}>{selectedStock.symbol}</strong> - {selectedStock.name}
          </p>
        )}
        {error ? <p className="form-error">{error}</p> : null}
        {!error && result?.message ? (
          <p className="muted" style={{ margin: 0 }}>
            {result.message}
          </p>
        ) : null}
      </Card>

      {result && (
        <>
          <div className="page-section">
            <SentimentSummaryCard result={result} />
          </div>

          <Card>
            <div className="card__header">
              <div>
                <h2 style={{ marginBottom: 6 }}>Recent News Coverage</h2>
                <p className="muted" style={{ margin: 0 }}>
                  Articles used to compute the sentiment signal for the selected stock.
                </p>
              </div>
              <DownloadReportButton disabled={!result?.stock || !(result?.articles || []).length} loading={downloading} onClick={handleDownloadReport} />
            </div>
          </Card>

          {(result.articles || []).length ? (
            <NewsList articles={result.articles || []} />
          ) : (
            <Card>
              <p className="muted" style={{ margin: 0 }}>
                No live news articles are available right now. The sentiment card is being kept neutral until a news source responds.
              </p>
            </Card>
          )}
        </>
      )}
    </>
  );
}
