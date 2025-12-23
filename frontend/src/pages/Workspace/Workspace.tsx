import { useState } from "react";
import WorkspaceLayout from "./Workspace.layout";
import CreatePost from "../../components/post/CreatePost";
import AIConversation from "../../components/ai/AIConversation";

export type WorkspaceMode = "compose" | "refine";

const Workspace = () => {
  const [mode, setMode] = useState<WorkspaceMode>("compose");
  const [draft, setDraft] = useState<string>("");

  const handleSubmitDraft = (content: string) => {
    setDraft(content);
    setMode("refine");
  };

  const handleSkipAI = () => {
    // user explicitly chooses not to refine with AI
    setMode("compose");
    setDraft("");
  };

  const handleFinalize = (finalContent: string) => {
    // at this point user can post or schedule
    console.log("Final content ready:", finalContent);
    setMode("compose");
    setDraft("");
  };

  return (
    <WorkspaceLayout>
      {mode === "compose" && (
        <CreatePost onSubmit={handleSubmitDraft} />
      )}

      {mode === "refine" && (
        <AIConversation
          initialPrompt={draft}
          onFinalize={handleFinalize}
          onSkip={handleSkipAI}
        />
      )}
    </WorkspaceLayout>
  );
};

export default Workspace;
