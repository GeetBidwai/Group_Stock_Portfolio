import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { telegramAuthApi } from "../services/telegramAuthApi";
import { loadPendingMobileReset, savePendingMobileReset } from "../utils/sessionStorage";

export default function VerifyOTPPage() {
  const navigate = useNavigate();
  const pending = loadPendingMobileReset();
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");

  if (!pending?.phone_number) {
    return <Navigate to="/auth/mobile-login" replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      setError("");
      const data = await telegramAuthApi.verifyMobileOtp({
        phone_number: pending.phone_number,
        otp,
      });
      savePendingMobileReset({
        ...pending,
        telegram_id: data.telegram_id,
        otp_verified: Boolean(data.otp_verified),
      });
      navigate("/auth/reset-mpin", { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(460px, 100%)" }}>
        <h1>Verify Telegram OTP</h1>
        <p className="muted">Verify the OTP sent to your Telegram account to continue with MPIN reset.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input
            inputMode="numeric"
            maxLength={6}
            placeholder="6-digit OTP"
            value={otp}
            onChange={(event) => setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))}
          />
          {error ? <p>{error}</p> : null}
          <button className="btn" type="submit">Verify OTP</button>
        </form>
      </div>
    </div>
  );
}
