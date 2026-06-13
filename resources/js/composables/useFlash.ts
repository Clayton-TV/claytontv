import { ref } from 'vue';

// Shared toast queue. Server flash (Django messages, bridged in Toaster.vue) and
// client-side notices (e.g. the error boundary / failed visits) push here.
export type FlashLevel = 'success' | 'info' | 'warning' | 'error';
export interface Toast {
    id: number;
    level: FlashLevel;
    message: string;
}

const toasts = ref<Toast[]>([]);
let seq = 0;

// Django's level_tag uses "debug"/"error" etc.; map the odd ones to our set.
const normalise = (level: string): FlashLevel =>
    level === 'debug' ? 'info' : ((['success', 'info', 'warning', 'error'].includes(level) ? level : 'info') as FlashLevel);

function dismiss(id: number) {
    toasts.value = toasts.value.filter((t) => t.id !== id);
}

function push(message: string, level: string = 'info', ttlMs = 6000) {
    if (!message) return -1;
    const id = ++seq;
    toasts.value = [...toasts.value, { id, level: normalise(level), message }];
    if (ttlMs > 0 && typeof window !== 'undefined') {
        window.setTimeout(() => dismiss(id), ttlMs);
    }
    return id;
}

export function useFlash() {
    return { toasts, push, dismiss };
}
