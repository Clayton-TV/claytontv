<script setup lang="ts">
import VideoCardGrid from '@/organisms/VideoCardGrid.vue';

defineProps({
    videos: {
        type: Array as () => Record<string, any>[],
        required: true,
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
    <VideoCardGrid :videos="videos" :title="title" :description="description ?? `Browsing videos under ` + title" :has_prev_page :has_next_page />
</template>
