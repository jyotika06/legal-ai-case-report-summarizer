import { useState, useContext, useRef, useEffect } from "react";
import { DataContext } from "../context/DataContext";
import "../App.css";

function ChatBot() {
  const { extractedText } = useContext(DataContext);
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello! How can I assist you with the judgment?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const msgEndRef = useRef(null);

  useEffect(() => {
    msgEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/chatbot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: userMsg.text,
          context: extractedText,
        }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: data.answer },
      ]);

    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "⚠ Network error. Try again." },
      ]);
    }

    setLoading(false);
  };

  return (
    <>
      {/* Floating Bubble with GIF */}
      {!open && (
        <div className="chatbot-bubble" onClick={() => setOpen(true)}>
          <img src="/chatbot.gif" alt="Chatbot" />
        </div>
      )}

      {/* Chat Window */}
      {open && (
        <div className="chatbot-window">

          <div className="chatbot-header">
            <div>
              <strong>Legal AI Assistant</strong>
              <div className="chatbot-sub">Online • Ready</div>
            </div>

            <span className="chatbot-close" onClick={() => setOpen(false)}>
              ✖
            </span>
          </div>

          <div className="chatbot-messages">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`msg ${
                  msg.sender === "user" ? "msg-user" : "msg-bot"
                }`}
              >
                {msg.text}
              </div>
            ))}

            {loading && (
              <div className="msg msg-bot typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            )}

            <div ref={msgEndRef}></div>
          </div>

          <div className="chatbot-input">
            <input
              placeholder="Ask something about the judgment..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button onClick={sendMessage}>Send</button>
          </div>

        </div>
      )}
    </>
  );
}

export default ChatBot;