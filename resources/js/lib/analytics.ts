import { router } from '@inertiajs/vue3';
import type { PostHog } from 'posthog-js';
import { getAnalyticsConsent, onConsentChange } from '~/composables/useCookieConsent';

/**
 * Privacy-respecting analytics (self-hosted PostHog).
 *
 * Activates only when VITE_POSTHOG_KEY is present at build time, so local
 * dev and CI capture nothing — and prod stays clean until the key is added.
 *
 * Consent-gated (PECR / UK-GDPR — see useCookieConsent):
 *  - No analytics consent → COOKIELESS: in-memory persistence, no cross-visit
 *    id, no autocapture, no heatmaps, no session recording. Sets no cookies.
 *  - Analytics consent → localStorage+cookie persistence (stable per-visit id),
 *    autocapture, heatmaps and masked session replay. The consent banner flips
 *    this live via applyAnalyticsConsent() (persistence + recording apply
 *    immediately; autocapture/heatmaps are init-time, so they engage on the
 *    next page load). respect_dnt and person_profiles:'identified_only' always.
 *
 * posthog-js is heavy (~200 kB), so it loads as a lazy chunk after boot and
 * never ships in keyless builds.
 */

// Set once posthog-js has loaded + initialised. Stays null in keyless builds,
// so track() below is inert in dev / CI / any build without VITE_POSTHOG_KEY.
let posthog: PostHog | null = null;

/**
 * Custom product-analytics event names. Defined as fixed constants (never
 * interpolated) per PostHog's best practices — dynamic data (speaker, query,
 * percent…) rides in the properties object, not the event name, to avoid a
 * cardinality explosion of unusable event definitions.
 */
export const EVENTS = {
    searchPerformed: 'search_performed',
    searchResultClicked: 'search_result_clicked',
    videoPlay: 'video_play',
    videoProgress: 'video_progress',
    videoComplete: 'video_complete',
    browseViewed: 'browse_viewed',
    navClicked: 'nav_clicked',
    heroCtaClicked: 'hero_cta_clicked',
    kidsPathViewed: 'kids_path_viewed',
} as const;

// Where the visitor first landed this session, and whether they've since moved
// on. Lets hero_cta_clicked flag an entry-page click with no persistent storage
// (we stay cookieless), so is_first_visit is privacy-safe by construction.
let entryPath: string | null = null;
let hasLeftEntry = false;

// Which deployment is sending events. Derived from the host (deploys are
// per-domain), so a single PostHog project can distinguish environments without
// the paid "Environments" feature — and prod tags itself once it gets a key.
function detectEnvironment(): string {
    const host = window.location.hostname;
    if (host.startsWith('beta.')) return 'beta';
    if (host === 'claytontv.co.uk' || host === 'www.claytontv.co.uk') return 'production';
    return 'development';
}

export async function initializeAnalytics() {
    const key = import.meta.env.VITE_POSTHOG_KEY;

    if (!key) {
        return;
    }

    const { default: ph } = await import('posthog-js');

    // Choose the initial config from any stored consent. Autocapture/heatmaps are
    // init-time only, so a returning visitor who already opted in gets the full
    // set from the first load; everyone else starts cookieless.
    const consented = getAnalyticsConsent();

    ph.init(key, {
        api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://posthog.tgo.dev',
        persistence: consented ? 'localStorage+cookie' : 'memory',
        person_profiles: 'identified_only',
        autocapture: consented,
        capture_pageview: true,
        capture_pageleave: consented,
        capture_heatmaps: consented,
        disable_session_recording: !consented,
        session_recording: {
            // Mask form inputs in recordings; general text stays visible so
            // playback is useful (this is a sermon library, not a PII app).
            maskAllInputs: true,
        },
        respect_dnt: true,
    });

    posthog = ph;

    // Tag every event with the deployment that sent it (beta / production), so a
    // single PostHog project can tell environments apart without the paid
    // "Environments" feature.
    ph.register({ environment: detectEnvironment() });

    // React to consent decisions made after boot (the banner on first visit, or
    // the footer "Cookie settings" later).
    onConsentChange(applyAnalyticsConsent);

    // Remember the entry surface so isEntryView() can flag a landing-page click.
    entryPath = normalizePath(window.location.pathname);

    // Report the entry surface's browse_viewed here. posthog-js already captures
    // the entry $pageview itself on init (capture_pageview: true), so the landing
    // page gets browse_viewed only — not a duplicate $pageview.
    trackBrowseFromUrl(window.location.pathname + window.location.search);

    // Inertia v3 fires 'navigate' on the INITIAL visit too — not just later SPA
    // visits — and that event races with this lazily-imported posthog chunk (it
    // may arrive after we register, or before we ever subscribed). We've already
    // reported the entry surface above, so ignore any navigate that's still on
    // the entry path until the visitor actually leaves: that dedupes the initial
    // visit either way the race resolves, without a fragile one-shot latch. Once
    // they've left, a later return to the entry path is a real visit and fires.
    router.on('navigate', (event) => {
        const url = event.detail.page.url;
        if (!hasLeftEntry && normalizePath(url) === entryPath) {
            return;
        }
        hasLeftEntry = true;
        posthog?.capture('$pageview', { $current_url: url });
        trackBrowseFromUrl(url);
    });
}

/**
 * Fire a custom event. No-op until PostHog is initialised (keyless builds never
 * initialise), so it's always safe to call from any component.
 */
export function track(event: string, properties?: Record<string, unknown>) {
    posthog?.capture(event, properties);
}

/**
 * Apply a consent decision to the live PostHog instance. Persistence and session
 * recording can switch at runtime, so they take effect immediately; autocapture
 * and heatmaps are init-time options and engage on the next page load (the
 * decision is persisted, so the next init picks the full config). No-op until
 * posthog-js has loaded — initializeAnalytics() seeds the correct initial state.
 */
function applyAnalyticsConsent(analyticsAllowed: boolean) {
    if (!posthog) return;
    if (analyticsAllowed) {
        posthog.set_config({ persistence: 'localStorage+cookie' });
        posthog.startSessionRecording();
    } else {
        // Revoked (or never granted): stop recording, drop the stored id and any
        // cookies, and fall back to in-memory so nothing persists across visits.
        posthog.stopSessionRecording();
        posthog.set_config({ persistence: 'memory' });
        posthog.reset();
    }
}

/**
 * True until the visitor navigates away from the page they entered on. Used as
 * hero_cta_clicked's `is_first_visit`: an honest, storage-free proxy meaning
 * "first/entry page of this session" — not a cross-visit identity (we keep none).
 */
export function isEntryView(): boolean {
    return !hasLeftEntry;
}

// First path segment → the browse_type we report. Detail pages add the slug as
// `value`; index pages report value: null.
const BROWSE_TYPES: Record<string, string> = {
    series: 'series',
    speaker: 'speaker',
    topic: 'topic',
    book: 'bible_book',
    audience: 'audience',
    demographic: 'audience', // legacy alias that redirects to /audience
    ministry: 'ministry',
    channel: 'channel',
    latest: 'latest',
    browse: 'all',
};

// Audience "slugs" are the demographic's free-text name, URL-encoded (e.g.
// /audience/Kids — see Demographic.get_absolute_url). The current set is
// Kids / Youth / Adults; this heuristic flags the kids/family ones (plus the
// audience index, which always fires) for the dedicated P4 "can they find the
// kids path?" event. Adults and unrelated demographics (e.g. searchers) don't
// match. It's a best-effort match over admin-editable names, so an unusually
// named future kids demographic would under-report rather than misfire.
const KIDS_PATTERN = /kid|child|infant|toddler|tot|baby|family|young|youth|teen|junior/i;

// Canonicalise a path for comparison and segmenting: drop query/hash + trailing
// slash, then decode each segment. Decoding matters for the entry-dedup check —
// window.location.pathname and Inertia's page.url encode reserved characters
// differently (e.g. a speaker slug "Steele, Dominic" is "Steele,%20Dominic" vs
// "Steele%2C%20Dominic"), so without decoding the entry path would never match
// its own initial-visit navigate and browse_viewed/$pageview would double-fire.
// Split before decode so an encoded slash inside a segment can't create one.
function normalizePath(url: string): string {
    const raw = url.split('?')[0].split('#')[0];
    const trimmed = raw.length > 1 ? raw.replace(/\/+$/, '') : raw;
    return trimmed
        .split('/')
        .map((segment) => {
            try {
                return decodeURIComponent(segment);
            } catch {
                return segment;
            }
        })
        .join('/');
}

/**
 * Emit a typed browse_viewed (and kids_path_viewed where relevant) for any
 * directory or entity surface, derived purely from the URL. URL-driven on
 * purpose: it can't break on an unexpected page-prop shape, and it covers every
 * browse page from one place — including the generic Browse.vue that backs the
 * topic / audience / ministry / channel detail pages.
 */
function trackBrowseFromUrl(url: string) {
    // normalizePath already decodes each segment, so don't decode again here.
    const segments = normalizePath(url).split('/').filter(Boolean);

    const browseType = segments.length ? BROWSE_TYPES[segments[0]] : undefined;
    if (!browseType) return;

    const value = segments.length > 1 ? segments[1] : null;
    track(EVENTS.browseViewed, { browse_type: browseType, value });

    if (browseType === 'audience' && (value === null || KIDS_PATTERN.test(value))) {
        track(EVENTS.kidsPathViewed, { source: value ?? 'index' });
    }
}
