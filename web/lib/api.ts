import { readAccess } from "@/components/access-panel";
import { getMode } from "@/components/mode-switch";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH || "/journal_trade";

function withBasePath(path: string): string {
  return `${BASE_PATH}${path}`;
}

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, { ...init, cache: "no-store" });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return (await res.json()) as T;
}

export async function getTrades(pathWithQuery: string): Promise<any> {
  const mode = getMode();
  if (mode === "demo") {
    return fetchJson<{ items: any[]; total: number }>(withBasePath("/demo/trades.json"));
  }

  const access = readAccess();
  return fetchJson(`${API_BASE}${pathWithQuery}`, {
    headers: {
      "X-Role": access.role,
      "X-Telegram-User-Id": String(access.telegram_user_id),
    },
  });
}

export async function getTradeById(id: string): Promise<any> {
  const mode = getMode();
  if (mode === "demo") {
    const demo = await fetchJson<{ items: any[] }>(withBasePath("/demo/trades.json"));
    const found = demo.items.find((x) => String(x.id) === id);
    if (!found) throw new Error("Not found");
    return found;
  }

  const access = readAccess();
  return fetchJson(`${API_BASE}/trades/${id}`, {
    headers: {
      "X-Role": access.role,
      "X-Telegram-User-Id": String(access.telegram_user_id),
    },
  });
}

export async function getMetrics(): Promise<any> {
  const mode = getMode();
  if (mode === "demo") {
    const [metrics, equity] = await Promise.all([
      fetchJson(withBasePath("/demo/metrics.json")),
      fetchJson(withBasePath("/demo/equity.json")),
    ]);
    return { ...(metrics as any), equity_curve: equity };
  }

  const access = readAccess();
  return fetchJson(`${API_BASE}/metrics`, {
    headers: {
      "X-Role": access.role,
      "X-Telegram-User-Id": String(access.telegram_user_id),
    },
  });
}

export async function apiUpload(path: string, file: File): Promise<unknown> {
  const mode = getMode();
  if (mode === "demo") {
    return { imported: 0, failed: 0, errors: [], note: "Demo mode: upload disabled" };
  }
  const access = readAccess();
  const form = new FormData();
  form.append("file", file);
  return fetchJson(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "X-Role": access.role,
      "X-Telegram-User-Id": String(access.telegram_user_id),
    },
    body: form,
  });
}

export function exportUrl(format: "csv" | "json"): string {
  const mode = getMode();
  if (mode === "demo") {
    return withBasePath("/demo/trades.json");
  }
  return `${API_BASE}/export?format=${format}`;
}
