"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useReactTable, getCoreRowModel, flexRender, ColumnDef } from "@tanstack/react-table";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { getTrades } from "@/lib/api";

type Trade = { id: number; trader_id: number; symbol: string; side: string; status: string; position_pct: number | null; ts: string | null };

type TradesResponse = { items: Trade[]; total: number };

export default function TradesPage() {
  const [symbol, setSymbol] = useState("");
  const [side, setSide] = useState("");
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [traderId, setTraderId] = useState("");
  const [page, setPage] = useState(0);
  const limit = 20;

  const query = useMemo(() => {
    const p = new URLSearchParams({ limit: String(limit), offset: String(page * limit) });
    if (symbol) p.set("symbol", symbol);
    if (side) p.set("side", side);
    if (status) p.set("status", status);
    if (search) p.set("search", search);
    if (dateFrom) p.set("date_from", dateFrom);
    if (dateTo) p.set("date_to", dateTo);
    if (traderId) p.set("trader_id", traderId);
    return p.toString();
  }, [symbol, side, status, search, dateFrom, dateTo, traderId, page]);

  const { data } = useQuery({
    queryKey: ["trades", query],
    queryFn: () => getTrades(`/trades?${query}`) as Promise<TradesResponse>,
  });

  const columns = useMemo<ColumnDef<Trade>[]>(
    () => [
      { header: "ID", accessorKey: "id", cell: ({ row }) => <Link className="underline" href={`/trades/${row.original.id}`}>{row.original.id}</Link> },
      { header: "Trader", accessorKey: "trader_id" },
      { header: "Symbol", accessorKey: "symbol" },
      { header: "Side", accessorKey: "side" },
      { header: "Status", accessorKey: "status" },
      { header: "Size %", accessorKey: "position_pct" },
      { header: "TS", accessorKey: "ts" },
    ],
    []
  );

  const table = useReactTable({ data: data?.items ?? [], columns, getCoreRowModel: getCoreRowModel() });
  const total = data?.total ?? 0;

  return (
    <div className="space-y-4">
      <Card className="grid gap-2 md:grid-cols-4">
        <Input placeholder="symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)} />
        <Input placeholder="side" value={side} onChange={(e) => setSide(e.target.value)} />
        <Input placeholder="status" value={status} onChange={(e) => setStatus(e.target.value)} />
        <Input placeholder="search" value={search} onChange={(e) => setSearch(e.target.value)} />
        <Input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
        <Input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
        <Input placeholder="trader_id (admin)" value={traderId} onChange={(e) => setTraderId(e.target.value)} />
      </Card>

      <Card>
        <table className="w-full text-sm">
          <thead>
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((h) => (
                  <th key={h.id} className="border-b p-2 text-left">{flexRender(h.column.columnDef.header, h.getContext())}</th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="border-b p-2">{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
                ))}
              </tr>
            ))}
            {!table.getRowModel().rows.length && (
              <tr><td className="p-4 text-slate-500" colSpan={7}>No trades</td></tr>
            )}
          </tbody>
        </table>
      </Card>

      <div className="flex items-center gap-2">
        <Button disabled={page === 0} onClick={() => setPage((p) => p - 1)}>Prev</Button>
        <span>Page {page + 1} / {Math.max(1, Math.ceil(total / limit))}</span>
        <Button disabled={(page + 1) * limit >= total} onClick={() => setPage((p) => p + 1)}>Next</Button>
      </div>
    </div>
  );
}
