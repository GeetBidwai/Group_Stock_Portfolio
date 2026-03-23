import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { authApi } from "../services/authApi";

export function OTPVerificationPage() {
  const navigate = useNavigate();
  const identifier = sessionStorage.getItem("resetIdentifier") || "";
  const otpRequired = sessionStorage.getItem("otpRequired");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (otpRequired === "false") {
      navigate("/reset-password");
    }
  }, [navigate, otpRequired]);

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      await authApi.verifyOtp({ identifier, otp });
      navigate("/reset-password");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(460px, 100%)" }}>
        <h1>Verify Telegram OTP</h1>
        <form className="form" onSubmit={handleSubmit}>
          <input placeholder="6-digit OTP" value={otp} onChange={(e) => setOtp(e.target.value)} />
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Verify OTP</button>
        </form>
      </div>
    </div>
  );
}
