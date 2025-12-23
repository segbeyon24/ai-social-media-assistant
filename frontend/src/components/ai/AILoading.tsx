export default function AILoading() {
  return (
    <div className="flex items-center gap-2 text-sm text-neutral-400">
      <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-neutral-400" />
      <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-neutral-400 delay-150" />
      <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-neutral-400 delay-300" />
    </div>
  );
}
