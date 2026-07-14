"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Target, FileText, CheckSquare, Users,
  Scale, AlertTriangle, Shield, BarChart3, Puzzle, Webhook,
  UsersRound, Settings, CreditCard,
} from "lucide-react";

const allNavItems = [
  { href: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["admin"] },
  { href: "/app/purposes", label: "Purposes", icon: Target, roles: ["admin"] },
  { href: "/app/notices", label: "Notices", icon: FileText, roles: ["admin"] },
  { href: "/app/consents", label: "Consents", icon: CheckSquare, roles: ["admin"] },
  { href: "/app/data-principals", label: "Data Principals", icon: Users, roles: ["admin"] },
  { href: "/app/rights", label: "Rights Requests", icon: Scale, roles: ["admin"] },
  { href: "/app/grievances", label: "Grievances", icon: AlertTriangle, roles: ["admin"] },
  { href: "/app/audit", label: "Audit Log", icon: Shield, roles: ["admin"] },
  { href: "/app/analytics", label: "Analytics", icon: BarChart3, roles: ["admin"] },
  { href: "/app/integrations", label: "Integrations", icon: Puzzle, roles: ["admin"] },
  { href: "/app/webhooks", label: "Webhooks", icon: Webhook, roles: ["admin"] },
  { href: "/app/team", label: "Team", icon: UsersRound, roles: ["admin"] },
  { href: "/app/settings", label: "Settings", icon: Settings, roles: ["admin"] },
  { href: "/app/billing", label: "Billing", icon: CreditCard, roles: ["admin"] },
];

export default function Sidebar({ collapsed }: { collapsed: boolean }) {
  const pathname = usePathname();
  const [role, setRole] = useState<string>("admin");

  useEffect(() => {
    setRole(localStorage.getItem("admin_role") || "admin");
  }, []);

  const navItems = allNavItems.filter((item) => item.roles.includes(role));

  return (
    <aside
      className={`flex flex-col border-r border-sidebar-border bg-sidebar transition-all duration-200 ${
        collapsed ? "w-16" : "w-56"
      }`}
    >
      <div className="flex h-14 items-center gap-2 border-b border-sidebar-border px-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-[10px] font-bold text-primary-foreground">
          CM
        </div>
        {!collapsed && <span className="text-sm font-semibold">Consent Manager</span>}
      </div>
      <nav className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-md px-2.5 py-2 text-sm transition-colors ${
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              }`}
              title={collapsed ? item.label : undefined}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
        {navItems.length === 0 && !collapsed && (
          <p className="px-2.5 py-2 text-xs text-muted-foreground">No pages available</p>
        )}
      </nav>
    </aside>
  );
}
