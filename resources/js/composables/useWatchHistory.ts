import { ref } from 'vue';

/**
 * Lightweight "have I seen this?" memory in localStorage — no accounts, no
 * tracking, just a courtesy for the viewer (especially older members catching
 * up across visits). Records which videos have been opened; the player APIs
 * needed for exact resume positions are a later addition.
 */
const STORAGE_KEY = 'ctv:watched';
const MAX_ENTRIES = 200;

type History = Record<string, number>; // videoId -> last-opened epoch ms

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

// Shared reactive snapshot so cards update without a reload
const watched = ref<History>(read());

export function useWatchHistory() {
    const markWatched = (videoId: string | number) => {
        if (typeof window === 'undefined') return;
        const id = String(videoId);
        watched.value = { ...watched.value, [id]: Date.now() };
        write(watched.value);
    };

    const hasWatched = (videoId: string | number) => String(videoId) in watched.value;

    return { watched, markWatched, hasWatched };
}
