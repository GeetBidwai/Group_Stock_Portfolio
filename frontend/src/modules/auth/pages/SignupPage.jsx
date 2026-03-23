import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export function SignupPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    telegram_chat_id: "",
    telegram_username: "",
  });
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      await register(form);
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(540px, 100%)" }}>
        <h1>Signup</h1>
        <form className="form" onSubmit={handleSubmit}>
          {["username", "email", "password", "first_name", "last_name", "telegram_chat_id", "telegram_username"].map((field) => (
            <input
              key={field}
              type={field === "password" ? "password" : "text"}
              placeholder={field.replaceAll("_", " ")}
              value={form[field]}
              onChange={(e) => setForm({ ...form, [field]: e.target.value })}
            />
          ))}
          {error && <p>{error}</p>}
          <button className="btn" type="submit">Create account</button>
        </form>
        <p><Link to="/login">Back to login</Link></p>
      </div>
    </div>
  );
}
