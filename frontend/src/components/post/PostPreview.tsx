interface Props {
  content: string;
}

export default function PostPreview({ content }: Props) {
  if (!content) return null;

  return (
    <div className="mt-4 rounded-xl border border-neutral-200 bg-neutral-50 p-4 text-sm">
      <p className="whitespace-pre-wrap text-neutral-800">{content}</p>
    </div>
  );
}
