const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api";

function normalizeApiBaseUrl(rawValue) {
  const candidate = (rawValue || DEFAULT_API_BASE_URL).trim().replace(/\/+$/, "");
  return /\/api$/i.test(candidate) ? candidate : `${candidate}/api`;
}

export const API_BASE_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL);
