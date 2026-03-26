import { API_BASE_URL } from "./apiBaseUrl";

const AUTH_EXPIRED_EVENT = "auth:expired";

function notifyAuthExpired() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
  }
}

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

export function clearTokens() {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
}

function extractErrorMessage(errorBody) {
  if (Array.isArray(errorBody) && errorBody.length) {
    return String(errorBody[0]);
  }
  if (typeof errorBody === "string" && errorBody.trim()) {
    return errorBody;
  }
  if (errorBody?.detail) {
    return Array.isArray(errorBody.detail) ? String(errorBody.detail[0]) : errorBody.detail;
  }
  if (errorBody?.error) {
    return errorBody.error;
  }
  if (Array.isArray(errorBody?.non_field_errors) && errorBody.non_field_errors.length) {
    return String(errorBody.non_field_errors[0]);
  }
  if (errorBody && typeof errorBody === "object") {
    for (const value of Object.values(errorBody)) {
      if (Array.isArray(value) && value.length) {
        return String(value[0]);
      }
      if (typeof value === "string" && value.trim()) {
        return value;
      }
    }
  }
  return "Request failed";
}

async function request(path, options = {}, retry = true) {
  const tokens = getTokens();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(tokens.access ? { Authorization: `Bearer ${tokens.access}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (response.status === 401 && retry && tokens.refresh) {
    const refreshed = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: tokens.refresh }),
    });
    if (refreshed.ok) {
      const data = await refreshed.json();
      saveTokens({ access: data.access, refresh: data.refresh || tokens.refresh });
      return request(path, options, false);
    }
    clearTokens();
    notifyAuthExpired();
  } else if (response.status === 401 && !tokens.refresh) {
    clearTokens();
    notifyAuthExpired();
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    if (response.status === 401) {
      clearTokens();
      notifyAuthExpired();
    }
    throw new Error(extractErrorMessage(errorBody));
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const apiClient = {
  get: (path) => request(path),
  post: (path, body) =>
    request(path, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  patch: (path, body) =>
    request(path, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  delete: (path) =>
    request(path, {
      method: "DELETE",
    }),
  saveTokens,
  getTokens,
  AUTH_EXPIRED_EVENT,
};
