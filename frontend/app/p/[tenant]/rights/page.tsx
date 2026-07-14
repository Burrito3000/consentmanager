"use client";

import { useState, use } from "react";
import Link from "next/link";

const requestTypes = [
  { id: "access", title: "Access my data", desc: "Get a copy of all personal data you've shared with us." },
  { id: "correction", title: "Correct my data", desc: "Update inaccurate or incomplete personal information." },
  { id: "erasure", title: "Erase my data", desc: "Request deletion of your personal data from our systems." },
  { id: "withdraw", title: "Withdraw consent", desc: "Withdraw consent for specific processing purposes." },
  { id: "nominee", title: "Nominate a representative", desc: "Designate someone to manage your data on your behalf." },
];

export default function RightsPage({ params }: { params: Promise<{ tenant: string }> }) {
  const { tenant } = use(params);
  const [selected, setSelected] = useState("");
  const [submitted, setSubmitted] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-4">
          <Link href={`/p/${tenant}/preferences`} className="text-sm text-muted-foreground hover:text-foreground">
            ← Preferences
          </Link>
          <span className="text-sm font-semibold">Data Principal Rights</span>
          <Link href={`/p/${tenant}/grievance`} className="text-sm text-muted-foreground hover:text-foreground">
            Grievance →
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8">
        {!submitted ? (
          <>
            <h1 className="text-lg font-semibold">Exercise Your Rights</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Under the DPDP Act 2023, you have the right to access, correct, erase, and manage your personal data.
            </p>

            <div className="mt-6 space-y-2">
              {requestTypes.map((r) => (
                <button
                  key={r.id}
                  onClick={() => setSelected(r.id)}
                  className={`w-full rounded-xl border p-4 text-left transition-colors ${
                    selected === r.id
                      ? "border-primary bg-primary/5"
                      : "border-border bg-card hover:bg-accent"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`flex h-5 w-5 items-center justify-center rounded-full border-2 ${
                      selected === r.id ? "border-primary" : "border-muted-foreground"
                    }`}>
                      {selected === r.id && <div className="h-2.5 w-2.5 rounded-full bg-primary" />}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{r.title}</p>
                      <p className="text-xs text-muted-foreground">{r.desc}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>

            <div className="mt-6 space-y-4">
              <div>
                <label className="mb-1.5 block text-xs font-medium">Email address</label>
                <input type="email" placeholder="your@email.com" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium">Additional details</label>
                <textarea rows={3} placeholder="Describe your request..." className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
              </div>
              <button onClick={() => setSubmitted(true)} disabled={!selected}
                className="h-9 w-full rounded-md bg-primary text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
                Submit Request
              </button>
            </div>
          </>
        ) : (
          <div className="text-center py-12">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-success/10">
              <svg className="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
            </div>
            <h2 className="text-base font-semibold">Request Submitted</h2>
            <p className="mt-1 text-sm text-muted-foreground">We&apos;ll process your request within 90 days as per DPDP Act guidelines.</p>
            <Link href={`/p/${tenant}/preferences`} className="mt-4 inline-block text-sm text-primary hover:underline">
              Back to preferences
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}
