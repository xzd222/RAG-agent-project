import { useEffect, useRef } from "react";
import type { ChatMessage } from "../api/chat";
import { MessageBubble } from "./MessageBubble";

interface Props {
  messages: ChatMessage[];
}

export function ChatBox({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto bg-gradient-to-b from-violet-50/30 via-white to-white px-4 py-6">
      {messages.length === 0 && (
        <div className="flex h-full flex-col items-center justify-center gap-3">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-400 to-purple-500 shadow-lg shadow-violet-200">
            <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
            </svg>
          </div>
          <p className="text-gray-400 text-sm">基于知识库的智能问答助手</p>
        </div>
      )}
      {messages.map((msg, i) => (
        <MessageBubble key={i} role={msg.role} content={msg.content} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
