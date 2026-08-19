import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: BASE_URL,
});

// Attach JWT token to every request automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If the token is expired/invalid, bounce to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem("token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default api;
export { BASE_URL };

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------
export async function loginUser(email, password) {
  try {
    const res = await api.post("/user/login", { email, password });
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || "Login failed");
  }
}

export async function registerUser(name, email, password, role) {
  try {
    const res = await api.post("/user/register", { name, email, password, role });
    return res.data;
  } catch (err) {
    const detail = err.response?.data?.detail;
    throw new Error(typeof detail === "string" ? detail : "Registration failed");
  }
}

// ---------------------------------------------------------------------------
// Waste / Inventory — legacy names kept so Dashboard.jsx keeps working as-is
// ---------------------------------------------------------------------------
export async function getWastes() {
  try {
    const res = await api.get("/waste/", { params: { page: 1, page_size: 1000 } });
    return res.data.items || res.data; // supports old and new response shape
  } catch (err) {
    throw new Error(err.response?.data?.detail || "Failed to fetch waste batches");
  }
}

export async function createWaste(wasteData) {
  try {
    const res = await api.post("/waste/", wasteData);
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || "Failed to create waste batch");
  }
}

export async function updateWaste(id, wasteData) {
  try {
    const res = await api.put(`/waste/${id}`, wasteData);
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || "Failed to update waste batch");
  }
}

export async function deleteWaste(id) {
  try {
    const res = await api.delete(`/waste/${id}`);
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || "Failed to delete waste batch");
  }
}

// ---------------------------------------------------------------------------
// Inventory page — search / filter / pagination / image upload
// ---------------------------------------------------------------------------
export async function getInventory({ search = "", fabricType = "All", status = "All", page = 1, pageSize = 8 } = {}) {
  try {
    const res = await api.get("/waste/", {
      params: {
        search: search || undefined,
        fabric_type: fabricType !== "All" ? fabricType : undefined,
        status: status !== "All" ? status : undefined,
        page,
        page_size: pageSize,
      },
    });
    return res.data; // { items, total, page, page_size, total_pages }
  } catch (err) {
    throw new Error(err.response?.data?.detail || "Failed to fetch inventory");
  }
}

export async function uploadWasteImage(file) {
  try {
    const formData = new FormData();
    formData.append("file", file);
    const res = await api.post("/waste/upload-image", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data.image_path;
  } catch (err) {
    throw new Error(err.response?.data?.detail || "Image upload failed");
  }
}

// ---------------------------------------------------------------------------
// Milestone 2 — Material Recognition & Waste Classification
// ---------------------------------------------------------------------------
export const uploadImage = (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);
  return api
    .post("/api/upload-image", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (evt) => {
        if (onProgress && evt.total) {
          onProgress(Math.round((evt.loaded * 100) / evt.total));
        }
      },
    })
    .then((r) => r.data);
};

// --- 2FA / OTP ---
export const loginStep1 = (email, password) =>
  api.post("/user/login", { email, password });

export const verifyOtp = (otp_session_id, otp) =>
  api.post("/user/verify-otp", { otp_session_id, otp });

export const resendOtp = (otp_session_id) =>
  api.post("/user/resend-otp", { otp_session_id });

export const getImagePreviewUrl = (imageId) => `${BASE_URL}/api/image/${imageId}/preview`;

export const runImageAnalysis = (imageId) =>
  api.post("/api/image-analysis", { image_id: imageId }).then((r) => r.data);

export const runMaterialClassification = (imageId) =>
  api.post(`/api/material-classification?image_id=${imageId}`).then((r) => r.data);

export const runWasteClassification = (imageId) =>
  api.post(`/api/waste-classification?image_id=${imageId}`).then((r) => r.data);

export const runRecyclabilityAssessment = (imageId) =>
  api.post(`/api/recyclability-assessment?image_id=${imageId}`).then((r) => r.data);

export const runRecyclingRecommendation = (imageId) =>
  api.post(`/api/recycling-recommendation?image_id=${imageId}`).then((r) => r.data);

export const getMaterialHistory = (limit = 50) =>
  api.get(`/api/material-history?limit=${limit}`).then((r) => r.data);

export const getWasteHistory = (limit = 50) =>
  api.get(`/api/waste-history?limit=${limit}`).then((r) => r.data);

export const getRecommendations = (limit = 50) =>
  api.get(`/api/recommendations?limit=${limit}`).then((r) => r.data);

export const downloadAnalysisReport = async (imageId, format = "pdf") => {
  const response = await api.get(`/api/analysis-report?image_id=${imageId}&format=${format}`, {
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `analysis-report-${imageId.slice(0, 8)}.${format}`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};
export const downloadReport = downloadAnalysisReport;  

// --- Analysis History (real backend) ---
export const uploadAndAnalyze = (file, wasteBatchId = null) => {
  const formData = new FormData();
  formData.append("file", file);
  const url = wasteBatchId
    ? `/api/upload-image?waste_batch_id=${wasteBatchId}`
    : `/api/upload-image`;
  return api.post(url, formData, { headers: { "Content-Type": "multipart/form-data" } });
};

export const getMyAnalyses = (params) =>
  api.get("/api/my-analyses", { params });
  // params: { search, page, page_size, sort_order }

export const getFullAnalysis = (imageId) =>
  api.get(`/api/analysis/${imageId}/full`);

export const deleteAnalysisById = (imageId) =>
  api.delete(`/api/analysis/${imageId}`);

export const getDashboardSummary = () =>
  api.get("/api/dashboard/summary");

// --- Analytics Dashboards (Milestone 4) ---
export const getRecyclerDashboard = (params) =>
  api.get("/api/analytics/recycler", { params });
  // params: { start_date, end_date, material_type, waste_category }

export const getSustainabilityAnalytics = (params) =>
  api.get("/api/analytics/sustainability", { params });
  // params: { start_date, end_date }

export const getManufacturerDashboard = (params) =>
  api.get("/api/analytics/manufacturer", { params });

export const getAdminDashboard = () =>
  api.get("/api/analytics/admin");

// --- Notifications (Milestone 4) ---
export const getNotifications = (params) =>
  api.get("/api/notifications", { params });
  // params: { unread_only, limit }

export const markNotificationRead = (id) =>
  api.patch(`/api/notifications/${id}/read`);

export const markAllNotificationsRead = () =>
  api.patch("/api/notifications/read-all");

// --- Reports & Export (Milestone 4) ---
export const generateReport = (reportType, format, params = {}) => {
  const query = new URLSearchParams({ report_type: reportType, format, ...params }).toString();
  return api.get(`/api/reports/generate?${query}`, { responseType: "blob" });
};

export const getReportHistory = (params) =>
  api.get("/api/reports/history", { params });

export const downloadPastReport = (id) =>
  api.get(`/api/reports/history/${id}/download`, { responseType: "blob" });


// --- Admin User Management ---
export const getAllUsers = () =>
  api.get("/api/admin/users");

export const updateUserRole = (userId, role) =>
  api.put(`/api/admin/users/${userId}/role`, { role });

export const deleteUserAccount = (userId) =>
  api.delete(`/api/admin/users/${userId}`);