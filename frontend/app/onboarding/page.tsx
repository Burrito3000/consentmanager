"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, ArrowLeft, Check, Rocket } from "lucide-react";

const steps = [
  { id: "profile", label: "Profile" },
  { id: "domain", label: "Domain" },
  { id: "purposes", label: "Purposes" },
  { id: "done", label: "Launch" },
];

const verticals = ["E-commerce", "Fintech", "Healthtech", "Edtech", "SaaS", "Media", "Other"];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({ name: "", vertical: "", domain: "" });

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-lg">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground">
            CM
          </div>
          <h1 className="text-lg font-semibold">Set up your workspace</h1>
          <p className="mt-1 text-sm text-muted-foreground">Configure your consent management platform</p>
        </div>

        <div className="flex items-center justify-center gap-1 mb-8">
          {steps.map((s, i) => (
            <div key={s.id} className="flex items-center gap-1">
              <div className={`flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-medium transition-colors ${
                i < step ? "bg-primary text-primary-foreground" :
                i === step ? "border-2 border-primary text-primary" :
                "border border-border text-muted-foreground"
              }`}>
                {i < step ? <Check className="h-3 w-3" /> : i + 1}
              </div>
              <span className={`hidden text-xs sm:block ${i === step ? "font-medium" : "text-muted-foreground"}`}>{s.label}</span>
              {i < steps.length - 1 && <div className="mx-1 h-px w-4 bg-border" />}
            </div>
          ))}
        </div>

        <div className="rounded-xl border border-border bg-card p-6">
          {step === 0 && (
            <div className="space-y-4">
              <div>
                <label className="mb-1.5 block text-xs font-medium">Organization name</label>
                <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="Acme Corp" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium">Industry</label>
                <select value={form.vertical} onChange={(e) => setForm({ ...form, vertical: e.target.value })}
                  className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
                  <option value="">Select...</option>
                  {verticals.map((v) => <option key={v} value={v.toLowerCase()}>{v}</option>)}
                </select>
              </div>
            </div>
          )}
          {step === 1 && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">Register your website domain for SDK embedding. You can add more later.</p>
              <div>
                <label className="mb-1.5 block text-xs font-medium">Domain</label>
                <input type="text" value={form.domain} onChange={(e) => setForm({ ...form, domain: e.target.value })}
                  placeholder="example.com" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
              </div>
            </div>
          )}
          {step === 2 && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">We&apos;ll create starter purposes:</p>
              {["Essential Functionality (mandatory)", "Analytics & Performance", "Marketing & Personalization"].map((p) => (
                <div key={p} className="flex items-center gap-3 rounded-md border border-border px-3 py-2">
                  <div className="h-2 w-2 rounded-full bg-primary" />
                  <span className="text-sm">{p}</span>
                </div>
              ))}
            </div>
          )}
          {step === 3 && (
            <div className="text-center space-y-4">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <Rocket className="h-6 w-6 text-primary" />
              </div>
              <h2 className="text-base font-semibold">You&apos;re all set!</h2>
              <p className="text-sm text-muted-foreground">Your workspace is ready. Next steps: define purposes, embed the SDK, and capture your first consent.</p>
            </div>
          )}
        </div>

        <div className="mt-4 flex items-center justify-between">
          <button onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0}
            className="flex items-center gap-1 rounded-md px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent disabled:opacity-30">
            <ArrowLeft className="h-4 w-4" /> Back
          </button>
          {step < steps.length - 1 ? (
            <button onClick={() => setStep(step + 1)}
              className="flex items-center gap-1 rounded-md bg-primary px-4 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90">
              Continue <ArrowRight className="h-4 w-4" />
            </button>
          ) : (
            <button onClick={() => router.push("/app/dashboard")}
              className="rounded-md bg-primary px-4 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90">
              Go to Dashboard
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
