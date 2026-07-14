"use client";

import { Plus, FileText, Globe, Languages } from "lucide-react";

const notices = [
  { id: 1, purpose: "Analytics & Performance", version: 3, status: "Published", languages: ["en", "hi", "ta"], updated: "2024-12-10" },
  { id: 2, purpose: "Marketing & Personalization", version: 2, status: "Published", languages: ["en", "hi"], updated: "2024-11-28" },
  { id: 3, purpose: "Essential Functionality", version: 1, status: "Draft", languages: ["en"], updated: "2024-12-01" },
];

export default function NoticesPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Privacy Notices</h1>
          <p className="text-sm text-muted-foreground">Create and manage multilingual notices per purpose</p>
        </div>
        <button className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          <Plus className="h-4 w-4" /> New Notice
        </button>
      </div>

      <div className="space-y-3">
        {notices.map((n) => (
          <div key={n.id} className="rounded-xl border border-border bg-card p-4 card-hover hover:shadow-sm cursor-pointer">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                  <FileText className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-medium">{n.purpose}</h3>
                    <span className="rounded-full bg-secondary px-2 py-0.5 text-[10px] text-muted-foreground">v{n.version}</span>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                      n.status === "Published" ? "bg-success/10 text-success" : "bg-warning/10 text-warning"
                    }`}>{n.status}</span>
                  </div>
                  <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Globe className="h-3 w-3" />
                      {n.languages.length} languages
                    </span>
                    <span>Updated {n.updated}</span>
                  </div>
                </div>
              </div>
              <div className="flex -space-x-1">
                {n.languages.map((lang) => (
                  <span key={lang} className="flex h-6 w-6 items-center justify-center rounded-full border border-border bg-card text-[9px] font-medium uppercase">
                    {lang}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
