"use client";

import { useState, use } from "react";
import Link from "next/link";

const purposes = [
  { id: "essential", name: "Essential Functionality", desc: "Authentication, session management, and security. Required for the service to function.", mandatory: true, consented: true },
  { id: "analytics", name: "Analytics & Performance", desc: "Help us understand how you use our service so we can improve it.", mandatory: false, consented: true },
  { id: "marketing", name: "Marketing & Personalization", desc: "Receive personalized content, recommendations, and offers.", mandatory: false, consented: false },
];

const languages = ["English", "हिन्दी (Hindi)", "தமிழ் (Tamil)", "తెలుగు (Telugu)", "ಕನ್ನಡ (Kannada)", "मराठी (Marathi)", "ગુજરાતી (Gujarati)", "বাংলা (Bengali)"];

export default function PreferencesPage({ params }: { params: Promise<{ tenant: string }> }) {
  const { tenant } = use(params);
  const [prefs, setPrefs] = useState(purposes);
  const [lang, setLang] = useState("English");
  const [saved, setSaved] = useState(false);

  const toggle = (id: string) => {
    if (id === "essential") return;
    setPrefs(prefs.map((p) => p.id === id ? { ...p, consented: !p.consented } : p));
    setSaved(false);
  };

  const selectAll = () => {
    setPrefs(prefs.map((p) => p.mandatory ? p : { ...p, consented: true }));
    setSaved(false);
  };

  const rejectAll = () => {
    setPrefs(prefs.map((p) => p.mandatory ? p : { ...p, consented: false }));
    setSaved(false);
  };

  const save = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-4">
          <Link href={`/p/${tenant}/preferences`} className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-[10px] font-bold text-primary-foreground">CM</div>
            <span className="text-sm font-semibold">Consent Preferences</span>
          </Link>
          <div className="flex items-center gap-3">
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              className="h-8 rounded-md border border-input bg-background px-2 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
            >
              {languages.map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
            <Link href={`/p/${tenant}/my-consents`} className="text-xs text-muted-foreground hover:text-foreground">My Consents</Link>
            <Link href={`/p/${tenant}/rights`} className="text-xs text-muted-foreground hover:text-foreground">My Rights</Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-lg font-semibold">Your Privacy Preferences</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Choose how your data is used. You can change these preferences at any time.
          </p>
        </div>

        <div className="mb-6 flex items-center gap-2">
          <button onClick={selectAll} className="rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90">
            Accept All
          </button>
          <button onClick={rejectAll} className="rounded-md border border-border px-3 py-1.5 text-xs font-medium hover:bg-accent">
            Reject All
          </button>
        </div>

        {saved && (
          <div className="mb-4 rounded-md bg-success/10 px-3 py-2 text-xs text-success">
            Your preferences have been saved.
          </div>
        )}

        <div className="space-y-3">
          {prefs.map((p) => (
            <div key={p.id} className="rounded-xl border border-border bg-card p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-medium">{p.name}</h3>
                    {p.mandatory && (
                      <span className="rounded-full bg-secondary px-2 py-0.5 text-[10px] text-muted-foreground">Required</span>
                    )}
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">{p.desc}</p>
                </div>
                <button
                  onClick={() => toggle(p.id)}
                  className={`ml-3 flex h-6 w-10 items-center rounded-full transition-colors ${
                    p.consented ? "bg-primary justify-end" : "bg-muted justify-start"
                  }`}
                >
                  <div className={`mx-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-transform ${
                    p.consented ? "translate-x-0" : "translate-x-0"
                  }`} />
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 flex items-center justify-between">
          <button onClick={save} className="rounded-md bg-primary px-4 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90">
            Save Preferences
          </button>
          <p className="text-xs text-muted-foreground">
            Withdrawal is as easy as grant — change anytime.
          </p>
        </div>

        <div className="mt-8 rounded-xl border border-border bg-card p-4">
          <h3 className="text-xs font-medium">Your Rights under DPDP Act 2023</h3>
          <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
            <Link href={`/p/${tenant}/rights`} className="rounded-md border border-border px-3 py-2 hover:bg-accent">
              Request my data (Access)
            </Link>
            <Link href={`/p/${tenant}/rights`} className="rounded-md border border-border px-3 py-2 hover:bg-accent">
              Correct my data
            </Link>
            <Link href={`/p/${tenant}/rights`} className="rounded-md border border-border px-3 py-2 hover:bg-accent">
              Erase my data
            </Link>
            <Link href={`/p/${tenant}/grievance`} className="rounded-md border border-border px-3 py-2 hover:bg-accent">
              File a grievance
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
