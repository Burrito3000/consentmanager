"use client";

import { Plus, Webhook, RefreshCw, CheckCircle, XCircle } from "lucide-react";

const webhooksList = [
  { id: 1, url: "https://api.example.com/webhooks/cmp", events: ["consent.granted", "consent.withdrawn"], active: true, lastDelivery: "2024-12-12 14:23" },
  { id: 2, url: "https://hooks.company.com/cmp-events", events: ["consent.*", "rights.*"], active: true, lastDelivery: "2024-12-12 10:15" },
  { id: 3, url: "https://webhook.site/old-endpoint", events: ["consent.granted"], active: false, lastDelivery: "2024-11-20" },
];

const recentDeliveries = [
  { id: "del_001", webhook: "api.example.com", event: "consent.granted", status: "delivered", attempts: 1, time: "2 min ago" },
  { id: "del_002", webhook: "hooks.company.com", event: "consent.withdrawn", status: "delivered", attempts: 1, time: "15 min ago" },
  { id: "del_003", webhook: "api.example.com", event: "rights.created", status: "failed", attempts: 3, time: "1 hour ago" },
  { id: "del_004", webhook: "hooks.company.com", event: "consent.modified", status: "delivered", attempts: 2, time: "3 hours ago" },
];

export default function WebhooksPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Webhooks</h1>
          <p className="text-sm text-muted-foreground">Receive real-time notifications when consent events occur</p>
        </div>
        <button className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          <Plus className="h-4 w-4" /> Add Webhook
        </button>
      </div>

      <div className="space-y-3">
        {webhooksList.map((w) => (
          <div key={w.id} className={`rounded-xl border p-4 ${w.active ? "border-border bg-card" : "border-dashed border-border/60 bg-muted/30"}`}>
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${w.active ? "bg-primary/10" : "bg-muted"}`}>
                  <Webhook className={`h-4 w-4 ${w.active ? "text-primary" : "text-muted-foreground"}`} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <code className="text-sm">{w.url}</code>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                      w.active ? "bg-success/10 text-success" : "bg-muted text-muted-foreground"
                    }`}>{w.active ? "Active" : "Disabled"}</span>
                  </div>
                  <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                    {w.events.map((ev) => (
                      <span key={ev} className="rounded bg-secondary px-1.5 py-0.5">{ev}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-border bg-card p-5">
        <h2 className="text-sm font-medium">Recent Deliveries</h2>
        <div className="mt-4 divide-y divide-border">
          {recentDeliveries.map((d) => (
            <div key={d.id} className="flex items-center justify-between py-2.5">
              <div className="flex items-center gap-3">
                {d.status === "delivered" ? (
                  <CheckCircle className="h-4 w-4 text-success" />
                ) : (
                  <XCircle className="h-4 w-4 text-destructive" />
                )}
                <div>
                  <p className="text-xs font-medium">{d.event}</p>
                  <p className="text-xs text-muted-foreground">{d.webhook} · {d.attempts} attempt{d.attempts > 1 ? "s" : ""}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">{d.time}</span>
                {d.status === "failed" && (
                  <button className="flex items-center gap-1 text-xs text-primary hover:underline">
                    <RefreshCw className="h-3 w-3" /> Retry
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
