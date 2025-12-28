import { useState } from "react";
import { handleComposerKey } from "../../utils/keyboard";

interface Props {
  onSubmit: (text: string) => void;
  children: (props: {
    text: string;
    setText: (text: string) => void;
    submit: () => void;
    onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  }) => React.ReactNode;
}

export default function PostComposer({ onSubmit, children }: Props) {
  const [text, setText] = useState("");

  const submit = () => {
    if (!text.trim()) return;
    onSubmit(text.trim());
    setText("");
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) =>
    handleComposerKey(e, submit);

  return children({ text, setText, submit, onKeyDown });
}
