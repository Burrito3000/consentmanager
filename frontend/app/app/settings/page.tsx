"use client";

import { Save } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="animate-fade-in space-y-6 max-w-2xl">
      <div>
        <h1 className="text-lg font-semibold">Settings</h1>
        <p className="text-sm text-muted-foreground">Workspace configuration, branding, and defaults</p>
      </div>

      <section className="rounded-xl border border-border bg-card p-5 space-y-4">
        <h2 className="text-sm font-medium">Organization Profile</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium">Organization name</label>
            <input type="text" defaultValue="Acme Corp" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium">Industry</label>
            <select className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
              <option>E-commerce</option>
              <option>Fintech</option>
              <option>Healthtech</option>
              <option>SaaS</option>
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium">Contact email</label>
            <input type="email" defaultValue="admin@acmecorp.com" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium">Domain</label>
            <input type="text" defaultValue="acmecorp.com" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
          </div>
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-5 space-y-4">
        <h2 className="text-sm font-medium">Branding</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium">Logo URL</label>
            <input type="text" placeholder="https://..." className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium">Brand color</label>
            <div className="flex items-center gap-2">
              <input type="text" defaultValue="#2E6BE6" className="h-9 flex-1 rounded-md border border-input bg-background px-3 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-ring" />
              <div className="h-9 w-9 rounded-md border border-border" style={{ backgroundColor: "#2E6BE6" }} />
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-5 space-y-4">
        <h2 className="text-sm font-medium">Defaults</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium">Default retention period (days)</label>
            <input type="number" defaultValue={365} className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium">Default language</label>
            <select className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
              <option>English (en)</option>
              <option>Hindi (hi)</option>
              <option>Tamil (ta)</option>
            </select>
          </div>
        </div>
      </section>

      <div className="flex justify-end">
        <button className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          <Save className="h-4 w-4" /> Save Changes
        </button>
      </div>
    </div>
  );
}
