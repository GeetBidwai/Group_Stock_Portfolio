import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { authApi } from "../services/authApi";

export function OTPVerificationPage() {
  const navigate = useNavigate();
  const mobileNumber = sessionStorage.getItem("resetMobileNumber") || "";
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!mobileNumber) {
      navigate("/forgot-password");
    }
  }, [mobileNumber, navigate]);

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      setError("");
      const data = await authApi.verifyResetOtp({ mobile_number: mobileNumber, otp });
      sessionStorage.setItem("passwordResetToken", data.token);
      navigate("/reset-password");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(460px, 100%)" }}>
        <h1>Verify Telegram OTP</h1>
        <p className="muted">Enter the OTP sent to your Telegram app.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input placeholder="6-digit OTP" value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))} />
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Verify OTP</button>
        </form>
      </div>
    </div>
  );
}
