import { useCallback } from "react";
import { useAIStore } from "../state/ai";
import { sendToLLM } from "../lib/llm";

export function useAIConversation() {
  const { messages, isThinking, addMessage, setThinking, reset } =
    useAIStore();

  const ask = useCallback(
    async (prompt: string) => {
      setThinking(true);

      addMessage({ role: "user", content: prompt });

      const response = await sendToLLM(prompt);

      addMessage({ role: "assistant", content: response });
      setThinking(false);
    },
    [addMessage, setThinking]
  );

  return {
    messages,
    isThinking,
    ask,
    reset,
  };
}
