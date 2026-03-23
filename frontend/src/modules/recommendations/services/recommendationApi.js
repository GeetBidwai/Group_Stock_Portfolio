import { apiClient } from "../../../services/apiClient";

export const recommendationApi = {
  list: () => apiClient.get("/recommendations/"),
};

