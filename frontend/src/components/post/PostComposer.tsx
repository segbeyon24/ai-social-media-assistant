import { useState } from "react";
import { handleComposerKey } from "../../utils/keyboard";

interface Props {
  onSubmit: (text: string) => void;
}

export default function PostComposer({ onSubmit }: Props) {
  const [text, setText] = useState("");

  const submit = () => {
    if (!text.trim()) return;
    onSubmit(text.trim());
    setText("");
  };

  return {
    text,
    setText,
    submit,
    onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) =>
      handleComposerKey(e, submit),
  };
}
