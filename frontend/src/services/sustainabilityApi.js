import axios from "axios";

// Reuses the same base client pattern as your existing Milestone 1/2
// services -- adjust BASE_URL / token key if your project names differ.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const analyzeSustainability = async (payload) => {
  const response = await apiClient.post("/api/sustainability/analyze", payload);
  return response.data;
};

export const getDashboardSummary = async () => {
  const response = await apiClient.get("/api/dashboard/summary");
  return response.data;
};

export const checkHealth = async () => {
  const response = await apiClient.get("/health");
  return response.data;
};

export default apiClient;
