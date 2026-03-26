import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { AuthShell } from "../../../components/AuthShell";
import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      await login(form);
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <AuthShell panelClassName="auth-panel--compact" assistantPage="login">
        <h1>Login</h1>
        <p className="muted">Access the protected analytics workspace.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Login</button>
        </form>
        <p><Link to="/signup">Create account</Link> | <Link to="/forgot-password">Forgot password</Link></p>
    </AuthShell>
  );
}
