"use client";

import { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";

export type AccessState = { role: "ADMIN" | "TRADER"; telegram_user_id: number };

const DEFAULT_ACCESS: AccessState = { role: "TRADER", telegram_user_id: 1001 };

export function readAccess(): AccessState {
  if (typeof window === "undefined") return DEFAULT_ACCESS;
  const raw = localStorage.getItem("journal_access_v1");
  if (!raw) return DEFAULT_ACCESS;
  try {
    return JSON.parse(raw) as AccessState;
  } catch {
    return DEFAULT_ACCESS;
  }
}

export function AccessPanel() {
  const [role, setRole] = useState<"ADMIN" | "TRADER">("TRADER");
  const [telegramUserId, setTelegramUserId] = useState("1001");

  useEffect(() => {
    const saved = readAccess();
    setRole(saved.role);
    setTelegramUserId(String(saved.telegram_user_id));
  }, []);

  useEffect(() => {
    const payload: AccessState = {
      role,
      telegram_user_id: Number(telegramUserId || "0"),
    };
    localStorage.setItem("journal_access_v1", JSON.stringify(payload));
  }, [role, telegramUserId]);

  return (
    <div className="flex items-center gap-2 rounded-md border bg-white p-2 text-sm">
      <label className="text-slate-500">Role</label>
      <select value={role} onChange={(e) => setRole(e.target.value as "ADMIN" | "TRADER")} className="rounded border px-2 py-1">
        <option value="TRADER">TRADER</option>
        <option value="ADMIN">ADMIN</option>
      </select>
      <label className="text-slate-500">telegram_user_id</label>
      <Input value={telegramUserId} onChange={(e) => setTelegramUserId(e.target.value)} className="w-28" />
    </div>
  );
}
