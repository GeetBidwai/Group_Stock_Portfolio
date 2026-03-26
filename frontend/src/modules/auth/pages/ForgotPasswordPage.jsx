import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { AuthShell } from "../../../components/AuthShell";
import { authApi } from "../services/authApi";

const CHAT_ID_STEPS = [
  "Open Telegram.",
  "Search for @userinfobot.",
  "Open the bot.",
  "Click Start and copy your Chat ID.",
];

export function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ phone_number: "", telegram_chat_id: "" });
  const [showHelp, setShowHelp] = useState(false);
  const [message, setMessage] = useState("");
  const [otpPreview, setOtpPreview] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      setError("");
      setMessage("");
      setOtpPreview("");
      const data = await authApi.requestOtp(form);
      sessionStorage.setItem("resetPhoneNumber", data.phone_number || form.phone_number);
      sessionStorage.setItem("resetTelegramChatId", String(data.telegram_chat_id || form.telegram_chat_id));
      setMessage(data.message || "OTP sent successfully.");
      if (data.otp_preview) {
        setOtpPreview(data.otp_preview);
        sessionStorage.setItem("debugOtpPreview", data.otp_preview);
      } else {
        sessionStorage.removeItem("debugOtpPreview");
      }
      navigate("/verify-otp");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <AuthShell assistantPage="forgotPassword">
        <h1>Forgot Password</h1>
        <p className="muted">Enter the phone number and Telegram Chat ID linked to your account. We will send the OTP to your Telegram bot chat.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input
            inputMode="tel"
            placeholder="Phone number"
            value={form.phone_number}
            onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
          />
          <input
            inputMode="numeric"
            placeholder="Telegram Chat ID"
            value={form.telegram_chat_id}
            onChange={(e) => setForm({ ...form, telegram_chat_id: e.target.value })}
          />
          <button
            className="btn"
            type="button"
            onClick={() => setShowHelp((value) => !value)}
            style={{ background: "transparent", color: "var(--text)", border: "1px solid var(--border)" }}
          >
            {showHelp ? "Hide Chat ID Help" : "Get Chat ID"}
          </button>
          {showHelp ? (
            <div className="panel" style={{ padding: 18, background: "rgba(255,255,255,0.65)" }}>
              <h2 style={{ marginTop: 0, marginBottom: 10, fontSize: 20 }}>How to get your Telegram Chat ID</h2>
              <ol style={{ margin: 0, paddingLeft: 20, color: "var(--muted)" }}>
                {CHAT_ID_STEPS.map((step) => (
                  <li key={step} style={{ marginBottom: 6 }}>{step}</li>
                ))}
              </ol>
            </div>
          ) : null}
          {otpPreview ? <p>Development OTP: <strong>{otpPreview}</strong></p> : null}
          {message && <p>{message}</p>}
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Get OTP</button>
        </form>
    </AuthShell>
  );
}
