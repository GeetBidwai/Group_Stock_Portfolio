import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { authApi } from "../services/authApi";

export function ResetPasswordPage() {
  const navigate = useNavigate();
  const resetToken = sessionStorage.getItem("passwordResetToken") || "";
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    try {
      setError("");
      await authApi.resetPasswordWithToken({ token: resetToken, new_password: password });
      sessionStorage.removeItem("resetMobileNumber");
      sessionStorage.removeItem("passwordResetToken");
      navigate("/login");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(460px, 100%)" }}>
        <h1>Reset Password</h1>
        <p className="muted">Set a new password to finish recovering your account.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input type="password" placeholder="New password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <input type="password" placeholder="Confirm new password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Reset password</button>
        </form>
        <p><Link to="/login">Return to login</Link></p>
      </div>
    </div>
  );
}
