<script setup lang="ts">
import { useToast } from '~/composables/useToast';
import { ToastPortal, ToastProvider, ToastViewport } from 'reka-ui';
import Toast from './Toast.vue';

// Mounted once in the app layout. Reka's ToastProvider gives us hover-to-pause
// and swipe handling for free; the actual toasts come from the module-level
// store in useToast(), so any component can fire one without wiring.
const { toasts, dismiss } = useToast();
</script>

<template>
    <ToastProvider :swipe-direction="'right'">
        <Toast
            v-for="t in toasts"
            :key="t.id"
            :variant="t.variant"
            :message="t.message"
            :duration="t.duration"
            @close="dismiss(t.id)"
        />
        <ToastPortal>
            <!-- Bottom-centre on mobile, bottom-right on desktop. Sits above the
                 safe-area inset so it clears the home indicator on notched
                 devices. z-toast keeps it over dialogs and the player dock. -->
            <ToastViewport
                class="fixed bottom-0 left-1/2 z-[var(--z-toast)] flex w-full max-w-[100vw] -translate-x-1/2 flex-col gap-2 p-4 pb-[max(1rem,env(safe-area-inset-bottom))] outline-none sm:right-0 sm:left-auto sm:translate-x-0 sm:max-w-sm"
            />
        </ToastPortal>
    </ToastProvider>
</template>
