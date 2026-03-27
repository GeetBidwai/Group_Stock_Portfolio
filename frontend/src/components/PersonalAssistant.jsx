import { useEffect, useRef, useState } from "react";

import { apiClient } from "../services/apiClient";
import { useAuth } from "../modules/auth/hooks/useAuth";

export function PersonalAssistant() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesRef = useRef(null);
  const [messages, setMessages] = useState(() => [
    {
      id: "assistant-welcome",
      role: "assistant",
      content: `Hi ${user?.username || "there"}! I am your Market Atlas assistant. Ask me about your portfolio, risk, forecasts, or even a simple question to get started.`,
    },
  ]);
  const quickPrompts = [
    "What is in my portfolio?",
    "What is my risk breakdown?",
    "Compare my top two stocks",
  ];
  const showQuickPrompts = messages.length <= 1 && !isLoading;

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  async function sendMessage(rawText) {
    const trimmed = rawText.trim();
    if (!trimmed || isLoading) {
      return;
    }

    const nextUserMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmed,
    };
    const nextMessages = [...messages, nextUserMessage];
    setMessages(nextMessages);
    setInput("");
    setIsOpen(true);
    setIsLoading(true);

    try {
      const history = nextMessages
        .slice(-8)
        .map((message) => ({ role: message.role, content: message.content }));
      const data = await apiClient.post("/assistant/chat/", {
        message: trimmed,
        history,
      });
      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: data.reply || "I could not answer that right now.",
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: `assistant-error-${Date.now()}`,
          role: "assistant",
          content: error.message || "I could not reach the assistant right now.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className={`personal-assistant ${isOpen ? "is-open" : ""}`}>
      <button
        type="button"
        className="personal-assistant__launcher"
        onClick={() => setIsOpen((current) => !current)}
        aria-expanded={isOpen}
        aria-label="Toggle personal assistant"
      >
        <span className="personal-assistant__launcher-mark">AI</span>
        <span className="personal-assistant__launcher-text">Assistant</span>
      </button>

      {isOpen ? (
        <section className="personal-assistant__panel" aria-label="Personal assistant">
          <div className="personal-assistant__header">
            <div>
              <strong>Personal Assistant</strong>
              <p className="muted">Friendly help using your current app data.</p>
            </div>
            <button
              type="button"
              className="personal-assistant__close"
              onClick={() => setIsOpen(false)}
              aria-label="Close personal assistant"
            >
              x
            </button>
          </div>

          <div ref={messagesRef} className="personal-assistant__messages">
            {messages.map((message) => (
              <div key={message.id} className={`personal-assistant__message personal-assistant__message--${message.role}`}>
                {message.content.split("\n").map((line, index) => (
                  <p key={`${message.id}-${index}`}>{line}</p>
                ))}
              </div>
            ))}
            {isLoading ? <div className="personal-assistant__typing">Thinking...</div> : null}
          </div>

          {showQuickPrompts ? (
            <div className="personal-assistant__suggestions">
              {quickPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  className="personal-assistant__chip"
                  onClick={() => sendMessage(prompt)}
                  disabled={isLoading}
                >
                  {prompt}
                </button>
              ))}
            </div>
          ) : null}

          <form
            className="personal-assistant__form"
            onSubmit={(event) => {
              event.preventDefault();
              sendMessage(input);
            }}
          >
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about your portfolio or stock ideas"
              aria-label="Ask your personal assistant"
            />
            <button type="submit" className="btn" disabled={isLoading}>
              Send
            </button>
          </form>
        </section>
      ) : null}
    </div>
  );
}
