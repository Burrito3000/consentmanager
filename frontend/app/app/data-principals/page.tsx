"use client";

import { Search, Users, Mail, Phone } from "lucide-react";

const principals = [
  { ref: "user_8a3f", email: "john@example.com", phone: "+91-98765-43210", locale: "en", consents: 3, lastActive: "2024-12-12" },
  { ref: "user_c21b", email: "alice@example.com", phone: "+91-87654-32109", locale: "hi", consents: 1, lastActive: "2024-12-10" },
  { ref: "user_f74d", email: "bob@example.com", phone: "+91-76543-21098", locale: "en", consents: 2, lastActive: "2024-11-28" },
  { ref: "user_3e9a", email: "carol@example.com", phone: "+91-65432-10987", locale: "ta", consents: 4, lastActive: "2024-12-11" },
  { ref: "user_d12b", email: "dave@example.com", phone: null, locale: "en", consents: 1, lastActive: "2024-11-15" },
];

export default function DataPrincipalsPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Data Principals</h1>
        <p className="text-sm text-muted-foreground">View and manage data principal identities and their consent preferences</p>
      </div>

      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input type="search" placeholder="Search by reference, email, or phone..." className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Reference</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Contact</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Locale</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Active Consents</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Last Active</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {principals.map((p) => (
              <tr key={p.ref} className="hover:bg-muted/30 transition-colors cursor-pointer">
                <td className="px-4 py-3"><span className="font-mono text-xs">{p.ref}</span></td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-3 w-3 text-muted-foreground" /> {p.email}
                    {p.phone && <><span className="text-muted-foreground">·</span><Phone className="h-3 w-3 text-muted-foreground" /> {p.phone}</>}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="rounded-full bg-secondary px-2 py-0.5 text-[11px] uppercase">{p.locale}</span>
                </td>
                <td className="px-4 py-3 text-sm font-medium">{p.consents}</td>
                <td className="px-4 py-3 text-sm text-muted-foreground">{p.lastActive}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
