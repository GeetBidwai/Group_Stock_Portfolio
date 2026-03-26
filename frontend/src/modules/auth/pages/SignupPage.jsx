import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { AuthShell } from "../../../components/AuthShell";
import { useAuth } from "../hooks/useAuth";

const CHAT_ID_STEPS = [
  "Open Telegram.",
  "Search for @userinfobot.",
  "Open the bot and click Start.",
  "Copy the Chat ID shown by the bot.",
];

export function SignupPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [showChatHelp, setShowChatHelp] = useState(false);
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    mobile_number: "",
    telegram_chat_id: "",
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
        <p className="muted">Create your account with your phone number and Telegram Chat ID so OTP recovery works end to end.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          <input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <input placeholder="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
          <input placeholder="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
          <input inputMode="tel" placeholder="Phone number" value={form.mobile_number} onChange={(e) => setForm({ ...form, mobile_number: e.target.value })} />
          <input
            inputMode="numeric"
            placeholder="Telegram Chat ID"
            value={form.telegram_chat_id}
            onChange={(e) => setForm({ ...form, telegram_chat_id: e.target.value })}
          />
          <button
            className="btn"
            type="button"
            onClick={() => setShowChatHelp((value) => !value)}
            style={{ background: "transparent", color: "var(--text)", border: "1px solid var(--border)" }}
          >
            {showChatHelp ? "Hide Chat ID Help" : "Get Chat ID"}
          </button>
          {showChatHelp ? (
            <div className="panel" style={{ padding: 18, background: "rgba(255,255,255,0.65)" }}>
              <h2 style={{ marginTop: 0, marginBottom: 10, fontSize: 20 }}>How to get your Telegram Chat ID</h2>
              <ol style={{ margin: 0, paddingLeft: 20, color: "var(--muted)" }}>
                {CHAT_ID_STEPS.map((step) => (
                  <li key={step} style={{ marginBottom: 6 }}>{step}</li>
                ))}
              </ol>
            </div>
          ) : null}
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Create account</button>
        </form>
        <p><Link to="/login">Back to login</Link></p>
    </AuthShell>
  );
}
