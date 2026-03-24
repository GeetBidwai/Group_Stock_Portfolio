import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

function getTokens() {
  return {
    access: localStorage.getItem("accessToken"),
    refresh: localStorage.getItem("refreshToken"),
  };
}

function saveTokens(tokens) {
  if (tokens?.access) {
    localStorage.setItem("accessToken", tokens.access);
  }
  if (tokens?.refresh) {
    localStorage.setItem("refreshToken", tokens.refresh);
  }
}

function clearTokens() {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
}

export const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

axiosClient.interceptors.request.use((config) => {
  const tokens = getTokens();
  if (tokens.access) {
    config.headers.Authorization = `Bearer ${tokens.access}`;
  }
  return config;
});

axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const tokens = getTokens();

    if (error.response?.status === 401 && !originalRequest?._retry && tokens.refresh) {
      originalRequest._retry = true;
      try {
        const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, { refresh: tokens.refresh });
        saveTokens({ access: refreshResponse.data.access, refresh: refreshResponse.data.refresh || tokens.refresh });
        originalRequest.headers.Authorization = `Bearer ${refreshResponse.data.access}`;
        return axiosClient(originalRequest);
      } catch (refreshError) {
        clearTokens();
        throw refreshError;
      }
    }

    throw error;
  },
);
