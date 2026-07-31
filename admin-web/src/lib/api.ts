import axios from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://coreops-platform.onrender.com/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("admin_access_token");
    if (token && token.trim() !== "") {
      config.headers.Authorization = `Bearer ${token.trim()}`;
    }
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      const currentPath = window.location.pathname;
      const isPublic = currentPath === "/login" || currentPath === "/";
      if (!isPublic) {
        localStorage.removeItem("admin_access_token");
        localStorage.removeItem("admin_user");
        localStorage.removeItem("admin_refresh_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);
