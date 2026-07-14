/**
 * DPDP Consent Management SDK — embeddable consent banner.
 *
 * Usage:
 *   <script src="https://cmp.example.com/sdk/cmp.js"
 *           data-tenant-key="cmp_live_xxx"
 *           data-principal-ref="user-123"
 *           data-api-base="https://api.cmp.example.com">
 *   </script>
 */

interface CMPConfig {
  tenantKey: string;
  principalRef: string;
  apiBase: string;
  locale: string;
  position: "bottom" | "center";
  theme: "light" | "dark";
}

interface PurposeConsent {
  purpose_id: string;
  name: string;
  description: string;
  data_categories: string[];
  granted: boolean;
}

interface ConsentNotice {
  title: string;
  body_text: string;
  how_to_withdraw: string;
  how_to_complain_to_dpb: string;
}

interface CMPState {
  config: CMPConfig;
  purposes: PurposeConsent[];
  notice: ConsentNotice | null;
  token: string | null;
  consentId: string | null;
}

class ConsentManager {
  private state: CMPState;
  private container: HTMLDivElement | null = null;
  private bannerEl: HTMLDivElement | null = null;
  private modalEl: HTMLDivElement | null = null;

  constructor(config: Partial<CMPConfig>) {
    this.state = {
      config: {
        tenantKey: config.tenantKey || "",
        principalRef: config.principalRef || "",
        apiBase: config.apiBase || "",  // Must be set via data-api-base attribute
        locale: config.locale || "en",
        position: config.position || "bottom",
        theme: config.theme || "light",
      },
      purposes: [],
      notice: null,
      token: null,
      consentId: null,
    };

    if (!this.state.config.tenantKey) {
      console.error("[CMP] Missing tenant-key attribute");
      return;
    }

    this.init();
  }

  private async init(): Promise<void> {
    try {
      await this.authenticate();
      await this.loadPurposes();
      await this.loadExistingConsent();
      this.render();
    } catch (err) {
      console.error("[CMP] Initialization error:", err);
    }
  }

  private async authenticate(): Promise<void> {
    const resp = await fetch(`${this.state.config.apiBase}/auth/sdk-token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tenant_key: this.state.config.tenantKey,
        principal_ref: this.state.config.principalRef,
      }),
    });
    const data = await resp.json();
    this.state.token = data.token;
  }

  private async loadPurposes(): Promise<void> {
    const resp = await fetch(
      `${this.state.config.apiBase}/purposes?locale=${this.state.config.locale}`,
      {
        headers: { Authorization: `Bearer ${this.state.token}` },
      }
    );
    const data = await resp.json();
    this.state.purposes = data.purposes.map((p: any) => ({
      purpose_id: p.id,
      name: p.name,
      description: p.description,
      data_categories: p.data_categories,
      granted: false,
    }));
    this.state.notice = data.notice;
  }

  private async loadExistingConsent(): Promise<void> {
    const resp = await fetch(
      `${this.state.config.apiBase}/consent?principal_ref=${this.state.config.principalRef}`,
      {
        headers: { Authorization: `Bearer ${this.state.token}` },
      }
    );
    if (resp.ok) {
      const data = await resp.json();
      if (data.consent_id) {
        this.state.consentId = data.consent_id;
        // Merge existing consent state
        for (const pc of data.purpose_consents || []) {
          const existing = this.state.purposes.find(
            (p) => p.purpose_id === pc.purpose_id
          );
          if (existing) {
            existing.granted = pc.granted;
          }
        }
      }
    }
  }

  private async submitConsent(): Promise<void> {
    const payload = {
      principal_ref: this.state.config.principalRef,
      purpose_grants: this.state.purposes.map((p) => ({
        purpose_id: p.purpose_id,
        granted: p.granted,
        data_categories: p.data_categories,
      })),
      notice_version: this.state.notice ? "latest" : "",
    };

    const endpoint = this.state.consentId
      ? `${this.state.config.apiBase}/consent/${this.state.consentId}/modify`
      : `${this.state.config.apiBase}/consent/grant`;

    const resp = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.state.token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      throw new Error("Failed to submit consent");
    }

    const data = await resp.json();
    this.state.consentId = data.consent_id;
  }

  private async withdrawConsent(): Promise<void> {
    if (!this.state.consentId) {
      console.warn("[CMP] No consent to withdraw");
      return;
    }

    const resp = await fetch(
      `${this.state.config.apiBase}/consent/${this.state.consentId}/withdraw`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.state.token}`,
        },
        body: JSON.stringify({
          principal_ref: this.state.config.principalRef,
        }),
      }
    );

    if (!resp.ok) {
      throw new Error("Failed to withdraw consent");
    }

    this.state.purposes.forEach((p) => (p.granted = false));
    this.state.consentId = null;
  }

  private render(): void {
    // Remove any existing CMP elements
    this.destroy();

    // Create container
    this.container = document.createElement("div");
    this.container.id = "cmp-container";
    this.container.style.cssText = `
      position: fixed;
      z-index: 2147483647;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

    this.renderBanner();
    document.body.appendChild(this.container);
  }

  private renderBanner(): void {
    this.bannerEl = document.createElement("div");
    this.bannerEl.style.cssText = `
      position: fixed;
      ${this.state.config.position === "center" ? "top: 50%; left: 50%; transform: translate(-50%, -50%);" : "bottom: 0; left: 0; right: 0;"}
      background: ${this.state.config.theme === "dark" ? "#1a1a2e" : "#ffffff"};
      color: ${this.state.config.theme === "dark" ? "#e0e0e0" : "#333333"};
      padding: 24px;
      border-radius: ${this.state.config.position === "center" ? "16px" : "16px 16px 0 0"};
      box-shadow: 0 -4px 24px rgba(0,0,0,0.15);
      max-width: ${this.state.config.position === "center" ? "600px" : "100%"};
      max-height: 80vh;
      overflow-y: auto;
      border: 1px solid ${this.state.config.theme === "dark" ? "#333" : "#e0e0e0"};
    `;

    // Title
    const title = document.createElement("h2");
    title.textContent =
      this.state.notice?.title || "Manage Your Consent Preferences";
    title.style.cssText = "font-size: 20px; font-weight: 600; margin-bottom: 12px;";
    this.bannerEl.appendChild(title);

    // Body text
    if (this.state.notice?.body_text) {
      const body = document.createElement("p");
      body.textContent = this.state.notice.body_text;
      body.style.cssText = "font-size: 14px; margin-bottom: 16px; line-height: 1.5;";
      this.bannerEl.appendChild(body);
    }

    // Purpose toggles
    this.state.purposes.forEach((purpose) => {
      const row = document.createElement("div");
      row.style.cssText = `
        display: flex; align-items: center; justify-content: space-between;
        padding: 12px 0; border-bottom: 1px solid
        ${this.state.config.theme === "dark" ? "#333" : "#eee"};
      `;

      const label = document.createElement("div");
      const name = document.createElement("div");
      name.textContent = purpose.name;
      name.style.cssText = "font-weight: 500; font-size: 14px;";
      const desc = document.createElement("div");
      desc.textContent = purpose.description;
      desc.style.cssText = "font-size: 12px; color: #888; margin-top: 2px;";
      label.appendChild(name);
      label.appendChild(desc);

      const toggle = document.createElement("input");
      toggle.type = "checkbox";
      toggle.checked = purpose.granted;
      toggle.style.cssText = `
        width: 20px; height: 20px; cursor: pointer;
        accent-color: #6366f1;
      `;
      toggle.addEventListener("change", () => {
        purpose.granted = toggle.checked;
      });

      row.appendChild(label);
      row.appendChild(toggle);
      this.bannerEl!.appendChild(row);
    });

    // Buttons
    const btnContainer = document.createElement("div");
    btnContainer.style.cssText =
      "display: flex; gap: 12px; margin-top: 20px; justify-content: flex-end;";

    const saveBtn = document.createElement("button");
    saveBtn.textContent = this.state.consentId
      ? "Update Preferences"
      : "Accept Selected";
    saveBtn.style.cssText = `
      padding: 12px 24px; background: #6366f1; color: white;
      border: none; border-radius: 8px; font-size: 14px; font-weight: 500;
      cursor: pointer;
    `;
    saveBtn.addEventListener("click", async () => {
      saveBtn.disabled = true;
      saveBtn.textContent = "Saving...";
      try {
        await this.submitConsent();
        this.destroy();
      } catch (err) {
        saveBtn.disabled = false;
        saveBtn.textContent = "Error — Retry";
      }
    });
    btnContainer.appendChild(saveBtn);

    // Withdraw button (only if consent exists)
    if (this.state.consentId) {
      const withdrawBtn = document.createElement("button");
      withdrawBtn.textContent = "Withdraw All";
      withdrawBtn.style.cssText = `
        padding: 12px 24px; background: transparent; color: #ef4444;
        border: 1px solid #ef4444; border-radius: 8px; font-size: 14px;
        cursor: pointer;
      `;
      withdrawBtn.addEventListener("click", async () => {
        if (confirm("Are you sure you want to withdraw all consent?")) {
          withdrawBtn.disabled = true;
          try {
            await this.withdrawConsent();
            this.destroy();
          } catch (err) {
            withdrawBtn.disabled = false;
          }
        }
      });
      btnContainer.appendChild(withdrawBtn);
    }

    this.bannerEl.appendChild(btnContainer);

    // Withdrawal and DPB info
    if (this.state.notice) {
      const info = document.createElement("div");
      info.style.cssText = "margin-top: 16px; font-size: 12px; color: #888;";

      if (this.state.notice.how_to_withdraw) {
        const w = document.createElement("p");
        w.textContent = this.state.notice.how_to_withdraw;
        info.appendChild(w);
      }
      if (this.state.notice.how_to_complain_to_dpb) {
        const c = document.createElement("p");
        c.style.cssText = "margin-top: 4px;";
        c.textContent = this.state.notice.how_to_complain_to_dpb;
        info.appendChild(c);
      }

      this.bannerEl.appendChild(info);
    }

    this.container!.appendChild(this.bannerEl);
  }

  destroy(): void {
    if (this.container && this.container.parentNode) {
      this.container.parentNode.removeChild(this.container);
    }
    this.container = null;
    this.bannerEl = null;
    this.modalEl = null;
  }
}

// Auto-initialize from data attributes
(function () {
  const script = document.currentScript;
  if (!script) return;

  const tenantKey = script.getAttribute("data-tenant-key");
  const principalRef = script.getAttribute("data-principal-ref");
  const apiBase = script.getAttribute("data-api-base") || undefined;
  const locale = script.getAttribute("data-locale") || undefined;
  const position = script.getAttribute("data-position") as any || undefined;
  const theme = script.getAttribute("data-theme") as any || undefined;

  if (!tenantKey) {
    console.error("[CMP] data-tenant-key attribute required");
    return;
  }

  // Expose globally
  (window as any).CMP = new ConsentManager({
    tenantKey,
    principalRef: principalRef || "",
    apiBase,
    locale,
    position,
    theme,
  });
})();
