export type AIProvider = "gpt" | "gemini" | "copilot";

export type AIRole = "user" | "assistant" | "system";

export interface AIMessage {
  id: string;
  role: AIRole;
  content: string;
  createdAt: number;
}

export interface AIConversation {
  id: string;
  provider: AIProvider;
  messages: AIMessage[];
  active: boolean;
}
