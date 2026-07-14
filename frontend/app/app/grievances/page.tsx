"use client";

import { Search, MessageSquare, AlertTriangle, CheckCircle } from "lucide-react";

const grievances = [
  { id: "GR-2024-0112", principal: "alice@example.com", subject: "Delay in access request response — 45 days without update", status: "Open", assignee: "—", submitted: "2024-12-10", sla: "Overdue by 2d" },
  { id: "GR-2024-0111", principal: "bob@example.com", subject: "Personal data continued to be used 7 days after withdrawal", status: "In Progress", assignee: "dpo@cmp.local", submitted: "2024-12-08", sla: "Due in 1d" },
  { id: "GR-2024-0110", principal: "carol@example.com", subject: "Receiving marketing SMS despite unsubscribing", status: "Resolved", assignee: "dpo@cmp.local", submitted: "2024-12-01", sla: "Resolved" },
  { id: "GR-2024-0109", principal: "dave@example.com", subject: "Data erasure request not processed within timeline", status: "Open", assignee: "—", submitted: "2024-12-12", sla: "Due in 13d" },
];

export default function GrievancesPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Grievance Redressal</h1>
          <p className="text-sm text-muted-foreground">Manage data principal complaints with SLA tracking and DPB escalation</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="flex items-center gap-1"><AlertTriangle className="h-3 w-3 text-destructive" /> 1 Overdue</span>
          <span className="flex items-center gap-1"><MessageSquare className="h-3 w-3 text-primary" /> 2 Open</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input type="search" placeholder="Search grievances..." className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
        </div>
        <select className="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
          <option>All Statuses</option>
          <option>Open</option>
          <option>In Progress</option>
          <option>Resolved</option>
          <option>Escalated to DPB</option>
        </select>
      </div>

      <div className="space-y-3">
        {grievances.map((g) => (
          <div key={g.id} className="rounded-xl border border-border bg-card p-4 card-hover hover:shadow-sm cursor-pointer">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${
                  g.status === "Resolved" ? "bg-success/10" : g.status === "In Progress" ? "bg-primary/10" : "bg-warning/10"
                }`}>
                  {g.status === "Resolved" ? (
                    <CheckCircle className={`h-4 w-4 ${g.status === "Resolved" ? "text-success" : ""}`} />
                  ) : (
                    <MessageSquare className={`h-4 w-4 ${
                      g.status === "In Progress" ? "text-primary" : "text-warning"
                    }`} />
                  )}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-muted-foreground">{g.id}</span>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                      g.status === "Resolved" ? "bg-success/10 text-success" :
                      g.status === "In Progress" ? "bg-primary/10 text-primary" :
                      "bg-warning/10 text-warning"
                    }`}>{g.status}</span>
                  </div>
                  <p className="mt-1 text-sm font-medium">{g.subject}</p>
                  <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                    <span>{g.principal}</span>
                    <span>·</span>
                    <span>Submitted {g.submitted}</span>
                    {g.assignee !== "—" && <><span>·</span><span>Assignee: {g.assignee}</span></>}
                  </div>
                </div>
              </div>
              <div className={`text-xs font-medium ${
                g.sla.includes("Overdue") ? "text-destructive" : g.sla.includes("Due") ? "text-warning" : "text-success"
              }`}>{g.sla}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
