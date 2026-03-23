import { apiClient } from "../../../services/apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export const sentimentApi = {
  analyze: (payload) => apiClient.post("/sentiment/analyze/", payload),
  async downloadReport(stock) {
    const tokens = apiClient.getTokens();
    const response = await fetch(`${API_BASE_URL}/sentiment/report/?stock=${encodeURIComponent(stock)}`, {
      headers: tokens.access ? { Authorization: `Bearer ${tokens.access}` } : {},
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || errorBody.error || "Unable to download report");
    }

    const blob = await response.blob();
    const objectUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = `${stock}_sentiment_report.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(objectUrl);
  },
};

