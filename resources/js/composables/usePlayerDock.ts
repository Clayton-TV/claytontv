import { computed, ref, shallowRef, watch } from 'vue';

/**
 * Shared state for the persistent player (the "dock"). The iframe lives in
 * AppLayout via PersistentPlayer — it survives Inertia navigations, so
 * playback continues while the viewer browses. The watch page doesn't own a
 * player; it registers a placeholder element the player positions itself
 * over ("docked"). No placeholder registered → the player floats in the
 * bottom corner ("mini").
 */

export interface DockVideo {
    id: string | number;
    name: string;
    url: string; // source url (YouTube/Vimeo), not the page url
}

export interface DockControls {
    toggle: () => void;
    play: () => void;
    pause: () => void;
    seekTo: (seconds: number) => void;
    seekBy: (seconds: number) => void;
    toggleMute: () => void;
}

const current = ref<DockVideo | null>(null);
const next = ref<{ id: string | number; name: string } | null>(null);
const autoplay = ref(false);
const resumedFrom = ref(0);
const playing = ref(false);
const position = ref(0);
const duration = ref(0);
const placeholder = shallowRef<HTMLElement | null>(null);
const controls = shallowRef<DockControls | null>(null);

const mode = computed(() => (current.value ? (placeholder.value ? 'docked' : 'mini') : 'hidden'));

// ----- survive a page refresh -----
// The dock is in-memory, so a reload would drop whatever's playing. Mirror the
// active video + position to localStorage (client-side; nothing to do with the
// Django session) and rehydrate on boot via restore(). Cleared on close().
const STORAGE_KEY = 'ctv:active-player';

const persist = () => {
    if (typeof localStorage === 'undefined') return;
    if (!current.value) {
        localStorage.removeItem(STORAGE_KEY);
        return;
    }
    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
            id: current.value.id,
            name: current.value.name,
            url: current.value.url,
            position: Math.floor(position.value),
        }),
    );
};

// Save when the video changes (incl. clear on close) and as playback advances,
// throttled so we're not writing every heartbeat tick.
let lastSavedAt = 0;
watch(current, persist);
watch(position, (seconds) => {
    if (!current.value || Math.abs(seconds - lastSavedAt) < 5) return;
    lastSavedAt = seconds;
    persist();
});

export function usePlayerDock() {
    /** Make this the playing video. Returns false (no-op) when it already is —
     * that's the seamless maximize: same iframe, playback never stops. */
    const load = (video: DockVideo, options: { autoplay?: boolean; startAt?: number } = {}) => {
        if (String(current.value?.id) === String(video.id)) return false;
        autoplay.value = options.autoplay ?? false;
        resumedFrom.value = options.startAt ?? 0;
        position.value = 0;
        duration.value = 0;
        next.value = null;
        current.value = video;
        return true;
    };

    const close = () => {
        current.value = null;
        next.value = null;
        playing.value = false;
        controls.value = null;
    };

    const setPlaceholder = (el: HTMLElement | null) => {
        placeholder.value = el;
        // Leaving the watch page with nothing playing: no reason to float
        if (!el && !playing.value) close();
    };

    /** Rehydrate the dock from localStorage on app boot (paused, at the saved
     * timecode). No-op if nothing was playing or it's already restored. Called
     * once from app.ts. */
    const restore = () => {
        if (typeof localStorage === 'undefined' || current.value) return;
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return;
        try {
            const saved = JSON.parse(raw);
            if (saved?.id && saved?.url) {
                load({ id: saved.id, name: saved.name, url: saved.url }, { startAt: saved.position || 0 });
                // load() zeroes position; seed it with the saved timecode so the
                // bar shows the right spot (and a paused restore doesn't persist 0
                // back over the saved value before the heartbeat catches up).
                position.value = saved.position || 0;
            }
        } catch {
            localStorage.removeItem(STORAGE_KEY);
        }
    };

    return {
        current,
        next,
        autoplay,
        resumedFrom,
        playing,
        position,
        duration,
        placeholder,
        controls,
        mode,
        load,
        close,
        setPlaceholder,
        restore,
    };
}
