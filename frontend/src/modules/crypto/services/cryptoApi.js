import { apiClient } from "../../../services/apiClient";

export const cryptoApi = {
  btcHourly: () => apiClient.get("/crypto/btcusd-hourly"),
  btcForecast: (range = "3m") => apiClient.get(`/crypto/btc-forecast/?range=${encodeURIComponent(range)}`),
};
