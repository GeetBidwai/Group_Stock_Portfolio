import { apiClient } from "../../../services/apiClient";

export const cryptoApi = {
  btcHourly: () => apiClient.get("/crypto/btcusd-hourly"),
};
