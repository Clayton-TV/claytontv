import { computed, ref, shallowRef } from 'vue';

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
    };
}
