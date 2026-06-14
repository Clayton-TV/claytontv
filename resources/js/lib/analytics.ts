import { router } from '@inertiajs/vue3';

/**
 * Self-hosted PostHog analytics.
 *
 * Activates only when VITE_POSTHOG_KEY is present at build time, so local
 * dev and CI capture nothing — and prod stays clean until the key is added
 * to the prod build env. Anonymous visitors still get no person profile
 * (person_profiles: 'identified_only').
 *
 * NOTE (2026-06): session replay, heatmaps and autocapture are enabled, and
 * persistence moved off 'memory' to 'localStorage+cookie' so a visit holds a
 * stable id across page loads (replays/heatmaps are incoherent otherwise).
 * This sets first-party storage/cookies → a cookie-consent banner is required
 * before this ships to production. respect_dnt stays on; session inputs are
 * masked in recordings. See PostHog "session replay" docs for masking knobs.
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
        persistence: 'localStorage+cookie',
        person_profiles: 'identified_only',
        autocapture: true,
        capture_pageview: true,
        capture_pageleave: true,
        capture_heatmaps: true,
        disable_session_recording: false,
        session_recording: {
            // Mask form inputs in recordings; keep general text visible so
            // playback is useful (this is a sermon library, not a PII app).
            maskAllInputs: true,
        },
        respect_dnt: true,
    });

    // Inertia SPA visits don't reload the page; report them as pageviews.
    router.on('navigate', (event) => {
        posthog.capture('$pageview', { $current_url: event.detail.page.url });
    });
}
