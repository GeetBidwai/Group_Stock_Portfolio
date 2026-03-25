import { apiClient } from "../../../services/apiClient";

export const telegramAuthApi = {
  verifyTelegram: (payload) => apiClient.post("/auth/telegram/", payload),
  setMpin: (payload) => apiClient.post("/auth/set-mpin/", payload),
  loginMpin: (payload) => apiClient.post("/auth/login-mpin/", payload),
  requestMobileOtp: (payload) => apiClient.post("/auth/mobile/request-otp/", payload),
  verifyMobileOtp: (payload) => apiClient.post("/auth/mobile/verify-otp/", payload),
  resetMpin: (payload) => apiClient.post("/auth/reset-mpin/", payload),
};
