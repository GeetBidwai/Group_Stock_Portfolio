import { axiosClient } from "../../../services/axiosClient";

export const compareStocksApi = {
  listPortfolioStocks: async () => {
    const response = await axiosClient.get("/portfolio/stocks/");
    return response.data;
  },
  compare: async (stockA, stockB, range = "6m") => {
    const response = await axiosClient.get("/portfolio/compare", {
      params: { stockA, stockB, range },
    });
    return response.data;
  },
};
