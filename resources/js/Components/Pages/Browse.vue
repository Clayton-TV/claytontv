<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Link } from "@inertiajs/vue3"
import VideoCardList from "@/Organisms/VideoCardList.vue"
import Topics from "@/Organisms/Topics.vue"

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
    <VideoCardList
        :videos="videos"
        :title="title"
        :description="description ?? `Browsing videos under ` + title" />
</template>
