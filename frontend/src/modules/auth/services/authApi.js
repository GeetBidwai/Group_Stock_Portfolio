import { apiClient, clearTokens } from "../../../services/apiClient";

export const authApi = {
  register: (payload) => apiClient.post("/auth/signup", payload),
  signup: (payload) => apiClient.post("/auth/signup", payload),
  login: (payload) => apiClient.post("/auth/login", payload),
  me: () => apiClient.get("/auth/me"),
  logout: (refresh) => apiClient.post("/auth/logout", { refresh }),
  sessions: () => apiClient.get("/auth/sessions"),
  clearTokens,
};
