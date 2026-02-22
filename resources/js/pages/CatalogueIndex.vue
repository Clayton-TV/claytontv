<script lang="ts" setup>
import Video from '@/atoms/Video.vue';
import PlaceholderPattern from '@/layout/PlaceholderPattern.vue';
import AppLayout from '@/layouts/AppLayout.vue';
import { BreadcrumbItem } from '@/types';
import { Deferred, Head } from '@inertiajs/vue3';

const breadcrumbs: BreadcrumbItem[] = [
    {
        title: 'Catalogue',
        href: '/catalogue',
    },
];

defineProps<{
    videos: any[];
}>();
</script>

<template>
    <Head title="Catalogue" />
    <AppLayout :breadcrumbs>
        <div class="flex h-full flex-1 flex-col gap-4 rounded-xl p-4 @container">
            <div class="grid auto-rows-min min-w-24 gap-y-4 grid-cols-1 @md:grid-cols-2 @xl:grid-cols-3">
                <Deferred data="videos">
                    <template #fallback>
                        <div class="border-sidebar-border/70 dark:border-sidebar-border relative aspect-video overflow-hidden rounded-xl border">
                            <PlaceholderPattern />
                        </div>
                        <div class="border-sidebar-border/70 dark:border-sidebar-border relative aspect-video overflow-hidden rounded-xl border">
                            <PlaceholderPattern />
                        </div>
                        <div class="border-sidebar-border/70 dark:border-sidebar-border relative aspect-video overflow-hidden rounded-xl border">
                            <PlaceholderPattern />
                        </div>
                    </template>
                    <Video v-for="video in videos" :key="video.id" :video />
                </Deferred>
            </div>
        </div>
    </AppLayout>
</template>

<style scoped></style>
