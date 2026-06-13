import { reactive } from 'vue';

/**
 * App-wide toast notifications. A single module-level store backs every caller,
 * so `useToast()` works anywhere — no provider injection, no prop drilling. The
 * <ToastViewport> mounted in the layout renders whatever lands in `toasts`.
 *
 *   const toast = useToast()
 *   toast.success('Link copied to clipboard')
 *   toast.error('Failed to subscribe. Please try again.')
 *   toast.info('Showing results for "gospel"')
 */

export type ToastVariant = 'success' | 'error' | 'info';

export interface Toast {
    id: number;
    variant: ToastVariant;
    message: string;
    duration: number;
}

// Oldest toasts past this count are dropped so the stack never overwhelms the
// screen (matches the "max 3 visible" behaviour in #160).
const MAX_TOASTS = 3;
const DEFAULT_DURATION = 3000;

const toasts = reactive<Toast[]>([]);
let nextId = 0;

function add(variant: ToastVariant, message: string, duration = DEFAULT_DURATION): number {
    const id = nextId++;
    toasts.push({ id, variant, message, duration });

    if (toasts.length > MAX_TOASTS) {
        toasts.splice(0, toasts.length - MAX_TOASTS);
    }

    return id;
}

function dismiss(id: number) {
    const index = toasts.findIndex((t) => t.id === id);
    if (index !== -1) toasts.splice(index, 1);
}

export function useToast() {
    return {
        toasts,
        toast: add,
        success: (message: string, duration?: number) => add('success', message, duration),
        error: (message: string, duration?: number) => add('error', message, duration),
        info: (message: string, duration?: number) => add('info', message, duration),
        dismiss,
    };
}
