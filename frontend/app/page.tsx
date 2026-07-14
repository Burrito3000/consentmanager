import Link from "next/link";
import { CheckCircle, Shield, Scale, FileText, ArrowRight, Menu } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-[10px] font-bold text-primary-foreground">CM</div>
            <span className="text-sm font-semibold">Consent Manager</span>
          </div>
          <nav className="hidden items-center gap-6 md:flex">
            <Link href="/features" className="text-sm text-muted-foreground hover:text-foreground">Features</Link>
            <Link href="/pricing" className="text-sm text-muted-foreground hover:text-foreground">Pricing</Link>
            <Link href="/security" className="text-sm text-muted-foreground hover:text-foreground">Security</Link>
            <Link href="/contact" className="text-sm text-muted-foreground hover:text-foreground">Contact</Link>
          </nav>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground">Sign in</Link>
            <Link href="/signup" className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90">Get Started</Link>
            <button className="rounded-md p-1.5 text-muted-foreground md:hidden"><Menu className="h-5 w-5" /></button>
          </div>
        </div>
      </header>

      <section className="border-b border-border">
        <div className="mx-auto max-w-6xl px-4 py-20 text-center">
          <div className="mx-auto mb-4 inline-block rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
            DPDP Act 2023 Compliance
          </div>
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
            Consent management for<br />India&apos;s data protection era
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-sm text-muted-foreground">
            The enterprise-grade platform to capture, manage, and audit consent across your entire digital ecosystem — built for the DPDP Act 2023.
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Link href="/signup" className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
              Start free trial <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/features" className="rounded-md border border-border px-4 py-2 text-sm font-medium hover:bg-accent">
              See features
            </Link>
          </div>
        </div>
      </section>

      <section className="border-b border-border py-16">
        <div className="mx-auto max-w-6xl px-4">
          <div className="grid gap-8 md:grid-cols-3">
            {[
              { icon: CheckCircle, title: "Per-Purpose Consent", desc: "Granular, explicit consent for each purpose. No bundled consent. Full withdrawal support." },
              { icon: Shield, title: "Tamper-Evident Audit", desc: "Hash-chained audit log for every action. Chain verification with one click." },
              { icon: Scale, title: "DPDP Compliant by Default", desc: "Built for Schedule I requirements. Age-gating, grievance redressal, SLA tracking." },
            ].map((f) => (
              <div key={f.title} className="rounded-xl border border-border bg-card p-5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                  <f.icon className="h-4 w-4 text-primary" />
                </div>
                <h3 className="mt-3 text-sm font-medium">{f.title}</h3>
                <p className="mt-1 text-xs text-muted-foreground">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-b border-border py-16">
        <div className="mx-auto max-w-6xl px-4">
          <div className="flex flex-col items-center gap-8 md:flex-row">
            <div className="flex-1">
              <h2 className="text-xl font-semibold">One-line SDK embed</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Add a single script tag to your website. The SDK automatically renders a branded consent banner, preference center, and language selector.
              </p>
              <div className="mt-4 rounded-md bg-muted p-3 font-mono text-xs">
                <code>{`<script src="https://cdn.cmp.local/sdk/cmp.js" data-tenant-key="pk_..."></script>`}</code>
              </div>
            </div>
            <div className="flex-1">
              <div className="rounded-xl border border-border bg-card p-5">
                <div className="flex items-center gap-2">
                  <div className="flex h-2 w-2 rounded-full bg-success" />
                  <span className="text-xs font-medium">Consent Preference Center</span>
                </div>
                <div className="mt-3 space-y-2">
                  {["Essential Functionality", "Analytics & Performance", "Marketing & Personalization"].map((p) => (
                    <div key={p} className="flex items-center justify-between rounded-md border border-border px-3 py-2">
                      <span className="text-xs">{p}</span>
                      <div className={`h-4 w-8 rounded-full ${p === "Essential Functionality" ? "bg-primary" : "bg-muted"} relative`}>
                        <div className={`absolute top-0.5 h-3 w-3 rounded-full bg-white shadow-sm ${p === "Essential Functionality" ? "right-0.5" : "left-0.5"}`} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-border py-12">
        <div className="mx-auto max-w-6xl px-4">
          <div className="grid grid-cols-2 gap-4 text-center md:grid-cols-4">
            {[
              { value: "10M+", label: "Consents managed" },
              { value: "99.9%", label: "Uptime SLA" },
              { value: "22", label: "Languages supported" },
              { value: "1M+", label: "Rights processed" },
            ].map((s) => (
              <div key={s.label}>
                <p className="text-2xl font-bold">{s.value}</p>
                <p className="text-xs text-muted-foreground">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-12">
        <div className="mx-auto max-w-6xl px-4 text-center">
          <h2 className="text-lg font-semibold">Built for the DPDP Act 2023</h2>
          <p className="mt-1 text-sm text-muted-foreground">Every feature maps to a specific regulatory requirement</p>
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {["Per-purpose consent", "Notice in 22 languages", "Grievance redressal", "72-hr breach notification", "Rights requests with SLA", "Data retention policies", "Age verification", "Audit hash chain", "Consent receipts", "Processor mapping"].map((tag) => (
              <span key={tag} className="rounded-full bg-secondary px-3 py-1 text-xs text-secondary-foreground">{tag}</span>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-border py-8">
        <div className="mx-auto max-w-6xl px-4 text-center text-xs text-muted-foreground">
          <p>Built for compliance with the Digital Personal Data Protection Act 2023.</p>
          <p className="mt-1">Not legal advice. Consult your legal team for full compliance.</p>
        </div>
      </footer>
    </div>
  );
}
