"use client";

import { useState, use } from "react";
import Link from "next/link";

export default function GrievancePage({ params }: { params: Promise<{ tenant: string }> }) {
  const { tenant } = use(params);
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-4">
          <Link href={`/p/${tenant}/rights`} className="text-sm text-muted-foreground hover:text-foreground">
            ← My Rights
          </Link>
          <span className="text-sm font-semibold">File a Grievance</span>
          <Link href={`/p/${tenant}/preferences`} className="text-sm text-muted-foreground hover:text-foreground">
            Preferences
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8">
        {!submitted ? (
          <>
            <h1 className="text-lg font-semibold">File a Grievance</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              If you&apos;re not satisfied with how your data has been handled, you can file a complaint with our Grievance Officer.
            </p>

            <div className="mt-6 rounded-xl border border-border bg-card p-4 text-xs text-muted-foreground">
              <p className="font-medium text-foreground">Grievance Officer</p>
              <p className="mt-1">Name: Priya Sharma</p>
              <p>Email: grievance@acmecorp.com</p>
              <p>Response time: Within 3 business days</p>
            </div>

            <form className="mt-6 space-y-4" onSubmit={(e) => { e.preventDefault(); setSubmitted(true); }}>
              <div>
                <label className="mb-1.5 block text-xs font-medium">Your email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com" required
                  className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium">Subject</label>
                <input type="text" value={subject} onChange={(e) => setSubject(e.target.value)}
                  placeholder="Brief summary of your complaint" required
                  className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium">Description</label>
                <textarea rows={5} value={description} onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe your grievance in detail..." required
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
              </div>
              <button type="submit"
                className="h-9 w-full rounded-md bg-primary text-sm font-medium text-primary-foreground hover:bg-primary/90">
                Submit Grievance
              </button>
            </form>
          </>
        ) : (
          <div className="text-center py-12">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-success/10">
              <svg className="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
            </div>
            <h2 className="text-base font-semibold">Grievance Submitted</h2>
            <p className="mt-1 text-sm text-muted-foreground">We&apos;ll respond within 3 business days. You can track the status in your account.</p>
            <Link href={`/p/${tenant}/preferences`} className="mt-4 inline-block text-sm text-primary hover:underline">
              Back to preferences
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}
