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
        <h1>Sign Up</h1>
        <p className="muted">Create your account to access the analytics workspace.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          <input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <input placeholder="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
          <input placeholder="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
          <input inputMode="tel" placeholder="Phone number (optional)" value={form.mobile_number} onChange={(e) => setForm({ ...form, mobile_number: e.target.value })} />
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Create account</button>
        </form>
        <p><Link to="/login">Back to login</Link></p>
    </AuthShell>
  );
}
