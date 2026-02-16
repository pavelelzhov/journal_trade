import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes, Link, useParams } from "react-router-dom";
import { useReactTable, getCoreRowModel, flexRender, ColumnDef } from "@tanstack/react-table";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";

import "./styles.css";

type Trade = {
  id: number;
  symbol: string;
  side: string;
  status: string;
  entry_price?: number;
  size_pct?: number;
  leverage?: number;
  sl?: number;
  tp1?: number;
  tp2?: number;
  tp3?: number;
  raw_text?: string;
  parsed_json?: Record<string, unknown>;
  created_at?: string;
};

type Metrics = {
  kpi: { total_trades: number; winrate: number; profit_factor: number; expectancy: number };
  r_histogram: Array<{ r: number; count: number }>;
  equity_curve: Array<{ index: number; equity: number }>;
};

async function getTrades(): Promise<{ items: Trade[]; total: number }> {
  const res = await fetch("/journal_trade/demo/trades.json");
  return res.json();
}

async function getMetrics(): Promise<Metrics> {
  const [m, e] = await Promise.all([
    fetch("/journal_trade/demo/metrics.json").then((r) => r.json()),
    fetch("/journal_trade/demo/equity.json").then((r) => r.json()),
  ]);
  return { ...(m as any), equity_curve: e as any };
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="container">
      <header className="header">
        <h1>Journal UI</h1>
        <nav>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/trades">Trades</Link>
          <Link to="/metrics">Metrics</Link>
          <Link to="/import-export">Import/Export</Link>
        </nav>
      </header>
      {children}
    </div>
  );
}

function DashboardPage() {
  const { data } = useQuery({ queryKey: ["metrics"], queryFn: getMetrics });
  const kpi = data?.kpi ?? { total_trades: 0, winrate: 0, profit_factor: 0, expectancy: 0 };
  return (
    <Layout>
      <div className="grid">
        <div className="card">Total: {kpi.total_trades}</div>
        <div className="card">Winrate: {kpi.winrate}%</div>
        <div className="card">PF: {kpi.profit_factor}</div>
        <div className="card">Expectancy: {kpi.expectancy}</div>
      </div>
      <div className="card h300">
        <h3>Equity curve</h3>
        <ResponsiveContainer width="100%" height="90%">
          <LineChart data={data?.equity_curve ?? []}>
            <XAxis dataKey="index" />
            <YAxis />
            <Tooltip />
            <Line dataKey="equity" stroke="#22c55e" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Layout>
  );
}

function TradesPage() {
  const { data } = useQuery({ queryKey: ["trades"], queryFn: getTrades });
  const columns: ColumnDef<Trade>[] = [
    { header: "ID", accessorKey: "id", cell: ({ row }) => <Link to={`/trades/${row.original.id}`}>{row.original.id}</Link> },
    { header: "Symbol", accessorKey: "symbol" },
    { header: "Side", accessorKey: "side" },
    { header: "Status", accessorKey: "status" },
  ];
  const table = useReactTable({ data: data?.items ?? [], columns, getCoreRowModel: getCoreRowModel() });
  return (
    <Layout>
      <div className="card"><input placeholder="Filter demo" /></div>
      <div className="card">
        <table>
          <thead>
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>{hg.headers.map((h) => <th key={h.id}>{flexRender(h.column.columnDef.header, h.getContext())}</th>)}</tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((r) => (
              <tr key={r.id}>{r.getVisibleCells().map((c) => <td key={c.id}>{flexRender(c.column.columnDef.cell, c.getContext())}</td>)}</tr>
            ))}
            {!table.getRowModel().rows.length && <tr><td colSpan={4}>No trades</td></tr>}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}

function TradeDetailPage() {
  const { id } = useParams();
  const { data } = useQuery({ queryKey: ["trades"], queryFn: getTrades });
  const trade = data?.items.find((x) => String(x.id) === id);
  return (
    <Layout>
      <div className="card">
        {!trade ? (
          <p>Trade not found.</p>
        ) : (
          <>
            <h2>Trade #{trade.id}</h2>
            <p>{trade.symbol} / {trade.side}</p>
            <p>Status: {trade.status}</p>
            <p>Entry: {trade.entry_price ?? "-"}</p>
            <p>SL: {trade.sl ?? "-"}</p>
          </>
        )}
      </div>
    </Layout>
  );
}

function MetricsPage() {
  const { data } = useQuery({ queryKey: ["metrics"], queryFn: getMetrics });
  return (
    <Layout>
      <div className="card h300">
        <h3>R histogram</h3>
        <ResponsiveContainer width="100%" height="90%">
          <BarChart data={data?.r_histogram ?? []}>
            <XAxis dataKey="r" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#38bdf8" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Layout>
  );
}

function ImportExportPage() {
  return (
    <Layout>
      <div className="card">
        <h3>Import / Export</h3>
        <p>Demo mode is connected to static dataset.</p>
      </div>
    </Layout>
  );
}

function App() {
  return (
    <BrowserRouter basename="/journal_trade">
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/trades" element={<TradesPage />} />
        <Route path="/trades/:id" element={<TradeDetailPage />} />
        <Route path="/metrics" element={<MetricsPage />} />
        <Route path="/import-export" element={<ImportExportPage />} />
      </Routes>
    </BrowserRouter>
  );
}

const queryClient = new QueryClient();
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
