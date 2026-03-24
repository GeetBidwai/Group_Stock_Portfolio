import { apiClient } from "../../../services/apiClient";

export const stockApi = {
  search: (query) => apiClient.get(`/stocks/search?q=${encodeURIComponent(query)}`),
  analytics: (symbol) => apiClient.get(`/stocks/${symbol}/analytics`),
  riskList: () => apiClient.get("/stocks/risk/"),
  compare: (payload) => apiClient.post("/portfolio/compare", payload),
  risk: (payload) => apiClient.post("/stock/risk-categorization", payload),
  forecast: (payload) => apiClient.post("/stock/forecast", payload),
};
