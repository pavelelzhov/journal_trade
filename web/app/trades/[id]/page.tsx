"use client";

import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { apiGet } from "@/lib/api";

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
};

export default function TradeDetailsPage({ params }: { params: { id: string } }) {
  const { data, isError } = useQuery({
    queryKey: ["trade", params.id],
    queryFn: () => apiGet<Trade>(`/trades/${params.id}`),
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
      <p>R: -</p>
      <p>Notes: -</p>
      <p>Tags: -</p>
    </Card>
  );
}
