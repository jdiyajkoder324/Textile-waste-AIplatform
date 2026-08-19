import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { AuthProvider, useAuth } from "./context/AuthContext";
import { AnalysisProvider } from "./context/AnalysisContext";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardLayout from "./layouts/DashboardLayout";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Inventory from "./pages/Inventory";
import Upload from "./pages/Upload";
import Analysis from "./pages/Analysis";
import VerifyOtp from "./pages/VerifyOtp";
import History from "./pages/History";
import AnalysisDetails from "./pages/AnalysisDetails";

// Milestone 3 — Sustainability Intelligence pages
import SustainabilityDashboard from "./pages/SustainabilityDashboard";
import EnvironmentalImpactPage from "./pages/EnvironmentalImpactPage";
import CircularEconomyPage from "./pages/CircularEconomyPage";
import WasteScoringPage from "./pages/WasteScoringPage";
import RecommendationPage from "./pages/RecommendationPage";
//import SustainabilityReportPage from "./pages/SustainabilityReportPage";
import Profile from "./pages/Profile";
import AdminUserManagement from "./pages/AdminUserManagement";


import RecyclerDashboard from "./pages/RecyclerDashboard";
import ManufacturerDashboard from "./pages/ManufacturerDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import ReportsCenter from "./pages/ReportsCenter";

function RootRedirect() {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return null;
  return <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />;
}

function App() {
  return (
    <AuthProvider>
      <AnalysisProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<RootRedirect />} />

            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/verify-otp" element={<VerifyOtp />} />

            {/* Authenticated routes — persistent sidebar layout */}
            <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/inventory" element={<Inventory />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/analysis" element={<Analysis />} />
              <Route path="/history" element={<History />} />
              <Route path="/analysis/:id" element={<AnalysisDetails />} />
              <Route path="/profile" element={<Profile />} />

              <Route path="/sustainability" element={<SustainabilityDashboard />} />
              <Route path="/sustainability/environmental-impact" element={<EnvironmentalImpactPage />} />
              <Route path="/sustainability/circular-economy" element={<CircularEconomyPage />} />
              <Route path="/sustainability/waste-scoring" element={<WasteScoringPage />} />
              <Route path="/sustainability/recommendations" element={<RecommendationPage />} />
              {/* <Route path="/sustainability/report" element={<SustainabilityReportPage />} /> */}
              <Route path="/analytics/recycler" element={<RecyclerDashboard />} />
              <Route path="/analytics/manufacturer" element={<ManufacturerDashboard />} />
              <Route path="/analytics/admin" element={<AdminDashboard />} />
              <Route path="/reports" element={<ReportsCenter />} />
              <Route path="/admin/users" element={<AdminUserManagement />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AnalysisProvider>
    </AuthProvider>
  );
}

export default App;