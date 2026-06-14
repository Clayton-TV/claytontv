/**
 * Read the CSRF token from the `XSRF-TOKEN` cookie.
 *
 * Django is configured (CSRF_COOKIE_NAME / CSRF_HEADER_NAME in base_settings)
 * to use the `XSRF-TOKEN` cookie + `X-XSRF-TOKEN` header that Inertia's client
 * uses by default. Inertia's own POSTs send this automatically; this helper is
 * for the handful of plain `fetch()` calls to JSON endpoints (e.g. the Studio's
 * Add-a-video metadata preview). The page must set the cookie first — we use
 * `@ensure_csrf_cookie` on those views.
 */
export function getCsrfToken(): string {
    const match = document.cookie.match(/(?:^|;\s*)XSRF-TOKEN=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
}
