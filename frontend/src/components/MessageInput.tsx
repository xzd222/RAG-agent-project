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
    <form
      onSubmit={handleSubmit}
      className="flex items-end gap-3 border-t border-gray-100 bg-white/80 backdrop-blur px-4 py-4"
    >
      <input
        ref={inputRef}
        type="text"
        placeholder="输入你的问题，按回车发送…"
        disabled={disabled}
        className="flex-1 rounded-2xl border border-gray-200 bg-gray-50 px-5 py-3 text-sm
                   placeholder:text-gray-400
                   focus:border-violet-400 focus:bg-white focus:outline-none focus:ring-3 focus:ring-violet-100
                   disabled:opacity-50 transition-all"
      />
      <button
        type="submit"
        disabled={disabled}
        className="flex items-center gap-2 rounded-2xl bg-gradient-to-r from-violet-500 to-purple-600
                   px-5 py-3 text-sm font-medium text-white
                   hover:from-violet-600 hover:to-purple-700
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-all shadow-sm shadow-violet-200
                   active:scale-95"
      >
        {disabled ? (
          <>
            <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            思考中
          </>
        ) : (
          <>
            <span>发送</span>
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </>
        )}
      </button>
    </form>
  );
}
