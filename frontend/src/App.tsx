import { useCallback, useState } from "react";
import type { ChatMessage } from "./api/chat";
import { streamChat } from "./api/chat";
import { ChatBox } from "./components/ChatBox";
import { MessageInput } from "./components/MessageInput";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSend = useCallback(async (text: string) => {
    const userMsg: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);

    const assistantMsg: ChatMessage = { role: "assistant", content: "" };
    setMessages((prev) => [...prev, assistantMsg]);

    setLoading(true);
    try {
      for await (const chunk of streamChat(text)) {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          updated[updated.length - 1] = { ...last, content: last.content + chunk };
          return updated;
        });
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "请求失败";
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        updated[updated.length - 1] = {
          ...last,
          content: last.content || `❌ 错误: ${msg}`,
        };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="mx-auto flex h-screen max-w-3xl flex-col bg-white shadow-lg">
      {/* Header */}
      <header className="border-b bg-white px-4 py-4">
        <h1 className="text-center text-lg font-semibold text-gray-800">
          💬 智能客服
        </h1>
      </header>

      {/* Messages */}
      <ChatBox messages={messages} />

      {/* Input */}
      <MessageInput onSend={handleSend} disabled={loading} />
    </div>
  );
}
