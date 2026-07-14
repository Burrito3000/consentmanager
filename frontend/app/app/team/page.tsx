"use client";

import { Plus, UsersRound, Shield, Mail, MoreHorizontal } from "lucide-react";

const team = [
  { name: "Kushal Bajoria", email: "kushal@cmp.local", role: "Owner", lastActive: "Now" },
  { name: "Priya Sharma", email: "priya@cmp.local", role: "Admin", lastActive: "2 hours ago" },
  { name: "Rahul Verma", email: "rahul@cmp.local", role: "DPO", lastActive: "1 day ago" },
  { name: "Sneha Patel", email: "sneha@cmp.local", role: "Analyst", lastActive: "3 days ago" },
  { name: "Arun Kumar", email: "arun@cmp.local", role: "Auditor", lastActive: "1 week ago" },
];

export default function TeamPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Team</h1>
          <p className="text-sm text-muted-foreground">Manage team members and their access roles</p>
        </div>
        <button className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          <Plus className="h-4 w-4" /> Invite Member
        </button>
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Email</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Role</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Last Active</th>
              <th className="px-4 py-3 w-8"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {team.map((m) => (
              <tr key={m.email} className="hover:bg-muted/30 transition-colors">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10 text-[10px] font-medium text-primary">
                      {m.name.split(" ").map((n) => n[0]).join("")}
                    </div>
                    <span className="text-sm font-medium">{m.name}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">{m.email}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                    m.role === "Owner" ? "bg-warning/10 text-warning" :
                    m.role === "Admin" ? "bg-primary/10 text-primary" :
                    m.role === "DPO" ? "bg-success/10 text-success" : "bg-secondary text-muted-foreground"
                  }`}>{m.role}</span>
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">{m.lastActive}</td>
                <td className="px-4 py-3">
                  <button className="rounded-md p-1 text-muted-foreground hover:bg-accent">
                    <MoreHorizontal className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
