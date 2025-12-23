import { nanoid } from "nanoid";
import { useAIStore } from "../../state/ai";
import AIMessage from "./AIMessage";
import AILoading from "./AILoading";

interface Props {
  initialPrompt: string;
}

export default function AIConversation({ initialPrompt }: Props) {
  const {
    messages,
    isThinking,
    enabled,
    addMessage,
    setThinking,
    setEnabled,
  } = useAIStore();

  const sendToAI = async (text: string) => {
    addMessage({
      id: nanoid(),
      role: "user",
      content: text,
    });

    setThinking(true);

    // v1 mock – replace with llm.ts later
    await new Promise((r) => setTimeout(r, 1200));

    addMessage({
      id: nanoid(),
      role: "assistant",
      content:
        "I can help refine this. Would you like it to be clearer, more persuasive, or more concise?",
    });

    setThinking(false);
  };

  if (!enabled) return null;

  return (
    <div className="mt-6 space-y-4">
      {/* Initial AI response trigger */}
      {messages.length === 0 && (
        <button
          onClick={() => sendToAI(initialPrompt)}
          className="rounded-xl border border-neutral-200 px-4 py-2 text-sm hover:bg-neutral-50"
        >
          Refine with AI
        </button>
      )}

      {/* Conversation */}
      {messages.map((m) => (
        <AIMessage key={m.id} {...m} />
      ))}

      {isThinking && <AILoading />}

      {/* Opt-out */}
      {messages.length > 0 && !isThinking && (
        <button
          onClick={() => setEnabled(false)}
          className="text-xs text-neutral-400 hover:underline"
        >
          Skip AI and continue
        </button>
      )}
    </div>
  );
}
