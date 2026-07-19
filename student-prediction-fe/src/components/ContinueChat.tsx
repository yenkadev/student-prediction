import type { ConversationDetail } from "../api/types";
import { ChatPanel } from "./ChatPanel";
import "./ContinueChat.css";

interface ContinueChatProps {
  conversation: ConversationDetail;
  onBack: () => void;
}

export function ContinueChat({ conversation, onBack }: ContinueChatProps) {
  return (
    <div className="continue-chat">
      <button type="button" className="continue-chat__back" onClick={onBack}>
        ← Back
      </button>
      <ChatPanel
        resumeConversationId={conversation.id}
        resumeTurns={conversation.turns}
        resumeAssessment={conversation.assessment}
      />
    </div>
  );
}
