"use client";

import { useEffect, useState } from "react";
import { api, RightsData } from "@/lib/api";
import { Search, CheckCircle, XCircle, Clock, AlertTriangle, Scale } from "lucide-react";

export default function RightsPage() {
  const [data, setData] = useState<RightsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getRights()
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
        <div className="text-sm text-muted-foreground">{error || "Failed to load rights & grievances"}</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Rights Requests &amp; Grievances</h1>
          <p className="text-sm text-muted-foreground">
            {data.total_requests} requests · {data.total_grievances} grievances
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input type="search" placeholder="Search by ID or principal..." className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-medium">Rights Requests</h2>
            <span className="text-xs text-muted-foreground">{data.pending_requests} pending · {data.resolved_requests} resolved</span>
          </div>
          <div className="divide-y divide-border">
            {data.rights_requests.length > 0 ? data.rights_requests.map((r) => (
              <div key={r.id} className="flex items-center justify-between py-2.5">
                <div className="flex items-center gap-3">
                  <Scale className={`h-4 w-4 ${r.is_breached ? "text-destructive" : "text-muted-foreground"}`} />
                  <div>
                    <p className="text-sm font-medium">{r.request_type}</p>
                    <p className="text-xs text-muted-foreground">{r.id} · {r.principal_ref}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs ${r.is_breached ? "text-destructive font-medium" : "text-muted-foreground"}`}>
                    {r.days_left}
                  </span>
                  <span className={`rounded-full px-2 py-0.5 text-[11px] ${
                    r.status === "RESOLVED" || r.status === "REJECTED" ? "bg-success/10 text-success" :
                    r.status === "IN_PROGRESS" ? "bg-primary/10 text-primary" :
                    "bg-warning/10 text-warning"
                  }`}>{r.status}</span>
                </div>
              </div>
            )) : <p className="text-xs text-muted-foreground py-2">No rights requests</p>}
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-medium">Grievances</h2>
            <span className="text-xs text-muted-foreground">{data.open_grievances} open · {data.resolved_grievances} resolved</span>
          </div>
          <div className="divide-y divide-border">
            {data.grievances.length > 0 ? data.grievances.map((g) => (
              <div key={g.id} className="flex items-center justify-between py-2.5">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="h-4 w-4 text-warning" />
                  <div>
                    <p className="text-sm font-medium">{g.subject}</p>
                    <p className="text-xs text-muted-foreground">{g.id} · {g.principal_ref}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">{g.sla_text}</span>
                  <span className={`rounded-full px-2 py-0.5 text-[11px] ${
                    g.status === "RESOLVED" || g.status === "REJECTED" ? "bg-success/10 text-success" :
                    g.status === "INVESTIGATING" ? "bg-primary/10 text-primary" :
                    "bg-warning/10 text-warning"
                  }`}>{g.status}</span>
                </div>
              </div>
            )) : <p className="text-xs text-muted-foreground py-2">No grievances</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
