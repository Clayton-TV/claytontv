<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Link } from "@inertiajs/vue3"
import VideoCardGrid from "@/organisms/VideoCardGrid.vue"

const props = defineProps({
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
})
</script>

<template>
    <VideoCardGrid
        :videos="videos"
        :title="title"
        :description="description ?? `Browsing videos under ` + title"
        :has_prev_page
        :has_next_page />
</template>
