/** Whole seconds → "h:mm:ss" or "m:ss". Empty string for null/undefined/0. */
export function formatDuration(seconds?: number | null): string {
    if (!seconds) return '';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const pad = (n: number) => String(n).padStart(2, '0');
    return hours ? `${hours}:${pad(minutes)}:${pad(secs)}` : `${minutes}:${pad(secs)}`;
}
