export const featureFlags = {
  commodities: import.meta.env.VITE_FF_ENABLE_COMMODITIES !== "false",
  crypto: import.meta.env.VITE_FF_ENABLE_CRYPTO !== "false",
  clustering: import.meta.env.VITE_FF_ENABLE_CLUSTERING !== "false",
  forecasting: import.meta.env.VITE_FF_ENABLE_FORECASTING !== "false",
  sentiment: import.meta.env.VITE_FF_ENABLE_SENTIMENT !== "false",
};
