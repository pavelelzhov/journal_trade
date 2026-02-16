"use client";

import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { getTradeById } from "@/lib/api";

type Trade = {
  id: number;
  trader_id: number;
  symbol: string;
  side: string;
  entries: unknown[];
  sl: number | null;
  tps: unknown[];
  position_pct: number | null;
  status: string;
  r?: number;
  notes?: string;
  tags?: string[];
};

export function TradeDetailsClient({ id }: { id: string }) {
  const { data, isError } = useQuery({
    queryKey: ["trade", id],
    queryFn: () => getTradeById(id) as Promise<Trade>,
  });

  if (isError) return <Card>Not found or access denied.</Card>;
  if (!data) return <Card>Loading...</Card>;

  return (
    <Card className="space-y-2">
      <h2 className="text-lg font-semibold">Trade #{data.id}</h2>
      <p>Symbol: {data.symbol}</p>
      <p>Side: {data.side}</p>
      <p>Status: {data.status}</p>
      <p>SL: {String(data.sl ?? "-")}</p>
      <p>TP: {JSON.stringify(data.tps)}</p>
      <p>Entries: {JSON.stringify(data.entries)}</p>
      <p>Size %: {String(data.position_pct ?? "-")}</p>
      <p>R: {String(data.r ?? "-")}</p>
      <p>Notes: {data.notes ?? "-"}</p>
      <p>Tags: {data.tags?.join(", ") || "-"}</p>
    </Card>
  );
}
