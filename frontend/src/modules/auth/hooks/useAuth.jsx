import { createContext, useContext, useEffect, useState } from "react";

import { authApi } from "../services/authApi";
import { apiClient } from "../../../services/apiClient";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const tokens = apiClient.getTokens();
    if (!tokens.access) {
      setLoading(false);
      return;
    }
    authApi.me().then(setUser).catch(() => authApi.clearTokens()).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    function handleAuthExpired() {
      authApi.clearTokens();
      setUser(null);
    }

    if (typeof window !== "undefined") {
      window.addEventListener(apiClient.AUTH_EXPIRED_EVENT, handleAuthExpired);
      return () => window.removeEventListener(apiClient.AUTH_EXPIRED_EVENT, handleAuthExpired);
    }

    return undefined;
  }, []);

  async function login(credentials) {
    const data = await authApi.login(credentials);
    apiClient.saveTokens(data);
    setUser(data.user);
    return data;
  }

  async function register(payload) {
    await authApi.register(payload);
    return login({ username: payload.username, password: payload.password });
  }

  async function logout() {
    const refresh = apiClient.getTokens().refresh;
    try {
      if (refresh) {
        await authApi.logout(refresh);
      }
    } finally {
      authApi.clearTokens();
      setUser(null);
    }
  }

  return <AuthContext.Provider value={{ user, loading, login, register, logout, setUser }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
