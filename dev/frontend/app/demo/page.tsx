"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslation } from "@/lib/i18n/useTranslation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8005/v1";

export default function DemoPage() {
  const router = useRouter();
  const { t } = useTranslation();
  const [status, setStatus] = useState(t.demo.preparing);

  useEffect(() => {
    async function startDemo() {
      try {
        setStatus(t.demo.signing_in);
        const res = await fetch(`${API_URL}/auth/demo`, { method: "POST" });
        const json = await res.json();
        if (!json.success) throw new Error(json.error ?? "Demo login failed");
        localStorage.setItem("access_token", json.data.access_token);
        setStatus(t.demo.redirecting);
        router.push("/search");
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setStatus(`${t.common.error}: ${msg}`);
      }
    }
    startDemo();
  }, [router, t]);

  return (
    <div className="min-h-screen bg-bg-dark flex items-center justify-center">
      <div className="text-center">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-4">
          <span className="text-white text-sm font-bold">LP</span>
        </div>
        <p className="text-text-secondary text-sm">{status}</p>
        {!status.startsWith(t.common.error) && (
          <div className="mt-3 w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
        )}
      </div>
    </div>
  );
}
