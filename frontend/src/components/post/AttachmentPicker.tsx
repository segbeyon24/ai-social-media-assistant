import { Paperclip } from "lucide-react";

export default function AttachmentPicker() {
  return (
    <button
      type="button"
      title="Attachments coming soon"
      disabled
      className="rounded-lg p-2 text-neutral-400 hover:bg-neutral-100"
    >
      <Paperclip size={18} />
    </button>
  );
}
