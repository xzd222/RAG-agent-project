import { type FormEvent, useRef } from "react";

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function MessageInput({ onSend, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const text = inputRef.current?.value.trim();
    if (!text || disabled) return;
    onSend(text);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 border-t bg-white p-4">
      <input
        ref={inputRef}
        type="text"
        placeholder="输入你的问题…"
        disabled={disabled}
        className="flex-1 rounded-xl border border-gray-300 px-4 py-3 text-sm
                   focus:outline-none focus:ring-2 focus:ring-blue-500
                   disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled}
        className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-medium text-white
                   hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        发送
      </button>
    </form>
  );
}
