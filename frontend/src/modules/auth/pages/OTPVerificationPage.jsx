import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { AuthShell } from "../../../components/AuthShell";
import { authApi } from "../services/authApi";

export function OTPVerificationPage() {
  const navigate = useNavigate();
  const phoneNumber = sessionStorage.getItem("resetPhoneNumber") || "";
  const debugOtpPreview = sessionStorage.getItem("debugOtpPreview") || "";
  const [otpCode, setOtpCode] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!phoneNumber) {
      navigate("/forgot-password");
    }
  }, [phoneNumber, navigate]);

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      setError("");
      const data = await authApi.verifyOtp({ phone_number: phoneNumber, otp_code: otpCode });
      sessionStorage.setItem("passwordResetToken", data.token);
      navigate("/reset-password");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <AuthShell panelClassName="auth-panel--compact" assistantPage="otpVerification">
        <h1>OTP Verification</h1>
        <p className="muted">Enter the OTP sent to your Telegram app.</p>
        {debugOtpPreview ? <p>Development OTP: <strong>{debugOtpPreview}</strong></p> : null}
        <form className="form" onSubmit={handleSubmit}>
          <input placeholder="Enter OTP" value={otpCode} onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, "").slice(0, 6))} />
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Verify OTP</button>
        </form>
    </AuthShell>
  );
}
