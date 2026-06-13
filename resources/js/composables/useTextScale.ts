import { ref } from 'vue';

/**
 * User-controlled text size for the elderly-first audience. Scales the root
 * font size, so every rem-based size (text + spacing) grows proportionally —
 * a genuinely bigger, still-balanced UI, not just bigger glyphs. Persisted in
 * localStorage; no account needed. Pinch-zoom remains untouched (this is an
 * addition to, not a replacement for, browser zoom).
 */
const STORAGE_KEY = 'ctv:textScale';
const MIN = 0.9;
const MAX = 1.5;
const STEP = 0.1;
const DEFAULT = 1;

const scale = ref(DEFAULT);

const clamp = (value: number) => Math.min(MAX, Math.max(MIN, Math.round(value * 10) / 10));

function apply(value: number) {
    if (typeof document === 'undefined') return;
    // Root font-size as a percentage of the browser default (so a user's own
    // browser font-size preference is still respected and multiplied).
    document.documentElement.style.setProperty('--text-scale', String(value));
}

export function initializeTextScale() {
    if (typeof window === 'undefined') return;
    const stored = parseFloat(window.localStorage.getItem(STORAGE_KEY) || '');
    scale.value = Number.isFinite(stored) ? clamp(stored) : DEFAULT;
    apply(scale.value);
}

export function useTextScale() {
    const set = (value: number) => {
        scale.value = clamp(value);
        apply(scale.value);
        try {
            window.localStorage.setItem(STORAGE_KEY, String(scale.value));
        } catch {
            // private mode — the size still applies for this session
        }
    };

    const increase = () => set(scale.value + STEP);
    const decrease = () => set(scale.value - STEP);
    const reset = () => set(DEFAULT);

    const canIncrease = () => scale.value < MAX;
    const canDecrease = () => scale.value > MIN;
    const isDefault = () => scale.value === DEFAULT;

    return { scale, increase, decrease, reset, canIncrease, canDecrease, isDefault, MIN, MAX };
}
