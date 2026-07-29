interface Props {
  content: string;
  role: "user" | "assistant";
}

export function MessageBubble({ content, role }: Props) {
  const isUser = role === "user";

  return (
    <div className={`flex items-start gap-3 mb-5 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {/* Avatar */}
      <div
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-medium
          ${isUser
            ? "bg-gradient-to-br from-violet-500 to-purple-600 text-white"
            : "bg-gradient-to-br from-emerald-400 to-teal-500 text-white"
          }`}
      >
        {isUser ? "我" : "AI"}
      </div>

      {/* Bubble */}
      <div
        className={`max-w-[72%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap shadow-sm
          ${isUser
            ? "bg-gradient-to-r from-violet-50 to-purple-50 text-gray-800 rounded-tr-md border border-violet-100"
            : "bg-white text-gray-800 rounded-tl-md border border-gray-200"
          }`}
      >
        {content || (
          <span className="inline-flex items-center gap-1 text-gray-400">
            <span className="animate-bounce delay-0">●</span>
            <span className="animate-bounce delay-100">●</span>
            <span className="animate-bounce delay-200">●</span>
          </span>
        )}
      </div>
    </div>
  );
}
