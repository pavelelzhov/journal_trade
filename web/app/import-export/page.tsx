"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { apiUpload, exportUrl } from "@/lib/api";

async function downloadWithHeaders(format: "csv" | "json") {
  const res = await fetch(exportUrl(format));
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `trades.${format}`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ImportExportPage() {
  const [result, setResult] = useState("");

  async function handleUpload(format: "csv" | "json", file: File | null) {
    if (!file) return;
    const res = await apiUpload(`/import?format=${format}`, file);
    setResult(JSON.stringify(res, null, 2));
  }

  return (
    <div className="space-y-4">
      <Card className="space-y-2">
        <h3 className="font-semibold">Import</h3>
        <div className="flex flex-wrap items-center gap-2">
          <input type="file" accept=".csv" onChange={(e) => handleUpload("csv", e.target.files?.[0] ?? null)} />
          <input type="file" accept=".json" onChange={(e) => handleUpload("json", e.target.files?.[0] ?? null)} />
        </div>
        <pre className="overflow-auto rounded bg-slate-100 p-2 text-xs">{result || "No uploads yet"}</pre>
      </Card>

      <Card className="space-y-2">
        <h3 className="font-semibold">Export</h3>
        <div className="flex gap-2">
          <Button onClick={() => downloadWithHeaders("json")}>Export JSON</Button>
          <Button onClick={() => downloadWithHeaders("csv")}>Export CSV</Button>
        </div>
      </Card>
    </div>
  );
}
