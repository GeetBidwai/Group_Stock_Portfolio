import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { telegramAuthApi } from "../services/telegramAuthApi";
import { savePendingMobileReset } from "../utils/sessionStorage";

export default function MobileLoginPage() {
  const navigate = useNavigate();
  const [phoneNumber, setPhoneNumber] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      setError("");
      const data = await telegramAuthApi.requestMobileOtp({ phone_number: phoneNumber });
      savePendingMobileReset({ phone_number: data.phone_number });
      setMessage(data.message || "OTP sent successfully.");
      navigate("/auth/verify-otp", { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(460px, 100%)" }}>
        <h1>Mobile Login</h1>
        <p className="muted">Enter your linked mobile number to receive a Telegram OTP before resetting your MPIN.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input
            inputMode="tel"
            placeholder="Mobile number"
            value={phoneNumber}
            onChange={(event) => setPhoneNumber(event.target.value)}
          />
          {message ? <p>{message}</p> : null}
          {error ? <p>{error}</p> : null}
          <button className="btn" type="submit">Send Telegram OTP</button>
        </form>
      </div>
    </div>
  );
}
