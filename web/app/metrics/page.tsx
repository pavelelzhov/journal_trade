"use client";

import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell } from "recharts";
import { Card } from "@/components/ui/card";
import { apiGet } from "@/lib/api";

type MetricsResponse = {
  kpi: { total_trades: number; winrate: number; profit_factor: number; expectancy: number };
  r_histogram: Array<{ r: number; count: number }>;
  breakdown_by_symbol: Array<{ symbol: string; count: number }>;
};

export default function MetricsPage() {
  const { data } = useQuery({ queryKey: ["metrics-full"], queryFn: () => apiGet<MetricsResponse>("/metrics") });
  const breakdown = data?.breakdown_by_symbol ?? [];

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <h3 className="mb-2 font-semibold">R histogram</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data?.r_histogram ?? []}>
              <XAxis dataKey="r" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0f172a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
      <Card>
        <h3 className="mb-2 font-semibold">Breakdown by symbol</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={breakdown} dataKey="count" nameKey="symbol" outerRadius={90}>
                {breakdown.map((_, i) => <Cell key={i} fill={["#0f172a", "#334155", "#64748b", "#94a3b8"][i % 4]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}
