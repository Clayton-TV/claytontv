<script setup lang="ts">
import AppFooter from '@/layouts/AppFooter.vue';
import AppHeader from '@/layouts/AppHeader.vue';
import PersistentPlayer from '@/organisms/PersistentPlayer.vue';
</script>

<template>
    <!-- relative: PersistentPlayer's docked mode positions in document coords -->
    <div class="relative flex min-h-full flex-col bg-gray-950">
        <AppHeader />
        <main class="flex-1">
            <slot />
        </main>
        <AppFooter />
        <!-- The shared player outlives page navigations (persistent layout) -->
        <PersistentPlayer />
    </div>
</template>
