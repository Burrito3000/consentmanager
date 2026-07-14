/**
 * React wrapper for the DPDP CMP SDK.
 *
 * Usage:
 *   import { ConsentBanner } from '@dpdp-cmp/consent-sdk/react';
 *
 *   <ConsentBanner
 *     tenantKey="cmp_live_xxx"
 *     principalRef="user-123"
 *     position="bottom"
 *     theme="dark"
 *   />
 */

import { useEffect, useRef } from "react";

interface ConsentBannerProps {
  tenantKey: string;
  principalRef?: string;
  apiBase?: string;
  locale?: string;
  position?: "bottom" | "center";
  theme?: "light" | "dark";
  onConsentUpdate?: (consentId: string) => void;
  onError?: (error: Error) => void;
}

declare global {
  interface Window {
    CMP: any;
  }
}

export function ConsentBanner({
  tenantKey,
  principalRef = "",
  apiBase,
  locale = "en",
  position = "bottom",
  theme = "light",
  onConsentUpdate,
  onError,
}: ConsentBannerProps) {
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    import("./index").catch(() => {
      // SDK loaded via script tag, already globally available
    });

    // Wait for script to load, then initialize
    const checkLoaded = setInterval(() => {
      if (typeof window !== "undefined" && window.CMP) {
        clearInterval(checkLoaded);
        try {
          const cmp = new window.CMP({
            tenantKey,
            principalRef,
            apiBase,
            locale,
            position,
            theme,
          });

          // Hook into consent updates
          const originalSubmit = cmp.submitConsent.bind(cmp);
          cmp.submitConsent = async function () {
            await originalSubmit();
            onConsentUpdate?.(cmp.state.consentId);
          };
        } catch (err) {
          onError?.(err as Error);
        }
      }
    }, 100);

    return () => clearInterval(checkLoaded);
  }, []);

  return null;
}
