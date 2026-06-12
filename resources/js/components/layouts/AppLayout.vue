<script setup lang="ts">
import AppFooter from '@/layouts/AppFooter.vue';
import AppHeader from '@/layouts/AppHeader.vue';
</script>

<template>
    <div class="flex min-h-full flex-col bg-gray-950">
        <AppHeader />
        <main class="flex-1">
            <slot />
        </main>
        <AppFooter />
    </div>
</template>
