import { apiClient } from "../../../services/apiClient";

export const portfolioApi = {
  listTypes: () => apiClient.get("/portfolio-types/"),
  createType: (payload) => apiClient.post("/portfolio-types/", payload),
  updateType: (id, payload) => apiClient.patch(`/portfolio-types/${id}`, payload),
  deleteType: (id) => apiClient.delete(`/portfolio-types/${id}`),
  listSectors: () => apiClient.get("/sectors/"),
  createSector: (payload) => apiClient.post("/sectors/", payload),
  listStocks: () => apiClient.get("/portfolio-stocks/"),
  addStock: (payload) => apiClient.post("/portfolio-stocks/", payload),
  deleteStock: (id) => apiClient.delete(`/portfolio-stocks/${id}`),
  peComparison: () => apiClient.get("/portfolio/pe-comparison"),
  clustering: () => apiClient.get("/portfolio/clustering"),
  portfolioForecast: (payload) => apiClient.post("/stock/portfolio-forecast-next-day", payload),
};
