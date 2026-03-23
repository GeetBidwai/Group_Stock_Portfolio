export function DownloadReportButton({ disabled, loading, onClick }) {
  return (
    <button className="btn" type="button" disabled={disabled || loading} onClick={onClick} style={{ opacity: disabled || loading ? 0.7 : 1 }}>
      {loading ? "Preparing report..." : "Download PDF Report"}
    </button>
  );
}

