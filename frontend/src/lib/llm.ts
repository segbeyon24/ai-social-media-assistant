export async function sendToLLM(prompt: string): Promise<string> {
  // Placeholder for backend call
  // This WILL be replaced with your /ai endpoint
  await new Promise((r) => setTimeout(r, 1200));

  return `Refined version:\n\n${prompt}`;
}
