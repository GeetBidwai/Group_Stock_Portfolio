import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { authApi } from "../services/authApi";

export function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [mobileNumber, setMobileNumber] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      setError("");
      setMessage("");
      const data = await authApi.requestResetOtp({ mobile_number: mobileNumber });
      sessionStorage.setItem("resetMobileNumber", data.mobile_number || mobileNumber);
      setMessage(data.message || "OTP sent successfully.");
      navigate("/verify-otp");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(460px, 100%)" }}>
        <h1>Forgot Password</h1>
        <p className="muted">Enter your linked mobile number. Your OTP will be sent to your Telegram app.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input
            inputMode="tel"
            placeholder="Linked mobile number"
            value={mobileNumber}
            onChange={(e) => setMobileNumber(e.target.value)}
          />
          {message && <p>{message}</p>}
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Send Telegram OTP</button>
        </form>
      </div>
    </div>
  );
}
