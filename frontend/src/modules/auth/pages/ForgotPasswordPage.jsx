import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { authApi } from "../services/authApi";

export function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      const data = await authApi.requestOtp({ identifier });
      sessionStorage.setItem("resetIdentifier", identifier);
      sessionStorage.setItem("otpRequired", String(data.otp_required !== false));
      setMessage(data.message || "Password reset request created.");
      navigate(data.otp_required === false ? "/reset-password" : "/verify-otp");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(460px, 100%)" }}>
        <h1>Forgot Password</h1>
        <form className="form" onSubmit={handleSubmit}>
          <input placeholder="Username, email, or Telegram username" value={identifier} onChange={(e) => setIdentifier(e.target.value)} />
          {message && <p>{message}</p>}
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Send Telegram OTP</button>
        </form>
      </div>
    </div>
  );
}
