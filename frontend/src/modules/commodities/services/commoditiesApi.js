import { apiClient } from "../../../services/apiClient";

export const commoditiesApi = {
  correlation: () => apiClient.get("/commodities/gold-silver-correlation"),
  gold: () => apiClient.get("/commodities/gold/"),
  silver: () => apiClient.get("/commodities/silver/"),
  enhancedCorrelation: () => apiClient.get("/commodities/correlation/"),
};
