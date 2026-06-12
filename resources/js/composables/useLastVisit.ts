/**
 * Remembers the last day the viewer opened a page (localStorage, no
 * accounts), so the Latest feed can draw a quiet "new since your last visit"
 * line. Day granularity — the catalogue dates videos by day.
 */
const STORAGE_KEY = 'ctv:lastVisit';

export function useLastVisit(page: string): string | null {
    if (typeof window === 'undefined') return null;
    const key = `${STORAGE_KEY}:${page}`;
    let previous: string | null = null;
    try {
        previous = window.localStorage.getItem(key);
        window.localStorage.setItem(key, new Date().toISOString().slice(0, 10));
    } catch {
        // storage unavailable (private mode) — feed just renders without the divider
    }
    return previous;
}
