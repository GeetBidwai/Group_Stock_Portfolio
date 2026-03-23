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

export function clearTokens() {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
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
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || errorBody.error || errorBody.non_field_errors?.[0] || "Request failed");
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
};
