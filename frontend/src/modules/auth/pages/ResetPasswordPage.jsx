import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { authApi } from "../services/authApi";

export function ResetPasswordPage() {
  const navigate = useNavigate();
  const identifier = sessionStorage.getItem("resetIdentifier") || "";
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      await authApi.resetPassword({ identifier, password });
      sessionStorage.removeItem("resetIdentifier");
      navigate("/login");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(460px, 100%)" }}>
        <h1>Reset Password</h1>
        <form className="form" onSubmit={handleSubmit}>
          <input type="password" placeholder="New password" value={password} onChange={(e) => setPassword(e.target.value)} />
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Reset password</button>
        </form>
        <p><Link to="/login">Return to login</Link></p>
      </div>
    </div>
  );
}
