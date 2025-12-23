export type PostFormat = "text" | "image" | "video" | "carousel";

export interface PostDraft {
  id: string;
  content: string;
  format: PostFormat;
  createdAt: number;
}

export interface PublishedPost extends PostDraft {
  platforms: string[];
  scheduledFor?: number;
}
