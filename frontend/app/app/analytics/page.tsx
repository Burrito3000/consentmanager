"use client";

import { TrendingUp, TrendingDown, Download } from "lucide-react";

const metrics = [
  { label: "Consent Rate", value: "68.2%", change: "+5.3%", trend: "up" },
  { label: "Avg. Purposes per User", value: "2.4", change: "+0.3", trend: "up" },
  { label: "Withdrawal Rate", value: "12.1%", change: "-2.1%", trend: "down" },
  { label: "SLA Compliance", value: "94.7%", change: "+1.2%", trend: "up" },
];

const weeklyData = [
  { day: "Mon", grants: 142, withdrawals: 12 },
  { day: "Tue", grants: 158, withdrawals: 8 },
  { day: "Wed", grants: 135, withdrawals: 15 },
  { day: "Thu", grants: 189, withdrawals: 10 },
  { day: "Fri", grants: 201, withdrawals: 18 },
  { day: "Sat", grants: 98, withdrawals: 5 },
  { day: "Sun", grants: 76, withdrawals: 3 },
];

const maxGrants = Math.max(...weeklyData.map((d) => d.grants));

export default function AnalyticsPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Analytics</h1>
          <p className="text-sm text-muted-foreground">Consent metrics, opt-in rates, and compliance reporting</p>
        </div>
        <button className="flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-sm hover:bg-accent">
          <Download className="h-4 w-4" /> Export Report
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((m) => (
          <div key={m.label} className="rounded-xl border border-border bg-card p-4">
            <p className="text-xs text-muted-foreground">{m.label}</p>
            <p className="mt-1 text-2xl font-semibold">{m.value}</p>
            <div className={`mt-1 flex items-center gap-1 text-xs ${
              m.trend === "up" ? "text-success" : "text-destructive"
            }`}>
              {m.trend === "up" ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              {m.change} vs last period
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-5">
          <h2 className="text-sm font-medium mb-4">Weekly Consent Activity</h2>
          <div className="flex items-end gap-2 h-32">
            {weeklyData.map((d) => (
              <div key={d.day} className="flex flex-1 flex-col items-center gap-1">
                <div className="w-full flex flex-col items-center gap-0.5">
                  <div className="w-full bg-primary/20 rounded-t" style={{ height: `${(d.withdrawals / maxGrants) * 100}%` }} />
                  <div className="w-full bg-primary rounded-t" style={{ height: `${(d.grants / maxGrants) * 100}%` }} />
                </div>
                <span className="text-[10px] text-muted-foreground">{d.day}</span>
              </div>
            ))}
          </div>
          <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1"><span className="h-2 w-2 rounded bg-primary" /> Grants</span>
            <span className="flex items-center gap-1"><span className="h-2 w-2 rounded bg-primary/20" /> Withdrawals</span>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-5">
          <h2 className="text-sm font-medium mb-4">Purpose Opt-in Rates</h2>
          <div className="space-y-3">
            {[
              { name: "Essential Functionality", rate: 98 },
              { name: "Analytics & Performance", rate: 72 },
              { name: "Marketing & Personalization", rate: 45 },
              { name: "Third-party Sharing", rate: 28 },
            ].map((p) => (
              <div key={p.name}>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span>{p.name}</span>
                  <span className="text-muted-foreground">{p.rate}%</span>
                </div>
                <div className="h-2 rounded-full bg-muted">
                  <div
                    className="h-2 rounded-full bg-primary transition-all"
                    style={{ width: `${p.rate}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card p-5">
        <h2 className="text-sm font-medium mb-4">Rights & Grievance SLA Health</h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          {[
            { label: "On Time", value: 42, color: "text-success" },
            { label: "At Risk", value: 8, color: "text-warning" },
            { label: "Breached", value: 3, color: "text-destructive" },
          ].map((s) => (
            <div key={s.label}>
              <p className={`text-2xl font-semibold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-muted-foreground">{s.label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
