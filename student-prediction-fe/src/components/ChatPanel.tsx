import { useEffect, useRef, useState } from "react";
import { apiClient } from "../api/client";
import type { ConversationTurn } from "../api/types";
import type { RiskAssessment } from "../types";
import "./ChatPanel.css";

interface TextMessage {
  id: string;
  kind: "text";
  isUser: boolean;
  text: string;
}

interface ResultMessage {
  id: string;
  kind: "result";
  result: RiskAssessment;
}

type ChatMessage = TextMessage | ResultMessage;

let idCounter = 0;
function nextId() {
  idCounter += 1;
  return `msg-${idCounter}`;
}

const WELCOME_MESSAGE: ChatMessage = {
  id: nextId(),
  kind: "text",
  isUser: false,
  text: "Hi, I'm the assistant. Describe a student's situation in plain language and I'll assess their dropout risk.",
};

function turnsToMessages(turns: ConversationTurn[], assessment?: RiskAssessment): ChatMessage[] {
  const msgs: ChatMessage[] = turns.map((t) => ({
    id: nextId(),
    kind: "text" as const,
    isUser: t.role === "user",
    text: t.content,
  }));
  if (assessment) {
    msgs.push({ id: nextId(), kind: "result", result: assessment });
  }
  return msgs;
}

interface ChatPanelProps {
  resumeConversationId?: string;
  resumeTurns?: ConversationTurn[];
  resumeAssessment?: RiskAssessment;
}

export function ChatPanel({ resumeConversationId, resumeTurns, resumeAssessment }: ChatPanelProps) {
  const initialMessages = resumeTurns && resumeTurns.length > 0
    ? turnsToMessages(resumeTurns, resumeAssessment)
    : [WELCOME_MESSAGE];

  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(resumeConversationId);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  async function sendMessage() {
    const text = input.trim();
    if (!text) return;

    setMessages((prev) => [...prev, { id: nextId(), kind: "text", isUser: true, text }]);
    setInput("");
    setIsThinking(true);

    const response = await apiClient.predictChat({ message: text, conversationId });
    setConversationId(response.conversationId);

    if (response.type === "need_more_info") {
      setMessages((prev) => [...prev, { id: nextId(), kind: "text", isUser: false, text: response.question }]);
    } else {
      setMessages((prev) => [...prev, { id: nextId(), kind: "result", result: response.data }]);
    }
    setIsThinking(false);
  }

  return (
    <div className="chat-panel">
      <div className="chat-panel__scroll" ref={scrollRef}>
        {messages.map((msg) =>
          msg.kind === "text" ? (
            <div key={msg.id} className={`chat-bubble ${msg.isUser ? "chat-bubble--user" : "chat-bubble--assistant"}`}>
              {msg.text}
            </div>
          ) : (
            <div key={msg.id} className="result-card">
              <div className={`result-card__header result-card__header--${msg.result.riskLevel}`}>
                <span className="result-card__risk">
                  {msg.result.riskLevel === "high" ? "High" : msg.result.riskLevel === "medium" ? "Medium" : "Low"} risk ·{" "}
                  {Math.round(msg.result.riskProb * 100)}%
                </span>
                <span className="result-card__status-pill">{msg.result.statusLabel}</span>
              </div>
              <div className="result-card__body">
                <div className="result-card__section-label">Recommended intervention</div>
                <div className="result-card__recommendation">{msg.result.recommendation}</div>
                <div className="result-card__section-label">Why</div>
                <div className="result-card__factors">
                  {msg.result.factors.map((factor) => (
                    <div className="result-card__factor" key={factor}>
                      <span className="result-card__bullet">•</span>
                      <span>{factor}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ),
        )}
        {isThinking && (
          <div className="thinking-indicator">
            <span className="thinking-dot" />
            <span className="thinking-dot" style={{ animationDelay: "0.15s" }} />
            <span className="thinking-dot" style={{ animationDelay: "0.3s" }} />
          </div>
        )}
      </div>
      <div className="chat-panel__input-row">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") sendMessage();
          }}
          placeholder="Describe the student's situation..."
          className="chat-input"
        />
        <button type="button" onClick={sendMessage} className="chat-send-btn">
          Send
        </button>
      </div>
    </div>
  );
}
