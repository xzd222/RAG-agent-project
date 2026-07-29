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
    <div className="flex-1 overflow-y-auto px-4 py-6">
      {messages.length === 0 && (
        <div className="flex h-full items-center justify-center text-gray-400">
          <p>输入问题，开始对话</p>
        </div>
      )}
      {messages.map((msg, i) => (
        <MessageBubble key={i} role={msg.role} content={msg.content} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
