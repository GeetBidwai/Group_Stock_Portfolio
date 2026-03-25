import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../../auth/hooks/useAuth";
import { apiClient } from "../../../services/apiClient";
import { telegramAuthApi } from "../services/telegramAuthApi";
import { clearPendingTelegramAuth, loadPendingTelegramAuth } from "../utils/sessionStorage";

export default function LoginMPINPage() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const pending = loadPendingTelegramAuth();
  const [mpin, setMpin] = useState("");
  const [error, setError] = useState("");

  if (!pending?.telegram_id) {
    return <Navigate to="/auth/telegram-login" replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      setError("");
      const data = await telegramAuthApi.loginMpin({
        telegram_id: pending.telegram_id,
        mpin,
      });
      apiClient.saveTokens(data);
      setUser(data.user);
      clearPendingTelegramAuth();
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(460px, 100%)" }}>
        <h1>Login with MPIN</h1>
        <p className="muted">Enter your 4-digit MPIN to continue.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input
            inputMode="numeric"
            maxLength={4}
            placeholder="4-digit MPIN"
            value={mpin}
            onChange={(event) => setMpin(event.target.value.replace(/\D/g, "").slice(0, 4))}
          />
          {error ? <p>{error}</p> : null}
          <button className="btn" type="submit">Login</button>
        </form>
      </div>
    </div>
  );
}
