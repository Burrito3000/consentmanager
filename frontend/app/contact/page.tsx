"use client";

import Link from "next/link";

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-[10px] font-bold text-primary-foreground">CM</div>
            <span className="text-sm font-semibold">Consent Manager</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground">Sign in</Link>
          </div>
        </div>
      </header>

      <section className="border-b border-border py-16">
        <div className="mx-auto max-w-6xl px-4 text-center">
          <h1 className="text-2xl font-bold sm:text-3xl">Get in touch</h1>
          <p className="mx-auto mt-2 max-w-xl text-sm text-muted-foreground">Have questions about DPDP compliance? We&apos;re here to help.</p>
        </div>
      </section>

      <section className="py-16">
        <div className="mx-auto max-w-lg px-4">
          <div className="rounded-xl border border-border bg-card p-6">
            <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1.5 block text-xs font-medium">First name</label>
                  <input type="text" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
                </div>
                <div>
                  <label className="mb-1.5 block text-xs font-medium">Last name</label>
                  <input type="text" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
                </div>
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium">Email</label>
                <input type="email" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium">Message</label>
                <textarea rows={4} className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
              </div>
              <button type="submit" className="h-9 w-full rounded-md bg-primary text-sm font-medium text-primary-foreground hover:bg-primary/90">
                Send message
              </button>
            </form>
          </div>
        </div>
      </section>
    </div>
  );
}
