import Link from "next/link";
import { Shield, Lock, Fingerprint, Eye, Server, Key } from "lucide-react";

const items = [
  { icon: Lock, title: "Encryption at Rest & Transit", desc: "All data encrypted with AES-256 at rest. TLS 1.3 for all data in transit. Encryption keys managed via secure vault." },
  { icon: Fingerprint, title: "Hash-Chained Audit Log", desc: "Every action creates a SHA-256 hashed entry linked to the previous hash. Any tampering breaks the chain — detectable instantly." },
  { icon: Eye, title: "Access Control & RBAC", desc: "Role-based access control with Owner, Admin, DPO, Analyst, and Auditor roles. Granular permissions per resource." },
  { icon: Server, title: "India Data Residency", desc: "All data stored exclusively in India (ap-south-1). No cross-border data transfer. Compliant with DPDP Section 16." },
  { icon: Key, title: "API Security", desc: "Per-tenant API keys with scoped permissions. Short-lived signed tokens. Origin allowlisting for CORS." },
  { icon: Shield, title: "Penetration Testing", desc: "Regular third-party security audits. OWASP ASVS-aligned. Vulnerability disclosure program." },
];

export default function SecurityPage() {
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
          <h1 className="text-2xl font-bold sm:text-3xl">Security & Compliance</h1>
          <p className="mx-auto mt-2 max-w-xl text-sm text-muted-foreground">Your data&apos;s security is our foundation. Built for the highest standards.</p>
        </div>
      </section>

      <section className="py-16">
        <div className="mx-auto max-w-6xl px-4">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((item) => (
              <div key={item.title} className="rounded-xl border border-border bg-card p-5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                  <item.icon className="h-4 w-4 text-primary" />
                </div>
                <h3 className="mt-3 text-sm font-medium">{item.title}</h3>
                <p className="mt-1 text-xs text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
