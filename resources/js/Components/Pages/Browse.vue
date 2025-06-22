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
})
</script>

<template>
    <!-- Something here to allow the user to navigate to the linked topics, maybe a bit like a breadcrumb trail -->
    <VideoCardGrid
        :videos="videos"
        :title="title"
        :description="description ?? `Browsing videos under ` + title" />
</template>
