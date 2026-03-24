import { apiClient } from "../../../services/apiClient";

export const clusteringApi = {
  listClusters: ({ method = "pca", k = 3, portfolioId } = {}) => {
    const params = new URLSearchParams({
      method,
      k: String(k),
    });
    if (portfolioId) {
      params.set("portfolio_id", String(portfolioId));
    }
    return apiClient.get(`/cluster-stocks/?${params.toString()}`);
  },
};
