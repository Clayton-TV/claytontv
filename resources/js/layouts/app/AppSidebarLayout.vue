<script setup lang="ts">
import AppContent from '@/layout/AppContent.vue';
import AppShell from '@/layout/AppShell.vue';
import AppSidebar from '@/layout/AppSidebar.vue';
import AppSidebarHeader from '@/layout/AppSidebarHeader.vue';
import type { BreadcrumbItemType } from '@/types';

interface Props {
    breadcrumbs?: BreadcrumbItemType[];
}

withDefaults(defineProps<Props>(), {
    breadcrumbs: () => [],
});
</script>

<template>
    <AppShell variant="sidebar">
        <AppSidebar />
        <AppContent variant="sidebar">
            <AppSidebarHeader :breadcrumbs="breadcrumbs" />
            <slot />
        </AppContent>
    </AppShell>
</template>
