<script setup lang="ts">
import EmptyState from '@/molecules/EmptyState.vue';
import { router } from '@inertiajs/vue3';
import { IconAlertTriangle } from '@tabler/icons-vue';
import { onErrorCaptured, ref } from 'vue';

// Catches render/setup errors from the page below so one broken page shows a
// calm fallback instead of blanking the whole app (header + mini-player live
// above this boundary and keep working).
const failed = ref(false);

onErrorCaptured((err) => {
    failed.value = true;
    console.error('[ErrorBoundary]', err); // also visible to Sentry once the FE SDK lands
    return false; // contain it — don't let the broken subtree crash the app
});

// The boundary is in the persistent layout, so clear the fault when the user
// navigates, letting the next page render fresh.
router.on('start', () => {
    failed.value = false;
});

const reload = () => window.location.reload();
</script>

<template>
    <EmptyState
        v-if="failed"
        :icon="IconAlertTriangle"
        title="Something went wrong"
        message="This page didn't load properly. Reloading usually sorts it."
    >
        <template #actions>
            <button
                @click="reload"
                class="bg-primary text-primary-foreground focus-visible:ring-ring hover:bg-primary/90 focus-visible:ring-offset-background inline-flex min-h-11 items-center rounded-lg px-5 text-sm font-semibold transition-colors duration-150 outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
            >
                Reload the page
            </button>
        </template>
    </EmptyState>
    <slot v-else />
</template>
