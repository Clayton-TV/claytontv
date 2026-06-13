<script setup>
import VideoCardGrid from '@/organisms/VideoCardGrid.vue';
import { Head } from '@inertiajs/vue3';

defineProps({
    videos: {
        type: Array,
    },
    title: {
        type: String,
    },
    description: {
        type: String,
    },
    has_prev_page: {
        type: Boolean,
    },
    has_next_page: {
        type: Boolean,
    },
});
</script>

<template>
    <Head :title="title" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <VideoCardGrid :videos="videos" :title="title" :description="description ?? `Browsing videos under ` + title" :has_prev_page :has_next_page />
    </div>
</template>
