export function truncate(text: string, length = 140) {
  if (text.length <= length) return text;
  return text.slice(0, length) + "…";
}

export function normalizeWhitespace(text: string) {
  return text.replace(/\s+/g, " ").trim();
}
