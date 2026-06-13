<script setup lang="ts">
import { usePage } from '@inertiajs/vue3';
import { Check, Info, TriangleAlert, X } from 'lucide-vue-next';
import { watch } from 'vue';
import { useFlash, type FlashLevel } from '~/composables/useFlash';

// Persistent toast region (lives in AppLayout, survives navigation). Bridges
// server flash (Django messages shared as page.props.flash) into the queue, and
// also shows client-side notices pushed via useFlash (e.g. the error boundary).
const { toasts, push, dismiss } = useFlash();
const page = usePage();

// Each Inertia response carries its own flash array; pushing on change shows
// server messages once. Partial reloads that omit flash keep the same reference,
// so this won't re-fire for them.
watch(
    () => page.props.flash as { level: string; message: string }[] | undefined,
    (flash) => (flash ?? []).forEach((f) => push(f.message, f.level)),
    { immediate: true },
);

const icons: Record<FlashLevel, typeof Check> = {
    success: Check,
    info: Info,
    warning: TriangleAlert,
    error: TriangleAlert,
};
const accent: Record<FlashLevel, string> = {
    success: 'text-emerald-500',
    info: 'text-primary',
    warning: 'text-amber-500',
    error: 'text-destructive',
};
</script>

<template>
    <div class="pt-safe pointer-events-none fixed inset-x-0 top-0 z-[60] flex flex-col items-center gap-2 px-4 py-3" role="status" aria-live="polite">
        <TransitionGroup
            enter-active-class="transition duration-200 ease-out motion-reduce:transition-none"
            enter-from-class="-translate-y-2 opacity-0"
            leave-active-class="transition duration-150 ease-in motion-reduce:transition-none"
            leave-to-class="-translate-y-2 opacity-0"
        >
            <div
                v-for="toast in toasts"
                :key="toast.id"
                class="border-border bg-card text-card-foreground pointer-events-auto flex w-full max-w-md items-start gap-3 rounded-xl border px-4 py-3 shadow-lg"
            >
                <component :is="icons[toast.level]" :class="accent[toast.level]" class="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
                <p class="min-w-0 flex-1 text-sm leading-snug">{{ toast.message }}</p>
                <button
                    @click="dismiss(toast.id)"
                    aria-label="Dismiss"
                    class="text-muted-foreground hover:text-foreground focus-visible:ring-ring -mr-1 shrink-0 rounded outline-none focus-visible:ring-2"
                >
                    <X class="h-4 w-4" aria-hidden="true" />
                </button>
            </div>
        </TransitionGroup>
    </div>
</template>
