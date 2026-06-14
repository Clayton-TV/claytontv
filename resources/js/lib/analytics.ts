import { router } from '@inertiajs/vue3';
import type { PostHog } from 'posthog-js';

/**
 * Privacy-respecting analytics (self-hosted PostHog).
 *
 * Activates only when VITE_POSTHOG_KEY is present at build time, so local
 * dev and CI capture nothing. Configured cookieless: persistence lives in
 * memory only, no cross-visit identifiers, no person profiles for anonymous
 * visitors — usage trends without tracking individuals.
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
} as const;

export async function initializeAnalytics() {
    const key = import.meta.env.VITE_POSTHOG_KEY;

    if (!key) {
        return;
    }

    const { default: ph } = await import('posthog-js');

    ph.init(key, {
        api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://posthog.tgo.dev',
        persistence: 'memory',
        person_profiles: 'identified_only',
        autocapture: false,
        capture_pageview: true,
        capture_pageleave: false,
        disable_session_recording: true,
        respect_dnt: true,
    });

    posthog = ph;

    // Inertia SPA visits don't reload the page; report them as pageviews.
    router.on('navigate', (event) => {
        posthog?.capture('$pageview', { $current_url: event.detail.page.url });
    });
}

/**
 * Fire a custom event. No-op until PostHog is initialised (keyless builds never
 * initialise), so it's always safe to call from any component.
 */
export function track(event: string, properties?: Record<string, unknown>) {
    posthog?.capture(event, properties);
}
