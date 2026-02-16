"use client";

import { useEffect, useState } from "react";

export type UIMode = "demo" | "api";

const KEY = "journal_ui_mode_v1";

export function getMode(): UIMode {
  if (typeof window === "undefined") return "demo";
  const mode = localStorage.getItem(KEY);
  return mode === "api" ? "api" : "demo";
}

export function ModeSwitch() {
  const [mode, setMode] = useState<UIMode>("demo");

  useEffect(() => {
    setMode(getMode());
  }, []);

  function onChange(next: UIMode) {
    setMode(next);
    localStorage.setItem(KEY, next);
  }

  return (
    <div className="flex items-center gap-2 rounded-md border bg-white p-2 text-sm">
      <span className="text-slate-500">Mode</span>
      <button className={`rounded px-2 py-1 ${mode === "demo" ? "bg-slate-900 text-white" : "bg-slate-100"}`} onClick={() => onChange("demo")}>
        Demo
      </button>
      <button className={`rounded px-2 py-1 ${mode === "api" ? "bg-slate-900 text-white" : "bg-slate-100"}`} onClick={() => onChange("api")}>
        API
      </button>
    </div>
  );
}
