interface Props {
  content: string;
  role: "user" | "assistant";
}

export function MessageBubble({ content, role }: Props) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap
          ${isUser
            ? "bg-blue-600 text-white rounded-br-md"
            : "bg-gray-100 text-gray-900 rounded-bl-md"
          }`}
      >
        {content}
      </div>
    </div>
  );
}
