"use client";

import { useEffect, useState } from "react";
import { api, PurposesData } from "@/lib/api";
import { Plus, Target, ToggleLeft, ToggleRight, MoreHorizontal } from "lucide-react";

export default function PurposesPage() {
  const [data, setData] = useState<PurposesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getPurposes()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-sm text-muted-foreground">{error || "Failed to load purposes"}</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Purposes</h1>
          <p className="text-sm text-muted-foreground">
            {data.active_purposes} active of {data.total_purposes} total purposes
          </p>
        </div>
        <button className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          <Plus className="h-4 w-4" /> New Purpose
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {data.purposes.map((p) => (
          <div key={p.id} className={`rounded-xl border p-5 ${p.is_active ? "border-border bg-card" : "border-dashed border-border/60 bg-muted/30"}`}>
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${p.is_active ? "bg-primary/10" : "bg-muted"}`}>
                  <Target className={`h-4 w-4 ${p.is_active ? "text-primary" : "text-muted-foreground"}`} />
                </div>
                <div>
                  <h3 className="text-sm font-medium">{p.name}</h3>
                  <p className="mt-0.5 text-xs text-muted-foreground max-w-md">{p.description}</p>
                </div>
              </div>
              <button className="rounded-md p-1 text-muted-foreground hover:bg-accent">
                <MoreHorizontal className="h-4 w-4" />
              </button>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {p.data_categories.map((cat) => (
                <span key={cat} className="rounded-full bg-secondary px-2.5 py-0.5 text-[11px] text-secondary-foreground">
                  {cat}
                </span>
              ))}
            </div>
            <div className="mt-4 flex items-center justify-between border-t border-border pt-3">
              <div className="flex items-center gap-4 text-[11px] text-muted-foreground">
                <span>Basis: <span className="font-medium text-foreground">{p.lawful_basis}</span></span>
                <span>Retention: <span className="font-medium text-foreground">{p.retention_days}d</span></span>
                <span>Consents: <span className="font-medium text-foreground">{p.consent_count}</span></span>
              </div>
              <button className="text-muted-foreground hover:text-foreground">
                {p.is_active ? <ToggleRight className="h-5 w-5 text-success" /> : <ToggleLeft className="h-5 w-5" />}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
