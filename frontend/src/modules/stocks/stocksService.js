import { apiClient } from "../../services/apiClient";

export const stocksService = {
  listMarkets: () => apiClient.get("/stocks/markets/"),
  listSectors: (marketCode) => apiClient.get(`/stocks/markets/${encodeURIComponent(marketCode)}/sectors/`),
  listStocks: (sectorId) => apiClient.get(`/stocks/sectors/${encodeURIComponent(sectorId)}/stocks/`),
  addToPortfolio: (stockId) => apiClient.post("/portfolio/add/", { stock_id: stockId }),
};
