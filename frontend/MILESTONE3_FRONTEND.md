# Milestone 3 — Frontend Integration Steps

## 1. Copy files

Copy into `frontend/src/`:

```
services/sustainabilityApi.js
components/GlassCard.jsx
components/StatCard.jsx
components/ProgressBar.jsx
components/StatusStates.jsx
components/AnalyzeForm.jsx
charts/SustainabilityPieChart.jsx
charts/SustainabilityBarChart.jsx
charts/SustainabilityAreaChart.jsx
charts/SustainabilityLineChart.jsx
charts/GaugeChart.jsx
pages/SustainabilityDashboard.jsx
pages/EnvironmentalImpactPage.jsx
pages/CircularEconomyPage.jsx
pages/WasteScoringPage.jsx
pages/RecommendationPage.jsx
pages/SustainabilityReportPage.jsx
```

## 2. Install recharts (if not already installed)

```powershell
npm install recharts
```

## 3. Add routes

In your router file (e.g. `App.jsx` or `router.jsx`), add:

```jsx
import SustainabilityDashboard from "./pages/SustainabilityDashboard";
import EnvironmentalImpactPage from "./pages/EnvironmentalImpactPage";
import CircularEconomyPage from "./pages/CircularEconomyPage";
import WasteScoringPage from "./pages/WasteScoringPage";
import RecommendationPage from "./pages/RecommendationPage";
import SustainabilityReportPage from "./pages/SustainabilityReportPage";

// inside your <Routes>
<Route path="/sustainability" element={<SustainabilityDashboard />} />
<Route path="/sustainability/environmental-impact" element={<EnvironmentalImpactPage />} />
<Route path="/sustainability/circular-economy" element={<CircularEconomyPage />} />
<Route path="/sustainability/waste-scoring" element={<WasteScoringPage />} />
<Route path="/sustainability/recommendations" element={<RecommendationPage />} />
<Route path="/sustainability/report" element={<SustainabilityReportPage />} />
```

## 4. Environment variable

Add to `frontend/.env`:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## 5. Notes

- All pages assume the JWT token is stored in `localStorage` under the key
  `access_token` (matches Milestone 1 auth flow). Update the key name in
  `services/sustainabilityApi.js` if your login page stores it differently.
- Every page (except the main Dashboard, which reads `/api/dashboard/summary`)
  includes its own **Analyze a Waste Batch** form since `/api/sustainability/analyze`
  is a per-batch endpoint — run an analysis on any page and its charts populate.
- Loading / error / empty states are handled on every page per Task 8 requirements.
