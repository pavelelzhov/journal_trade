"use client";

import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { getMode } from "@/components/mode-switch";
import { readAccess } from "@/components/access-panel";

type UsersResponse = { items: Array<{ user_id: number; telegram_user_id: number; role: string; trader_id: number | null }> };

export default function AdminUsersPage() {
  const { data, isError } = useQuery({ queryKey: ["admin-users"], queryFn: async () => {
    if (getMode() === "demo") return { items: [] } as UsersResponse;
    const access = readAccess();
    const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
    const r = await fetch(`${base}/admin/users`, { headers: { "X-Role": access.role, "X-Telegram-User-Id": String(access.telegram_user_id) } });
    if (!r.ok) throw new Error("forbidden");
    return r.json() as Promise<UsersResponse>;
  } });

  if (isError) return <Card>Admin only. Set role=ADMIN in access panel.</Card>;

  return (
    <Card>
      <h2 className="mb-2 text-lg font-semibold">Users</h2>
      <table className="w-full text-sm">
        <thead>
          <tr><th className="text-left">user_id</th><th className="text-left">telegram_user_id</th><th className="text-left">role</th><th className="text-left">trader_id</th></tr>
        </thead>
        <tbody>
          {(data?.items ?? []).map((u) => (
            <tr key={u.user_id}><td>{u.user_id}</td><td>{u.telegram_user_id}</td><td>{u.role}</td><td>{String(u.trader_id ?? "-")}</td></tr>
          ))}
          {!data?.items?.length && <tr><td colSpan={4} className="text-slate-500">No users</td></tr>}
        </tbody>
      </table>
    </Card>
  );
}
