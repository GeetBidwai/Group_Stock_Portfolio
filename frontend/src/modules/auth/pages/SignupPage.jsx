import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { authApi } from "../services/authApi";

export function SignupPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    mobile_number: "",
  });
  const [linkSession, setLinkSession] = useState(null);
  const [linkStatus, setLinkStatus] = useState(null);
  const [linkLoading, setLinkLoading] = useState(false);
  const [error, setError] = useState("");
  const [linkError, setLinkError] = useState("");

  const isLinked = linkStatus?.linked;
  const isExpired = linkStatus?.expired;
  const canShowForm = Boolean(linkSession && isLinked && !isExpired);

  useEffect(() => {
    if (!linkSession?.session_token || canShowForm || isExpired) {
      return undefined;
    }

    const intervalId = window.setInterval(async () => {
      try {
        const status = await authApi.getTelegramLinkStatus(linkSession.session_token);
        setLinkStatus(status);
      } catch (err) {
        setLinkError(err.message);
        window.clearInterval(intervalId);
      }
    }, 3000);

    return () => window.clearInterval(intervalId);
  }, [linkSession?.session_token, canShowForm, isExpired]);

  const statusMessage = useMemo(() => {
    if (!linkSession) {
      return "Start by generating a Telegram QR code. We will link your bot chat before creating the account.";
    }
    if (linkError) {
      return linkError;
    }
    if (isExpired) {
      return "This Telegram link expired. Generate a fresh QR code to continue.";
    }
    if (isLinked) {
      return `Telegram linked${linkStatus?.telegram_username ? ` as @${linkStatus.telegram_username}` : ""}. Complete your account details below.`;
    }
    return "Open Telegram, tap Start on the bot, and this page will unlock automatically.";
  }, [isExpired, isLinked, linkError, linkSession, linkStatus?.telegram_username]);

  async function handleGenerateQr() {
    try {
      setLinkLoading(true);
      setLinkError("");
      setError("");
      const data = await authApi.createTelegramLinkSession();
      setLinkSession(data);
      const status = await authApi.getTelegramLinkStatus(data.session_token);
      setLinkStatus(status);
    } catch (err) {
      setLinkError(err.message);
    } finally {
      setLinkLoading(false);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      setError("");
      await authApi.completeTelegramSignup({
        session_token: linkSession.session_token,
        ...form,
      });
      await login({ username: form.username, password: form.password });
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(540px, 100%)" }}>
        <h1>Signup</h1>
        <p className="muted">Link your Telegram bot chat first, then finish the rest of your account details.</p>
        <div className="panel" style={{ marginBottom: 24, padding: 24 }}>
          <h2 style={{ marginBottom: 12 }}>Step 1: Verify Telegram</h2>
          <p className="muted" style={{ marginBottom: 16 }}>{statusMessage}</p>
          {!linkSession || isExpired ? (
            <button className="btn" type="button" onClick={handleGenerateQr} disabled={linkLoading}>
              {linkLoading ? "Generating..." : "Generate QR Code"}
            </button>
          ) : null}
          {linkSession && !isExpired ? (
            <div className="grid" style={{ gap: 16, justifyItems: "center" }}>
              <img
                src={linkSession.qr_code_url}
                alt="Telegram signup QR code"
                style={{ width: 220, height: 220, borderRadius: 16, background: "#fff", padding: 12 }}
              />
              <a className="btn" href={linkSession.deep_link} target="_blank" rel="noreferrer">
                Open Telegram
              </a>
            </div>
          ) : null}
          {linkError && <p>{linkError}</p>}
        </div>
        <form className="form" onSubmit={handleSubmit}>
          <h2 style={{ marginBottom: 12 }}>Step 2: Account Details</h2>
          {["username", "email", "password", "first_name", "last_name", "mobile_number"].map((field) => (
            <input
              key={field}
              type={field === "password" ? "password" : "text"}
              inputMode={field === "mobile_number" ? "tel" : undefined}
              placeholder={field.replaceAll("_", " ")}
              value={form[field]}
              disabled={!canShowForm}
              onChange={(e) => setForm({ ...form, [field]: e.target.value })}
            />
          ))}
          {error && <p>{error}</p>}
          <button className="btn" type="submit" disabled={!canShowForm}>Create account</button>
        </form>
        <p><Link to="/login">Back to login</Link></p>
      </div>
    </div>
  );
}
