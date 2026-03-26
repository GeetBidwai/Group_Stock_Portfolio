import { useMemo, useState } from "react";

const PAGE_HINTS = {
  login: ["What should I enter here?", "I can't login", "Signup is not working"],
  signup: ["What should I enter here?", "Signup is not working", "Do I need a phone number?"],
};

const PAGE_WELCOME = {
  login: "I can help with login and common sign-in issues.",
  signup: "I can guide you through each signup field.",
};

function buildSteps(title, steps, closing = "Tell me which step is failing if you want more help.") {
  return `${title}\n\n${steps.map((step, index) => `${index + 1}. ${step}`).join("\n")}\n\n${closing}`;
}

function answerForMessage(message, page) {
  const text = message.trim().toLowerCase();

  if (!text) {
    return "Tell me what you need help with, and I'll guide you step by step.";
  }

  if (text === "hi" || text === "hello" || text === "hey" || text === "hii") {
    return `${text.charAt(0).toUpperCase() + text.slice(1)}!\n\n${PAGE_WELCOME[page] || "I can help you complete the authentication steps on this page."}\n\nTell me which step you are on.`;
  }

  if (text.includes("password") && text.includes("match")) {
    return buildSteps(
      "Both password fields must be exactly the same.",
      [
        "Enter your new password once.",
        "Enter the same password again in confirm password.",
        "Check for extra spaces or different characters.",
      ]
    );
  }

  if (text.includes("sign up") || text.includes("signup") || text.includes("register") || (page === "signup" && text.includes("not working"))) {
    return buildSteps(
      "For signup, please fill in all required details carefully.",
      [
        "Enter your username and email.",
        "Set your password.",
        "Enter your first name and last name.",
        "Phone number is optional.",
      ],
      "If one field is failing, tell me which one."
    );
  }

  if (text.includes("login") || text.includes("sign in") || (page === "login" && text.includes("not working"))) {
    return buildSteps(
      "For login, use your username and password.",
      [
        "Enter your username exactly as you created it.",
        "Enter your password carefully.",
        "If you still cannot sign in, verify that your account exists.",
      ]
    );
  }

  if (text.includes("what should i enter") || text.includes("what to enter") || text.includes("what should i do here")) {
    if (page === "login") {
      return "On this page, enter your username and password.";
    }
    if (page === "signup") {
      return "On this page, enter username, email, password, first name, last name, and optionally a phone number.";
    }
  }

  if (text.includes("not working") || text.includes("failed") || text.includes("error")) {
    return "Tell me exactly which step failed: login or signup. I'll guide you from there.";
  }

  return "I can help with login and signup. Tell me which step you are on.";
}

function RobotIllustration() {
  return (
    <svg viewBox="0 0 240 240" role="img" aria-label="Login assistant robot" className="auth-assistant__robot">
      <circle cx="120" cy="120" r="102" fill="#09144d" />
      <path d="M121 35a8 8 0 1 1-2 0v24h2V35Z" fill="#dce8f6" />
      <circle cx="120" cy="31" r="10" fill="#ffffff" />
      <rect x="63" y="67" width="114" height="96" rx="34" fill="#ffffff" />
      <rect x="76" y="84" width="88" height="52" rx="24" fill="#09144d" />
      <circle cx="100" cy="110" r="8" fill="#35d9f3" />
      <circle cx="140" cy="110" r="8" fill="#35d9f3" />
      <rect x="71" y="86" width="12" height="46" rx="6" fill="#dce8f6" />
      <rect x="157" y="86" width="12" height="46" rx="6" fill="#dce8f6" />
      <path d="M92 163h56v18a22 22 0 0 1-22 22h-12a22 22 0 0 1-22-22v-18Z" fill="#ffffff" />
      <path d="M98 163h44v22H98z" fill="#dce8f6" />
    </svg>
  );
}

export function AuthAssistant({ page = "login" }) {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState(() => [
    {
      id: "welcome",
      role: "assistant",
      content: PAGE_WELCOME[page] || "I can help you complete the authentication steps on this page.",
    },
  ]);

  const suggestions = useMemo(() => PAGE_HINTS[page] || PAGE_HINTS.login, [page]);

  function sendMessage(rawText) {
    const trimmed = rawText.trim();
    if (!trimmed) {
      return;
    }
    const reply = answerForMessage(trimmed, page);
    setMessages((current) => [
      ...current,
      { id: `${current.length + 1}-user`, role: "user", content: trimmed },
      { id: `${current.length + 1}-assistant`, role: "assistant", content: reply },
    ]);
    setInput("");
    setIsOpen(true);
  }

  return (
    <aside className="auth-assistant">
      <div className="auth-assistant__intro">
        <div className="auth-assistant__bubble">
          <p>Hi! I am here to help you.</p>
        </div>
        <RobotIllustration />
        <button type="button" className="auth-assistant__toggle btn" onClick={() => setIsOpen((current) => !current)}>
          {isOpen ? "Hide Help" : "Help Me"}
        </button>
      </div>

      {isOpen ? (
        <section className="auth-assistant__panel" aria-label="Authentication assistant">
          <div className="auth-assistant__header">
            <div>
              <strong>Login Assistant</strong>
              <p className="muted">Guidance only. I do not perform actions.</p>
            </div>
            <button type="button" className="auth-assistant__icon" onClick={() => setIsOpen(false)} aria-label="Close assistant">
              x
            </button>
          </div>

          <div className="auth-assistant__messages">
            {messages.map((message) => (
              <div key={message.id} className={`auth-assistant__message auth-assistant__message--${message.role}`}>
                {message.content.split("\n").map((line, index) => (
                  <p key={`${message.id}-${index}`}>{line}</p>
                ))}
              </div>
            ))}
          </div>

          <div className="auth-assistant__suggestions">
            {suggestions.map((suggestion) => (
              <button key={suggestion} type="button" className="auth-assistant__chip" onClick={() => sendMessage(suggestion)}>
                {suggestion}
              </button>
            ))}
          </div>

          <form
            className="auth-assistant__form"
            onSubmit={(event) => {
              event.preventDefault();
              sendMessage(input);
            }}
          >
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask for help"
              aria-label="Ask the login assistant"
            />
            <button type="submit" className="btn">Send</button>
          </form>
        </section>
      ) : null}
    </aside>
  );
}
