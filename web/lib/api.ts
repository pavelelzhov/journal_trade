import { readAccess } from "@/components/access-panel";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiGet<T>(path: string): Promise<T> {
  const access = readAccess();
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "X-Role": access.role,
      "X-Telegram-User-Id": String(access.telegram_user_id),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function apiUpload(path: string, file: File): Promise<unknown> {
  const access = readAccess();
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "X-Role": access.role,
      "X-Telegram-User-Id": String(access.telegram_user_id),
    },
    body: form,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
