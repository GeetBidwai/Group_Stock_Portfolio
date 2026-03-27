import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { AuthShell } from "../../../components/AuthShell";
import { useAuth } from "../hooks/useAuth";

export function SignupPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    mobile_number: "",
  });
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      setError("");
      await register(form);
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <AuthShell assistantPage="signup">
      <div className="auth-copy">
        <p className="auth-kicker">Create Account</p>
        <h1>Sign Up</h1>
        <p className="muted">Create your account to unlock the full analytics workspace and assistant experience.</p>
      </div>
      <form className="form auth-form" onSubmit={handleSubmit}>
        <div className="auth-grid">
          <label className="field">
            <span className="field__label">Username</span>
            <input placeholder="Choose a username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          </label>
          <label className="field">
            <span className="field__label">Email</span>
            <input type="email" placeholder="you@example.com" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </label>
          <label className="field">
            <span className="field__label">Password</span>
            <input type="password" placeholder="Create a password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </label>
          <label className="field">
            <span className="field__label">Phone number</span>
            <input inputMode="tel" placeholder="Optional" value={form.mobile_number} onChange={(e) => setForm({ ...form, mobile_number: e.target.value })} />
          </label>
          <label className="field">
            <span className="field__label">First name</span>
            <input placeholder="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
          </label>
          <label className="field">
            <span className="field__label">Last name</span>
            <input placeholder="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
          </label>
        </div>
        {error ? <p className="form-error">{error}</p> : null}
        <button className="btn" type="submit">Create account</button>
      </form>
      <p className="auth-footer-link"><Link to="/login">Back to login</Link></p>
    </AuthShell>
  );
}
