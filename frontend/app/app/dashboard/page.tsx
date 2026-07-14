"use client";

import { useEffect, useState } from "react";
import { api, DashboardData } from "@/lib/api";
import { CheckCircle2, Clock, AlertTriangle, TrendingUp, Scale, Shield } from "lucide-react";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getDashboard()
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
        <div className="text-sm text-muted-foreground">{error || "Failed to load dashboard"}</div>
      </div>
    );
  }

  const stats = [
    { label: "Active Consents", value: data.active_consents.toLocaleString(), change: `${data.active_pct}% of total`, icon: CheckCircle2, color: "text-success" },
    { label: "Withdrawn", value: data.withdrawn_consents.toLocaleString(), change: `${data.withdrawn_pct}% of total`, icon: TrendingUp, color: "text-primary" },
    { label: "Open Rights Requests", value: data.pending_rights.toString(), change: `${data.sla_breached} SLA breach`, icon: Scale, color: "text-warning" },
    { label: "Total Consents", value: data.total_consents.toLocaleString(), change: data.consent_change, icon: AlertTriangle, color: "text-muted-foreground" },
  ];

  const slaAlerts = data.recent_events.slice(0, 3).map((e) => ({
    type: e.action.replace("CONSENT_", "").replace("_", " "),
    ref: e.actor,
    principal: e.actor,
    due: e.timestamp,
    severity: "info" as const,
  }));

  const recentEvents = data.recent_events.slice(0, 4);

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Dashboard</h1>
          <p className="text-sm text-muted-foreground">Real-time overview of your consent platform</p>
        </div>
        <div className="flex items-center gap-2 rounded-md border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground">
          <Clock className="h-3 w-3" />
          Languages: {data.languages.length}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => (
          <div key={s.label} className="rounded-xl border border-border bg-card p-4 card-hover hover:shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted-foreground">{s.label}</p>
              <s.icon className={`h-4 w-4 ${s.color}`} />
            </div>
            <p className="mt-2 text-2xl font-semibold">{s.value}</p>
            <p className="mt-1 text-xs text-muted-foreground">{s.change}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-xl border border-border bg-card p-5 lg:col-span-2">
          <h2 className="text-sm font-medium">Purpose Adoption Rates</h2>
          <div className="mt-4 space-y-3">
            {data.purpose_stats.length > 0 ? data.purpose_stats.map((p) => (
              <div key={p.name}>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span>{p.name}</span>
                  <span className="text-muted-foreground">{p.pct}%</span>
                </div>
                <div className="h-2 rounded-full bg-muted">
                  <div className="h-2 rounded-full bg-primary" style={{ width: `${p.pct}%` }} />
                </div>
              </div>
            )) : <p className="text-xs text-muted-foreground">No purpose data yet</p>}
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium">SLA Alerts</h2>
            <AlertTriangle className="h-4 w-4 text-warning" />
          </div>
          <div className="mt-4 space-y-3">
            {slaAlerts.length > 0 ? slaAlerts.map((a, i) => (
              <div key={i} className="flex items-start gap-2 rounded-md border border-border p-2.5">
                <div className={`mt-0.5 h-2 w-2 rounded-full ${
                  a.severity === "info" ? "bg-muted-foreground" : "bg-destructive"
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium">{a.type}</p>
                  <p className="text-xs text-muted-foreground truncate">{a.ref}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{a.due}</p>
                </div>
              </div>
            )) : <p className="text-xs text-muted-foreground">No SLA alerts</p>}
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-medium">Recent Activity</h2>
          <button className="text-xs text-primary hover:underline">View all</button>
        </div>
        <div className="divide-y divide-border">
          {recentEvents.length > 0 ? recentEvents.map((e, i) => (
            <div key={i} className="flex items-center justify-between py-2.5">
              <div className="flex items-center gap-3">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10">
                  <Shield className="h-3.5 w-3.5 text-primary" />
                </div>
                <div>
                  <p className="text-sm">{e.action}</p>
                  <p className="text-xs text-muted-foreground">{e.actor}</p>
                </div>
              </div>
              <span className="text-xs text-muted-foreground">{e.timestamp}</span>
            </div>
          )) : <p className="text-xs text-muted-foreground py-2">No recent activity</p>}
        </div>
      </div>
    </div>
  );
}
