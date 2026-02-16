"use client";

import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useMemo, useState } from "react";
import { apiGet } from "@/lib/api";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type MetricsResponse = {
  kpi: { total_trades: number; winrate: number; profit_factor: number; expectancy: number };
  equity_curve: Array<{ index: number; equity: number }>;
};

export default function DashboardPage() {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const query = useMemo(() => {
    const params = new URLSearchParams();
    if (dateFrom) params.set("date_from", dateFrom);
    if (dateTo) params.set("date_to", dateTo);
    return params.toString();
  }, [dateFrom, dateTo]);

  const { data } = useQuery({
    queryKey: ["metrics", query],
    queryFn: () => apiGet<MetricsResponse>(`/metrics${query ? `?${query}` : ""}`),
  });

  const kpi = data?.kpi ?? { total_trades: 0, winrate: 0, profit_factor: 0, expectancy: 0 };
  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
        <Input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
      </div>

      <div className="grid gap-3 md:grid-cols-4">
        <Card>Total trades: {kpi.total_trades}</Card>
        <Card>Winrate: {kpi.winrate}%</Card>
        <Card>PF: {kpi.profit_factor}</Card>
        <Card>Expectancy: {kpi.expectancy}</Card>
      </div>

      <Card className="h-72">
        <p className="mb-2 font-medium">Equity curve</p>
        <ResponsiveContainer width="100%" height="90%">
          <LineChart data={data?.equity_curve ?? []}>
            <XAxis dataKey="index" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="equity" stroke="#0f172a" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
}
