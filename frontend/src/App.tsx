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
    <div className="mx-auto flex h-screen max-w-3xl flex-col bg-white shadow-2xl">
      {/* Header */}
      <header className="border-b border-gray-100 bg-gradient-to-r from-violet-500 via-purple-500 to-fuchsia-500 px-4 py-4 shadow-sm">
        <div className="flex items-center justify-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/20">
            <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
            </svg>
          </div>
          <h1 className="text-lg font-semibold text-white">智能客服</h1>
        </div>
      </header>

      {/* Messages */}
      <ChatBox messages={messages} />

      {/* Input */}
      <MessageInput onSend={handleSend} disabled={loading} />
    </div>
  );
}
