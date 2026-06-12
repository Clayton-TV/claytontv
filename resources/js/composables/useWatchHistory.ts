import { ref } from 'vue';

/**
 * Lightweight "have I seen this?" memory in localStorage — no accounts, no
 * tracking, just a courtesy for the viewer (especially older members catching
 * up across visits). Two stores: which videos have been opened (watched
 * ticks), and how far playback got (resume positions, via usePlayer).
 */
const STORAGE_KEY = 'ctv:watched';
const PROGRESS_KEY = 'ctv:progress';
const MAX_ENTRIES = 200;

// Played ≥80% counts as properly watched; resume only matters ≥30s in and
// stops being useful once the ending is in sight.
const WATCHED_FRACTION = 0.8;
const RESUME_MIN_SECONDS = 30;
const RESUME_MAX_FRACTION = 0.95;

type History = Record<string, number>; // videoId -> last-opened epoch ms
type Progress = Record<string, { t: number; d: number; at: number }>; // seconds, duration, updated epoch ms

function read(): History {
    if (typeof window === 'undefined') return {};
    try {
        return JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '{}');
    } catch {
        return {};
    }
}

function write(history: History) {
    // Keep only the most recent MAX_ENTRIES to bound storage growth
    const trimmed = Object.fromEntries(
        Object.entries(history)
            .sort((a, b) => b[1] - a[1])
            .slice(0, MAX_ENTRIES),
    );
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
}

function readProgress(): Progress {
    if (typeof window === 'undefined') return {};
    try {
        return JSON.parse(window.localStorage.getItem(PROGRESS_KEY) || '{}');
    } catch {
        return {};
    }
}

function writeProgress(progress: Progress) {
    const trimmed = Object.fromEntries(
        Object.entries(progress)
            .sort((a, b) => b[1].at - a[1].at)
            .slice(0, MAX_ENTRIES),
    );
    try {
        window.localStorage.setItem(PROGRESS_KEY, JSON.stringify(trimmed));
    } catch {
        // storage unavailable (private mode) — resume just won't persist
    }
}

// Shared reactive snapshots so cards update without a reload
const watched = ref<History>(read());
const progress = ref<Progress>(readProgress());

export function useWatchHistory() {
    const markWatched = (videoId: string | number) => {
        if (typeof window === 'undefined') return;
        const id = String(videoId);
        watched.value = { ...watched.value, [id]: Date.now() };
        write(watched.value);
    };

    const hasWatched = (videoId: string | number) => String(videoId) in watched.value;

    /** Heartbeat from the player; promotes to watched at 80% played. */
    const saveProgress = (videoId: string | number, seconds: number, duration: number) => {
        if (typeof window === 'undefined' || !duration) return;
        const id = String(videoId);
        progress.value = { ...progress.value, [id]: { t: Math.floor(seconds), d: Math.floor(duration), at: Date.now() } };
        writeProgress(progress.value);
        if (seconds / duration >= WATCHED_FRACTION && !hasWatched(id)) markWatched(id);
    };

    /** Seconds to resume from, or 0 when starting fresh is the right call. */
    const resumePoint = (videoId: string | number): number => {
        const entry = progress.value[String(videoId)];
        if (!entry || entry.t < RESUME_MIN_SECONDS || entry.t / entry.d > RESUME_MAX_FRACTION) return 0;
        return entry.t;
    };

    return { watched, progress, markWatched, hasWatched, saveProgress, resumePoint };
}
