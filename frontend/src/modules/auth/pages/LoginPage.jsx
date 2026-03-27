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
      <div className="auth-copy">
        <p className="auth-kicker">Welcome Back</p>
        <h1>Login</h1>
        <p className="muted">Access the protected analytics workspace and continue from where you left off.</p>
      </div>
      <form className="form auth-form" onSubmit={handleSubmit}>
        <label className="field">
          <span className="field__label">Username</span>
          <input placeholder="Enter your username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        </label>
        <label className="field">
          <span className="field__label">Password</span>
          <input type="password" placeholder="Enter your password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </label>
        {error ? <p className="form-error">{error}</p> : null}
        <button className="btn" type="submit">Enter Workspace</button>
      </form>
      <p className="auth-footer-link"><Link to="/signup">Create account</Link></p>
    </AuthShell>
  );
}
