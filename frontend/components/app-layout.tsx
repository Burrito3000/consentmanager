"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "./app-sidebar";
import { Bell, Search, LogOut, Menu } from "lucide-react";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  const [userEmail, setUserEmail] = useState("Admin");

  useEffect(() => {
    const email = localStorage.getItem("admin_email");
    if (email) setUserEmail(email);
  }, []);

  function handleSignOut() {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_email");
    router.push("/");
  }

  const initials = userEmail.charAt(0).toUpperCase();

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar collapsed={collapsed} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-14 items-center justify-between border-b border-border bg-card px-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="rounded-md p-1.5 text-muted-foreground hover:bg-accent"
            >
              <Menu className="h-4 w-4" />
            </button>
            <div className="relative hidden sm:block">
              <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              <input
                type="search"
                placeholder="Search consents, purposes..."
                className="h-8 w-56 rounded-md border border-input bg-background pl-8 pr-3 text-xs placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="rounded-md p-1.5 text-muted-foreground hover:bg-accent">
              <Bell className="h-4 w-4" />
            </button>
            <div className="flex items-center gap-2 rounded-md px-2 py-1 text-sm hover:bg-accent cursor-pointer">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-[10px] font-medium text-primary-foreground">
                {initials}
              </div>
              <span className="hidden text-sm sm:block">{userEmail}</span>
            </div>
            <button
              onClick={handleSignOut}
              className="rounded-md p-1.5 text-muted-foreground hover:bg-accent"
              title="Sign out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
