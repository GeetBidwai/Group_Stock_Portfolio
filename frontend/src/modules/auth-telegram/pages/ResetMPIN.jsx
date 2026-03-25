import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../../auth/hooks/useAuth";
import { apiClient } from "../../../services/apiClient";
import { telegramAuthApi } from "../services/telegramAuthApi";
import { clearPendingMobileReset, loadPendingMobileReset } from "../utils/sessionStorage";

export default function ResetMPINPage() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const pending = loadPendingMobileReset();
  const [newMpin, setNewMpin] = useState("");
  const [confirmMpin, setConfirmMpin] = useState("");
  const [error, setError] = useState("");

  if (!pending?.telegram_id || !pending?.otp_verified) {
    return <Navigate to="/auth/mobile-login" replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (newMpin !== confirmMpin) {
      setError("MPIN values do not match.");
      return;
    }

    try {
      setError("");
      await telegramAuthApi.resetMpin({
        telegram_id: pending.telegram_id,
        new_mpin: newMpin,
      });
      const loginData = await telegramAuthApi.loginMpin({
        telegram_id: pending.telegram_id,
        mpin: newMpin,
      });
      apiClient.saveTokens(loginData);
      setUser(loginData.user);
      clearPendingMobileReset();
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(460px, 100%)" }}>
        <h1>Reset MPIN</h1>
        <p className="muted">Set a new 4-digit MPIN. You will be signed in after a successful reset.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input
            inputMode="numeric"
            maxLength={4}
            placeholder="New 4-digit MPIN"
            value={newMpin}
            onChange={(event) => setNewMpin(event.target.value.replace(/\D/g, "").slice(0, 4))}
          />
          <input
            inputMode="numeric"
            maxLength={4}
            placeholder="Confirm MPIN"
            value={confirmMpin}
            onChange={(event) => setConfirmMpin(event.target.value.replace(/\D/g, "").slice(0, 4))}
          />
          {error ? <p>{error}</p> : null}
          <button className="btn" type="submit">Reset MPIN</button>
        </form>
      </div>
    </div>
  );
}
