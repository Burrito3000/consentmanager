"use client";

import { use } from "react";
import Link from "next/link";
import { CheckCircle, XCircle, Download } from "lucide-react";

const consents = [
  { id: "CN-2024-001", date: "2024-12-01", purposes: ["Marketing", "Analytics"], status: "Active", channel: "Website" },
  { id: "CN-2024-002", date: "2024-11-28", purposes: ["Essential"], status: "Active", channel: "Website" },
  { id: "CN-2024-003", date: "2024-10-15", purposes: ["Marketing", "Analytics", "Essential"], status: "Withdrawn", channel: "Mobile App" },
];

export default function MyConsentsPage({ params }: { params: Promise<{ tenant: string }> }) {
  const { tenant } = use(params);
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-4">
          <Link href={`/p/${tenant}/preferences`} className="text-sm text-muted-foreground hover:text-foreground">
            ← Preferences
          </Link>
          <span className="text-sm font-semibold">My Consents</span>
          <Link href={`/p/${tenant}/rights`} className="text-sm text-muted-foreground hover:text-foreground">
            My Rights →
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-lg font-semibold">My Consent Records</h1>
        <p className="mt-1 text-sm text-muted-foreground">View and download your consent receipts</p>

        <div className="mt-6 space-y-3">
          {consents.map((c) => (
            <div key={c.id} className="rounded-xl border border-border bg-card p-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    {c.status === "Active" ? (
                      <CheckCircle className="h-4 w-4 text-success" />
                    ) : (
                      <XCircle className="h-4 w-4 text-destructive" />
                    )}
                    <span className="text-sm font-medium">{c.id}</span>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                      c.status === "Active" ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive"
                    }`}>{c.status}</span>
                  </div>
                  <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
                    <span>Granted: {c.date}</span>
                    <span>Channel: {c.channel}</span>
                  </div>
                  <div className="mt-2 flex gap-1">
                    {c.purposes.map((p) => (
                      <span key={p} className="rounded-full bg-secondary px-2 py-0.5 text-[11px]">{p}</span>
                    ))}
                  </div>
                </div>
                <button className="rounded-md p-1.5 text-muted-foreground hover:bg-accent">
                  <Download className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
