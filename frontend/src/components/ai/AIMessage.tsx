import { AIMessage as Msg } from "../../state/ai";

export default function AIMessage({ role, content }: Msg) {
  const isAI = role === "assistant";

  return (
    <div
      className={`flex ${
        isAI ? "justify-start" : "justify-end"
      }`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isAI
            ? "bg-neutral-100 text-neutral-800"
            : "bg-neutral-900 text-white"
        }`}
      >
        {content}
      </div>
    </div>
  );
}
