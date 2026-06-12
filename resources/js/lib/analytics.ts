import { router } from '@inertiajs/vue3';

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
export async function initializeAnalytics() {
    const key = import.meta.env.VITE_POSTHOG_KEY;

    if (!key) {
        return;
    }

    const { default: posthog } = await import('posthog-js');

    posthog.init(key, {
        api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://posthog.tgo.dev',
        persistence: 'memory',
        person_profiles: 'identified_only',
        autocapture: false,
        capture_pageview: true,
        capture_pageleave: false,
        disable_session_recording: true,
        respect_dnt: true,
    });

    // Inertia SPA visits don't reload the page; report them as pageviews.
    router.on('navigate', (event) => {
        posthog.capture('$pageview', { $current_url: event.detail.page.url });
    });
}
