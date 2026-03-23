import { AuthProvider } from "../modules/auth/hooks/useAuth";

export function AppProviders({ children }) {
  return <AuthProvider>{children}</AuthProvider>;
}
