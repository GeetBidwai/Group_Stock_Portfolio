import { apiClient } from "../../../services/apiClient";

export const qualityStocksApi = {
  snapshot: (portfolioId) => apiClient.post("/quality-stocks/snapshot/", { portfolio_id: portfolioId }),
  sectorSnapshot: (sectorName) => apiClient.post("/quality-stocks/sector-snapshot/", { sector_name: sectorName }),
  generate: (portfolioId, stockIds) =>
    apiClient.post("/quality-stocks/generate/", {
      portfolio_id: portfolioId,
      stock_ids: stockIds,
    }),
  sectorGenerate: (sectorName, stockIds) =>
    apiClient.post("/quality-stocks/sector-generate/", {
      sector_name: sectorName,
      stock_ids: stockIds,
    }),
  list: (portfolioId) =>
    apiClient.get(
      portfolioId
        ? `/quality-stocks/?portfolio_id=${encodeURIComponent(portfolioId)}`
        : "/quality-stocks/",
    ),
  detail: (id) => apiClient.get(`/quality-stocks/${id}/`),
  rerun: (id) => apiClient.post(`/quality-stocks/${id}/rerun/`, {}),
  remove: (id) => apiClient.delete(`/quality-stocks/${id}/`),
};
