import { apiClient, clearTokens } from "../../../services/apiClient";

export const authApi = {
  register: (payload) => apiClient.post("/auth/register", payload),
  login: (payload) => apiClient.post("/auth/login", payload),
  me: () => apiClient.get("/auth/me"),
  logout: (refresh) => apiClient.post("/auth/logout", { refresh }),
  sessions: () => apiClient.get("/auth/sessions"),
  requestOtp: (payload) => apiClient.post("/auth/forgot-password/request-otp", payload),
  verifyOtp: (payload) => apiClient.post("/auth/forgot-password/verify-otp", payload),
  resetPassword: (payload) => apiClient.post("/auth/forgot-password/reset-password", payload),
  clearTokens,
};
