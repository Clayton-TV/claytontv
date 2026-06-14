import { readonly, ref } from 'vue';

/**
 * Cookie-consent state (PECR / UK-GDPR).
 *
 * Two categories:
 *  - "necessary" — always on. We keep no necessary *tracking* cookies; this
 *    covers the visitor's own preferences (theme, text size, this choice).
 *  - "analytics" — opt-in. Until granted, PostHog runs cookieless (in-memory,
 *    no cross-visit id, no session recording). On consent it upgrades to
 *    localStorage+cookie persistence + session replay + heatmaps + autocapture.
 *    See lib/analytics.ts, which reads getAnalyticsConsent() and listens via
 *    onConsentChange() so a decision takes effect without a reload.
 *
 * The decision itself is stored in localStorage (a strictly-necessary use), so
 * the banner only shows until the visitor chooses — and again if we add a new
 * category (bump CONSENT_VERSION).
 */
const STORAGE_KEY = 'ctv:cookieConsent';
// Bump when the set of categories changes, to re-ask everyone.
const CONSENT_VERSION = 1;

type StoredConsent = { analytics: boolean; version: number; ts: string };

// Module-level singletons so the banner, the footer link and analytics all
// share one source of truth.
const analytics = ref(false);
const decided = ref(false);
const open = ref(false);
// True only in builds that actually ship analytics (VITE_POSTHOG_KEY present).
// Without it nothing non-essential runs, so there's nothing to consent to and we
// suppress the banner + footer link entirely (keeps dev and the current
// uninstrumented prod clean).
const enabled = ref(false);

const listeners = new Set<(analyticsAllowed: boolean) => void>();

function read(): StoredConsent | null {
    try {
        const raw = window.localStorage.getItem(STORAGE_KEY);
        if (!raw) return null;
        const parsed = JSON.parse(raw) as StoredConsent;
        // Treat an older-version record as "no decision" so we re-ask.
        return parsed && parsed.version === CONSENT_VERSION ? parsed : null;
    } catch {
        return null;
    }
}

function persist(analyticsAllowed: boolean) {
    try {
        const record: StoredConsent = {
            analytics: analyticsAllowed,
            version: CONSENT_VERSION,
            // Timestamp passed in via the host clock — stored as ISO for audit.
            ts: new Date().toISOString(),
        };
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(record));
    } catch {
        // Private mode / storage disabled — the choice still holds this session.
    }
}

/** Apply + remember a decision, then notify analytics (and any other listener). */
function decide(analyticsAllowed: boolean) {
    analytics.value = analyticsAllowed;
    decided.value = true;
    open.value = false;
    persist(analyticsAllowed);
    listeners.forEach((cb) => cb(analyticsAllowed));
}

/** Read any stored decision on boot; show the banner only if none exists yet. */
export function initializeCookieConsent() {
    if (typeof window === 'undefined') return;

    // No analytics in this build → nothing non-essential to consent to.
    if (!import.meta.env.VITE_POSTHOG_KEY) {
        enabled.value = false;
        decided.value = true;
        open.value = false;
        return;
    }
    enabled.value = true;

    const stored = read();
    if (stored) {
        analytics.value = stored.analytics;
        decided.value = true;
        open.value = false;
    } else {
        analytics.value = false;
        decided.value = false;
        open.value = true;
    }
}

/** Current analytics consent — false until the visitor actively opts in. */
export function getAnalyticsConsent(): boolean {
    return decided.value && analytics.value;
}

/** Subscribe to consent changes (analytics.ts uses this to flip PostHog live). */
export function onConsentChange(cb: (analyticsAllowed: boolean) => void) {
    listeners.add(cb);
    return () => listeners.delete(cb);
}

export function useCookieConsent() {
    return {
        open: readonly(open),
        enabled: readonly(enabled),
        analyticsGranted: readonly(analytics),
        decided: readonly(decided),
        // Primary CTA: accept everything.
        acceptAll: () => decide(true),
        // Decline non-essential (also the effect of "necessary only").
        rejectNonEssential: () => decide(false),
        // Save whatever the visitor toggled in the banner.
        savePreferences: (analyticsAllowed: boolean) => decide(analyticsAllowed),
        // Footer "Cookie settings" — let them revisit the choice (no-op in builds
        // without analytics, where there's nothing to consent to).
        reopen: () => {
            if (enabled.value) open.value = true;
        },
        dismiss: () => {
            open.value = false;
        },
    };
}
