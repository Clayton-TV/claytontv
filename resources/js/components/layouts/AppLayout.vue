<script setup lang="ts">
import AppFooter from '@/layouts/AppFooter.vue';
import AppHeader from '@/layouts/AppHeader.vue';
import PersistentPlayer from '@/organisms/PersistentPlayer.vue';
</script>

<template>
    <!-- relative: PersistentPlayer's docked mode positions in document coords -->
    <div class="relative flex min-h-full flex-col bg-gray-950">
        <!-- Keyboard users skip the nav straight to content -->
        <a
            href="#main"
            class="bg-primary text-primary-foreground sr-only z-50 rounded-md px-4 py-2 text-sm font-semibold focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:outline-none focus:ring-2 focus:ring-white"
        >
            Skip to content
        </a>
        <AppHeader />
        <main id="main" tabindex="-1" class="flex-1 outline-none">
            <slot />
        </main>
        <AppFooter />
        <!-- The shared player outlives page navigations (persistent layout) -->
        <PersistentPlayer />
    </div>
</template>
