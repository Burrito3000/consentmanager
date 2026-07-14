"use client";

import { CreditCard, Check, Download } from "lucide-react";

const plans = [
  { name: "Starter", price: "Free", consents: "Up to 1,000", purposes: 3, users: 2, support: "Email", popular: false },
  { name: "Growth", price: "₹49,999/yr", consents: "Up to 50,000", purposes: 20, users: 10, support: "Priority", popular: true },
  { name: "Enterprise", price: "Custom", consents: "Unlimited", purposes: "Unlimited", users: "Unlimited", support: "Dedicated", popular: false },
];

const invoices = [
  { id: "INV-2024-001", date: "Dec 1, 2024", amount: "₹49,999", status: "Paid" },
  { id: "INV-2024-002", date: "Nov 1, 2024", amount: "₹49,999", status: "Paid" },
  { id: "INV-2024-003", date: "Oct 1, 2024", amount: "₹49,999", status: "Paid" },
];

export default function BillingPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Billing</h1>
        <p className="text-sm text-muted-foreground">Subscription plan, usage, and invoices</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {plans.map((plan) => (
          <div key={plan.name} className={`rounded-xl border p-5 ${
            plan.popular ? "border-primary bg-card shadow-sm" : "border-border bg-card"
          }`}>
            {plan.popular && (
              <div className="mb-3 inline-block rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">
                Most Popular
              </div>
            )}
            <h3 className="text-base font-semibold">{plan.name}</h3>
            <p className="mt-1 text-2xl font-bold">{plan.price}</p>
            <ul className="mt-4 space-y-2">
              <li className="flex items-center gap-2 text-xs"><Check className="h-3.5 w-3.5 text-success" /> {plan.consents} consents</li>
              <li className="flex items-center gap-2 text-xs"><Check className="h-3.5 w-3.5 text-success" /> {plan.purposes} purposes</li>
              <li className="flex items-center gap-2 text-xs"><Check className="h-3.5 w-3.5 text-success" /> {plan.users} users</li>
              <li className="flex items-center gap-2 text-xs"><Check className="h-3.5 w-3.5 text-success" /> {plan.support} support</li>
            </ul>
            <button className={`mt-6 w-full rounded-md py-1.5 text-sm font-medium ${
              plan.popular ? "bg-primary text-primary-foreground" : "border border-border hover:bg-accent"
            }`}>
              {plan.name === "Enterprise" ? "Contact Sales" : plan.name === "Starter" ? "Current Plan" : "Upgrade"}
            </button>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-border bg-card p-5">
        <h2 className="text-sm font-medium">Invoice History</h2>
        <div className="mt-4 divide-y divide-border">
          {invoices.map((inv) => (
            <div key={inv.id} className="flex items-center justify-between py-2.5">
              <div>
                <p className="text-sm">{inv.id}</p>
                <p className="text-xs text-muted-foreground">{inv.date}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium">{inv.amount}</span>
                <span className="rounded-full bg-success/10 px-2 py-0.5 text-[10px] text-success">{inv.status}</span>
                <button className="rounded-md p-1 text-muted-foreground hover:bg-accent">
                  <Download className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
