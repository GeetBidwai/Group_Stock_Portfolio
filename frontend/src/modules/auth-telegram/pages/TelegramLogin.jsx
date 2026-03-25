import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { telegramAuthApi } from "../services/telegramAuthApi";
import { savePendingTelegramAuth } from "../utils/sessionStorage";

const WIDGET_ID = "telegram-login-widget";

export default function TelegramLoginPage() {
  const navigate = useNavigate();
  const widgetContainerRef = useRef(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const botUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME;
    if (!botUsername || !widgetContainerRef.current) {
      return undefined;
    }

    window.onTelegramAuth = async (user) => {
      try {
        setError("");
        const payload = await telegramAuthApi.verifyTelegram(user);
        savePendingTelegramAuth({
          telegram_id: payload.telegram_id,
          username: payload.username,
        });
        navigate(payload.new_user ? "/auth/set-mpin" : "/auth/login-mpin", { replace: true });
      } catch (err) {
        setError(err.message);
      }
    };

    const existingScript = document.getElementById(WIDGET_ID);
    if (existingScript) {
      existingScript.remove();
    }

    const script = document.createElement("script");
    script.id = WIDGET_ID;
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.async = true;
    script.setAttribute("data-telegram-login", botUsername);
    script.setAttribute("data-size", "large");
    script.setAttribute("data-radius", "12");
    script.setAttribute("data-userpic", "false");
    script.setAttribute("data-request-access", "write");
    script.setAttribute("data-onauth", "onTelegramAuth(user)");
    widgetContainerRef.current.innerHTML = "";
    widgetContainerRef.current.appendChild(script);

    return () => {
      delete window.onTelegramAuth;
    };
  }, [navigate]);

  const botUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME;

  return (
    <div className="page-shell grid" style={{ placeItems: "center" }}>
      <div className="panel" style={{ width: "min(460px, 100%)" }}>
        <h1>Telegram Login</h1>
        <p className="muted">Authenticate with Telegram to continue into the analytics workspace.</p>
        {!botUsername ? <p>Telegram bot username is not configured.</p> : null}
        <div ref={widgetContainerRef} style={{ minHeight: 56, marginTop: 20 }} />
        {error ? <p>{error}</p> : null}
      </div>
    </div>
  );
}
