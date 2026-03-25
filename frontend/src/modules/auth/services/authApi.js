import { apiClient, clearTokens } from "../../../services/apiClient";

export const authApi = {
  register: (payload) => apiClient.post("/auth/register", payload),
  createTelegramLinkSession: () => apiClient.post("/auth/signup/telegram-link/session", {}),
  getTelegramLinkStatus: (token) => apiClient.get(`/auth/signup/telegram-link/status/${token}`),
  completeTelegramSignup: (payload) => apiClient.post("/auth/signup/telegram-link/complete", payload),
  login: (payload) => apiClient.post("/auth/login", payload),
  me: () => apiClient.get("/auth/me"),
  logout: (refresh) => apiClient.post("/auth/logout", { refresh }),
  sessions: () => apiClient.get("/auth/sessions"),
  requestResetOtp: (payload) => apiClient.post("/auth/request-reset-otp", payload),
  verifyResetOtp: (payload) => apiClient.post("/auth/verify-otp", payload),
  resetPasswordWithToken: (payload) => apiClient.post("/auth/reset-password", payload),
  requestOtp: (payload) => apiClient.post("/auth/forgot-password/request-otp", payload),
  verifyOtp: (payload) => apiClient.post("/auth/forgot-password/verify-otp", payload),
  resetPassword: (payload) => apiClient.post("/auth/forgot-password/reset-password", payload),
  clearTokens,
};
