"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/dashboard");
  }, [router]);

  return <p className="p-6 text-sm text-slate-500">Redirecting to dashboard…</p>;
}
