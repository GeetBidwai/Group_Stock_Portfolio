import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "../components/AppLayout";
import { ProtectedRoute } from "./ProtectedRoute";
import { LoginPage } from "../modules/auth/pages/LoginPage";
import { SignupPage } from "../modules/auth/pages/SignupPage";
import { StocksPage } from "../modules/stocks";
import { PortfolioPage } from "../modules/portfolio/pages/PortfolioPage";
import { PortfolioAnalysisPage } from "../modules/portfolio/pages/PortfolioAnalysisPage";
import { StockDetailPage as PortfolioStockDetailPage } from "../modules/portfolio/pages/StockDetail";
import { SectorPortfolioPage } from "../modules/portfolio/pages/SectorPortfolioPage";
import { PortfolioDetailPage } from "../modules/portfolio/pages/PortfolioDetail";
import { CompareStocksPage } from "../modules/stock-comparison/pages/CompareStocks";
import { RiskPage } from "../modules/risk/pages/RiskPage";
import { ClusteringPage } from "../modules/clustering/pages/Clustering";
import { ForecastPage } from "../modules/forecasting/pages/Forecast";
import { ForecastResultPage } from "../modules/forecasting/pages/ForecastResultPage";
import { RecommendationPage } from "../modules/recommendations/pages/RecommendationPage";
import { SentimentPage } from "../modules/sentiment/pages/SentimentPage";
import { CommoditiesPage } from "../modules/commodities/pages/CommoditiesPage";
import { CryptoPage } from "../modules/crypto/pages/CryptoPage";
import { BTCForecastPage } from "../modules/crypto/pages/BTCForecastPage";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Navigate to="/stocks" replace />} />
            <Route path="/stocks" element={<StocksPage />} />
            <Route path="/portfolio" element={<PortfolioPage />} />
            <Route path="/portfolio/analysis" element={<PortfolioAnalysisPage />} />
            <Route path="/portfolio/sector/:sectorName" element={<SectorPortfolioPage />} />
            <Route path="/portfolio/:id" element={<PortfolioDetailPage />} />
            <Route path="/stock/:symbol" element={<PortfolioStockDetailPage />} />
            <Route path="/compare" element={<CompareStocksPage />} />
            <Route path="/risk" element={<RiskPage />} />
            <Route path="/clustering" element={<ClusteringPage />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/forecast/result" element={<ForecastResultPage />} />
            <Route path="/recommendations" element={<RecommendationPage />} />
            <Route path="/sentiment" element={<SentimentPage />} />
            <Route path="/commodities" element={<CommoditiesPage />} />
            <Route path="/crypto" element={<CryptoPage />} />
            <Route path="/btc" element={<BTCForecastPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
