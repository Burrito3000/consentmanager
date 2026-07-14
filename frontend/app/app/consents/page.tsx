"use client";

import { useEffect, useState } from "react";
import { api, ConsentsData } from "@/lib/api";
import { Search, Download, CheckCircle, XCircle, Clock } from "lucide-react";

export default function ConsentsPage() {
  const [data, setData] = useState<ConsentsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getConsents()
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
        <div className="text-sm text-muted-foreground">{error || "Failed to load consents"}</div>
      </div>
    );
  }

  const StatusIcon = ({ status }: { status: string }) => {
    if (status === "ACTIVE") return <CheckCircle className="h-3.5 w-3.5 text-success" />;
    if (status === "WITHDRAWN") return <XCircle className="h-3.5 w-3.5 text-destructive" />;
    return <Clock className="h-3.5 w-3.5 text-muted-foreground" />;
  };

  const statusColor = (status: string) => {
    if (status === "ACTIVE") return "text-success";
    if (status === "WITHDRAWN") return "text-destructive";
    return "text-muted-foreground";
  };

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Consent Records</h1>
          <p className="text-sm text-muted-foreground">
            {data.total_consents} total · {data.active_consents} active · {data.withdrawn_consents} withdrawn
            {data.chain_verified && " · Chain Verified"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-sm hover:bg-accent">
            <Download className="h-4 w-4" /> Export
          </button>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="search"
            placeholder="Search by principal, email, or consent ID..."
            className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
        <select className="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
          <option>All Statuses</option>
          <option>ACTIVE</option>
          <option>WITHDRAWN</option>
          <option>EXPIRED</option>
        </select>
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Consent ID</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Principal</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Event</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Timestamp</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Source</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data.consents.map((c) => (
              <tr key={c.consent_id} className="hover:bg-muted/30 transition-colors cursor-pointer">
                <td className="px-4 py-3 text-sm font-mono text-xs">{c.consent_id.slice(0, 12)}</td>
                <td className="px-4 py-3">
                  <div className="text-sm">{c.principal_ref}</div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <StatusIcon status={c.status} />
                    <span className={`text-xs font-medium ${statusColor(c.status)}`}>{c.status}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[11px] text-primary">{c.event_type}</span>
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">{c.timestamp}</td>
                <td className="px-4 py-3 text-sm text-muted-foreground">{c.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
