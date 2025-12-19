import { supabase } from "./supabase";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

/* ---------------- auth header helper ---------------- */

async function authHeaders(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;

  return token ? { Authorization: `Bearer ${token}` } : {};
}

/* ---------------- low-level helpers ---------------- */

async function apiGet<T>(path: string): Promise<T> {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}${path}`, { headers });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json();
}

async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const headers = {
    ...(await authHeaders()),
    "Content-Type": "application/json",
  };

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json();
}

/* ---------------- public API ---------------- */

export const api = {
  get: apiGet,
  post: apiPost,
};
