"use client";

import { useEffect, useState } from "react";
import { api, AuditData } from "@/lib/api";
import { Search, Shield, ShieldCheck, ShieldAlert, ChevronRight } from "lucide-react";

export default function AuditPage() {
  const [data, setData] = useState<AuditData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getAudit()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-sm text-muted-foreground">{error || "Failed to load audit log"}</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Audit Log</h1>
          <p className="text-sm text-muted-foreground">
            {data.total_events} events · {data.consent_events} consent · {data.rights_events} rights · {data.grievance_events} grievances
          </p>
        </div>
        <div className={`flex items-center gap-2 rounded-md border px-3 py-1.5 text-xs ${
          data.chain_valid ? "border-success/30 bg-success/5 text-success" : "border-destructive/30 bg-destructive/5 text-destructive"
        }`}>
          {data.chain_valid ? <ShieldCheck className="h-3.5 w-3.5" /> : <ShieldAlert className="h-3.5 w-3.5" />}
          {data.chain_valid ? "Chain Verified" : "Chain Broken"}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input type="search" placeholder="Search audit log..." className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground w-8"></th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Hash</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Prev Hash</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Action</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Actor</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border font-mono text-xs">
            {data.audit_entries.map((e, i) => (
              <tr key={i} className="hover:bg-muted/30 transition-colors">
                <td className="px-4 py-3">
                  {e.verified ? (
                    <ShieldCheck className="h-3.5 w-3.5 text-success" />
                  ) : (
                    <ShieldAlert className="h-3.5 w-3.5 text-destructive" />
                  )}
                </td>
                <td className="px-4 py-3">{e.hash_value}</td>
                <td className="px-4 py-3 text-muted-foreground">{e.prev_hash}</td>
                <td className="px-4 py-3">
                  <span className="rounded bg-primary/10 px-1.5 py-0.5 text-primary">{e.action}</span>
                </td>
                <td className="px-4 py-3 text-muted-foreground">{e.actor}</td>
                <td className="px-4 py-3 text-muted-foreground">{e.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="rounded-xl border border-border bg-card p-5">
        <h2 className="text-sm font-medium">Hash Chain Visualizer</h2>
        <div className="mt-4 flex items-center gap-1 overflow-x-auto pb-2">
          {data.audit_entries.map((e, i) => (
            <div key={i} className="flex items-center gap-1 shrink-0">
              <div className={`flex flex-col items-center rounded-md border px-3 py-2 ${
                e.verified ? "border-success/30 bg-success/5" : "border-destructive/30 bg-destructive/5"
              }`}>
                <span className="text-[10px] text-muted-foreground">#{i + 1}</span>
                <span className="text-[10px] font-mono">{e.action.split(".")[1] || e.action}</span>
              </div>
              {i < data.audit_entries.length - 1 && (
                <ChevronRight className="h-3 w-3 text-muted-foreground shrink-0" />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
