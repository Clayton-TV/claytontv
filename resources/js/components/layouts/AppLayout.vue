<script setup lang="ts">
import AppFooter from '@/layouts/AppFooter.vue';
import AppHeader from '@/layouts/AppHeader.vue';
import PersistentPlayer from '@/organisms/PersistentPlayer.vue';
</script>

<template>
    <!-- relative: PersistentPlayer's docked mode positions in document coords.
         overflow-x-clip: belt-and-braces against any descendant forcing
         horizontal scroll on mobile (clip, not hidden, so sticky still works). -->
    <div class="bg-background relative flex min-h-full flex-col overflow-x-clip">
        <!-- Keyboard users skip the nav straight to content -->
        <a
            href="#main"
            class="bg-primary text-primary-foreground sr-only z-50 rounded-md px-4 py-2 text-sm font-semibold focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:ring-2 focus:ring-white focus:outline-none"
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
