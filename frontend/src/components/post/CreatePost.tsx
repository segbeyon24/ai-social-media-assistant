import { useState } from "react";
import PostComposer from "./PostComposer";
import AttachmentPicker from "./AttachmentPicker";
import PostPreview from "./PostPreview";

export default function CreatePost() {
  const [submittedText, setSubmittedText] = useState<string | null>(null);

  return (
    <div className="w-full max-w-3xl rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm">
      {/* Input */}
      <div className="flex items-end gap-2">
        <PostComposer
          onSubmit={(text) => {
            setSubmittedText(text);
          }}
        >
          {({ text, setText, onKeyDown }) => (
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Write something…"
              rows={1}
              className="flex-1 resize-none rounded-xl border border-neutral-200 px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-neutral-300"
            />
          )}
        </PostComposer>

        <AttachmentPicker />
      </div>

      {/* Preview */}
      {submittedText && <PostPreview content={submittedText} />}
    </div>
  );
}
