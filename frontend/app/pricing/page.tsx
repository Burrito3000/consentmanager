import Link from "next/link";
import { Check } from "lucide-react";

const plans = [
  { name: "Starter", price: "Free", desc: "For small businesses exploring DPDP compliance", features: ["Up to 1,000 consents/month", "3 purposes", "2 team members", "Email support", "Basic SDK embed"], cta: "Start free" },
  { name: "Growth", price: "₹49,999/yr", desc: "For growing companies needing full compliance", features: ["Up to 50,000 consents/month", "20 purposes", "10 team members", "Priority support", "All SDK features", "API access", "Webhooks", "Analytics dashboard"], cta: "Start trial", popular: true },
  { name: "Enterprise", price: "Custom", desc: "For large organizations with custom needs", features: ["Unlimited consents", "Unlimited purposes", "Unlimited team members", "Dedicated support", "Custom SLA terms", "On-premise option", "SAML/SSO", "Dedicated instance"], cta: "Contact sales" },
];

export default function PricingPage() {
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
          <h1 className="text-2xl font-bold sm:text-3xl">Simple, transparent pricing</h1>
          <p className="mx-auto mt-2 max-w-xl text-sm text-muted-foreground">Start free. Upgrade as you grow.</p>
        </div>
      </section>

      <section className="py-16">
        <div className="mx-auto max-w-5xl px-4">
          <div className="grid gap-6 md:grid-cols-3">
            {plans.map((plan) => (
              <div key={plan.name} className={`rounded-xl border p-6 ${plan.popular ? "border-primary shadow-sm" : "border-border bg-card"}`}>
                {plan.popular && <div className="mb-3 inline-block rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">Most Popular</div>}
                <h3 className="text-base font-semibold">{plan.name}</h3>
                <p className="mt-1 text-2xl font-bold">{plan.price}</p>
                <p className="mt-1 text-xs text-muted-foreground">{plan.desc}</p>
                <ul className="mt-4 space-y-2">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-xs"><Check className="h-3.5 w-3.5 text-success shrink-0" /> {f}</li>
                  ))}
                </ul>
                <Link href="/signup" className={`mt-6 flex w-full items-center justify-center rounded-md py-1.5 text-sm font-medium ${
                  plan.popular ? "bg-primary text-primary-foreground" : "border border-border hover:bg-accent"
                }`}>{plan.cta}</Link>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
