<script setup lang="ts">
import AppContent from '@/layout/AppContent.vue';
import AppFooter from '@/layout/AppFooter.vue';
import AppHeader from '@/layout/AppHeader.vue';
import AppShell from '@/layout/AppShell.vue';
</script>

<template>
    <AppShell variant="header">
        <AppHeader />
        <AppContent variant="header">
            <slot />
        </AppContent>
        <AppFooter />
    </AppShell>
</template>
