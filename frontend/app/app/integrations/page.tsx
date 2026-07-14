"use client";

import { useEffect, useState } from "react";
import { api, IntegrationData } from "@/lib/api";
import { Copy, Check, Globe, Code } from "lucide-react";

export default function IntegrationsPage() {
  const [data, setData] = useState<IntegrationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    api.getIntegration()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const copy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

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
        <div className="text-sm text-muted-foreground">{error || "Failed to load integrations"}</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Integrations</h1>
        <p className="text-sm text-muted-foreground">API keys, SDK setup, and platform integrations</p>
      </div>

      <div className="rounded-xl border border-border bg-card p-5">
        <h2 className="text-sm font-medium">API Keys</h2>
        <p className="mt-1 text-xs text-muted-foreground">Use these keys to authenticate API requests from your application.</p>
        {data.api_keys.length > 0 ? data.api_keys.map((key) => (
          <div key={key.id} className="mt-4 rounded-md border border-border p-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{key.label}</p>
                <p className="mt-0.5 font-mono text-xs text-muted-foreground">{key.prefix}...</p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-[10px] ${key.is_active ? "text-success" : "text-muted-foreground"}`}>
                  {key.is_active ? "Active" : "Inactive"}
                </span>
                <button
                  onClick={() => copy(key.prefix, key.id)}
                  className="rounded-md p-1.5 text-muted-foreground hover:bg-accent"
                >
                  {copied === key.id ? <Check className="h-3.5 w-3.5 text-success" /> : <Copy className="h-3.5 w-3.5" />}
                </button>
              </div>
            </div>
          </div>
        )) : <p className="mt-3 text-xs text-muted-foreground">No API keys yet</p>}
      </div>

      <div className="rounded-xl border border-border bg-card p-5">
        <h2 className="text-sm font-medium">SDK Embed</h2>
        <p className="mt-1 text-xs text-muted-foreground">Add this script to your website to render the consent banner and preference center.</p>
        <div className="mt-3 rounded-md bg-muted p-3 font-mono text-xs">
          <div className="flex items-start justify-between">
            <code>{`<script src="https://cdn.cmp.local/sdk/cmp.js" data-tenant-key="${data.api_keys[0]?.prefix || 'your-key'}"></script>`}</code>
            <button
              onClick={() => copy(`<script src="https://cdn.cmp.local/sdk/cmp.js" data-tenant-key="${data.api_keys[0]?.prefix || 'your-key'}"></script>`, "snippet")}
              className="rounded-md p-1 text-muted-foreground hover:bg-accent shrink-0"
            >
              {copied === "snippet" ? <Check className="h-3.5 w-3.5 text-success" /> : <Copy className="h-3.5 w-3.5" />}
            </button>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card p-5">
        <h2 className="text-sm font-medium">Allowed Origins</h2>
        <p className="mt-1 text-xs text-muted-foreground">CORS origins allowed to make SDK requests.</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {data.origins.length > 0 ? data.origins.map((origin) => (
            <div key={origin} className="flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-xs">
              <Globe className="h-3 w-3 text-muted-foreground" />
              {origin}
            </div>
          )) : <p className="text-xs text-muted-foreground">No origins configured</p>}
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card p-5">
        <h2 className="text-sm font-medium">Quick Start</h2>
        <div className="mt-3 space-y-2">
          {[
            { step: "1", title: "Get your API key", desc: "Use the sandbox key above to test integration." },
            { step: "2", title: "Embed the SDK", desc: "Copy the script tag into your website's head section." },
            { step: "3", title: "Configure purposes", desc: "Define what data you collect and why in the Purposes page." },
            { step: "4", title: "Test end-to-end", desc: "Visit your site, accept/decline consents, verify in the dashboard." },
            { step: "5", title: "Go live", desc: "Generate a production API key and update your embed snippet." },
          ].map((s) => (
            <div key={s.step} className="flex items-start gap-3 rounded-md border border-border p-2.5">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary">
                {s.step}
              </div>
              <div>
                <p className="text-sm font-medium">{s.title}</p>
                <p className="text-xs text-muted-foreground">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
