import Link from "next/link";
import { Shield, Target, FileText, CheckSquare, Users, Scale, AlertTriangle, BarChart3, Puzzle, Webhook, Lock, Baby } from "lucide-react";

const features = [
  { icon: Target, title: "Purpose Management", desc: "Define granular processing purposes with data categories, lawful basis, retention periods, and consent requirements." },
  { icon: FileText, title: "Multilingual Notices", desc: "Versioned privacy notices in all 22 Eighth Schedule languages. Live preview per locale. Freeze on publish." },
  { icon: CheckSquare, title: "Consent Capture Engine", desc: "Explicit, per-purpose consent with append-only event log. Grant, modify, withdraw, or expire with full timeline." },
  { icon: Shield, title: "Consent Receipts", desc: "Signed, verifiable receipts for every consent action. Downloadable as PDF or JSON for audit evidence." },
  { icon: Users, title: "Data Principal Portal", desc: "Self-service preference center where users can view, modify, or withdraw consent at any time." },
  { icon: Scale, title: "Rights Request Management", desc: "Handle access, correction, erasure, and withdrawal requests. SLA tracking with amber/red alerts." },
  { icon: AlertTriangle, title: "Grievance Redressal", desc: "Full grievance lifecycle with SLA countdown, assignee tracking, response templates, and DPB escalation." },
  { icon: BarChart3, title: "Analytics & Reporting", desc: "Real-time consent metrics, opt-in rates per purpose, SLA compliance dashboards, and exportable reports." },
  { icon: Puzzle, title: "Embeddable SDK", desc: "One-line script embed with branded consent banner, preference center, Accept All/Reject All, and language selection." },
  { icon: Webhook, title: "Webhooks & Events", desc: "Real-time event notifications on grant, modify, withdraw, expire. Signed payloads with retry + delivery log." },
  { icon: Lock, title: "Audit Hash Chain", desc: "Every action logged immutably with SHA-256 hash chain. One-click chain verification for auditors." },
  { icon: Baby, title: "Children's Data", desc: "Age-gating workflow with verifiable parental/guardian consent flow. Behavioral tracking blocked for minors." },
];

export default function FeaturesPage() {
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
            <Link href="/signup" className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90">Get Started</Link>
          </div>
        </div>
      </header>

      <section className="border-b border-border py-16">
        <div className="mx-auto max-w-6xl px-4 text-center">
          <h1 className="text-2xl font-bold sm:text-3xl">Everything you need for DPDP compliance</h1>
          <p className="mx-auto mt-2 max-w-xl text-sm text-muted-foreground">
            From consent capture to audit trails — every feature is designed for the Digital Personal Data Protection Act 2023.
          </p>
        </div>
      </section>

      <section className="py-16">
        <div className="mx-auto max-w-6xl px-4">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => (
              <div key={f.title} className="rounded-xl border border-border bg-card p-4 card-hover hover:shadow-sm">
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
    </div>
  );
}
