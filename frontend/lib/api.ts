const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "https://consentmanager.netstartagency.com/").replace(/\/+$/, "");

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("admin_token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_email");
      window.location.href = "/login";
    }
    throw new ApiError(401, "Unauthorized");
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(res.status, body.detail || "Request failed");
  }

  return res.json();
}

export const api = {
  login: (email: string, password: string) =>
    request<{ token: string; email: string }>("/admin/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  getIndex: () => request<IndexData>("/admin/index"),

  getDashboard: () => request<DashboardData>("/admin/dashboard"),

  getPurposes: () => request<PurposesData>("/admin/purposes"),

  getConsents: () => request<ConsentsData>("/admin/consents"),

  getRights: () => request<RightsData>("/admin/rights"),

  getAudit: () => request<AuditData>("/admin/audit"),

  getIntegration: () => request<IntegrationData>("/admin/integration"),
};

export interface IndexData {
  language_count: number;
  sla_breached: number;
}

export interface DashboardData {
  total_consents: number;
  active_consents: number;
  withdrawn_consents: number;
  active_pct: number;
  withdrawn_pct: number;
  consent_change: string;
  pending_rights: number;
  sla_breached: number;
  purpose_stats: { name: string; count: number; pct: number }[];
  recent_events: { action: string; timestamp: string; actor: string }[];
  languages: string[];
}

export interface PurposesData {
  purposes: {
    id: string;
    name: string;
    description: string;
    is_active: boolean;
    retention_days: number;
    data_categories: string[];
    lawful_basis: string;
    notice_count: number;
    consent_count: number;
  }[];
  total_purposes: number;
  active_purposes: number;
  languages: string[];
}

export interface ConsentsData {
  consents: {
    consent_id: string;
    principal_ref: string;
    purpose_ids: string[];
    status: string;
    event_type: string;
    timestamp: string;
    source: string;
  }[];
  total_consents: number;
  active_consents: number;
  withdrawn_consents: number;
  expired_consents: number;
  chain_genesis_hash: string;
  chain_latest_hash: string;
  chain_verified: boolean;
}

export interface RightsData {
  rights_requests: {
    id: string;
    principal_ref: string;
    request_type: string;
    status: string;
    submitted_at: string;
    sla_due_at: string;
    days_left: string;
    is_breached: boolean;
  }[];
  grievances: {
    id: string;
    principal_ref: string;
    subject: string;
    status: string;
    submitted_at: string;
    sla_text: string;
  }[];
  total_requests: number;
  pending_requests: number;
  resolved_requests: number;
  sla_breached_requests: number;
  total_grievances: number;
  open_grievances: number;
  resolved_grievances: number;
  sla_breached_grievances: number;
}

export interface AuditData {
  audit_entries: {
    timestamp: string;
    action: string;
    actor: string;
    resource: string;
    prev_hash: string;
    hash_value: string;
    verified: boolean;
  }[];
  total_events: number;
  chain_valid: boolean;
  consent_events: number;
  rights_events: number;
  grievance_events: number;
  system_events: number;
}

export interface IntegrationData {
  api_keys: {
    id: string;
    label: string;
    prefix: string;
    is_active: boolean;
    created_at: string;
    allowed_origins: string[];
  }[];
  webhooks: Record<string, unknown>[];
  origins: string[];
}
