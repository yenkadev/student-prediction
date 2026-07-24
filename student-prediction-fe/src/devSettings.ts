import { useCallback, useEffect, useState } from "react";

/**
 * Lightweight developer settings, persisted in localStorage.
 *
 * These flags are for developers / researchers only — they are hidden from the
 * normal assessment flow by default. Toggle them from the "Developer" section in
 * the sidebar footer.
 */
export interface DevSettings {
  /** Reveal the data source + solution dropdowns on the New assessment screen. */
  experimentControls: boolean;
}

const STORAGE_KEY = "student-risk-dev-settings";
const CHANGE_EVENT = "dev-settings-change";

const DEFAULTS: DevSettings = {
  experimentControls: false,
};

function read(): DevSettings {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? { ...DEFAULTS, ...(JSON.parse(raw) as Partial<DevSettings>) } : DEFAULTS;
  } catch {
    return DEFAULTS;
  }
}

function write(next: DevSettings) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    /* ignore write failures (private mode, etc.) */
  }
  // Notify listeners in the same tab; the native "storage" event only fires
  // across tabs.
  window.dispatchEvent(new CustomEvent(CHANGE_EVENT));
}

/**
 * Subscribe to developer settings. Returns the current settings plus a helper
 * to flip a single flag. Stays in sync across every component that uses it.
 */
export function useDevSettings(): {
  settings: DevSettings;
  setFlag: (key: keyof DevSettings, value: boolean) => void;
} {
  const [settings, setSettings] = useState<DevSettings>(read);

  useEffect(() => {
    const sync = () => setSettings(read());
    window.addEventListener(CHANGE_EVENT, sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener(CHANGE_EVENT, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  const setFlag = useCallback((key: keyof DevSettings, value: boolean) => {
    write({ ...read(), [key]: value });
  }, []);

  return { settings, setFlag };
}
