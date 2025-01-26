<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Link } from "@inertiajs/vue3"
import VideoCardList from "@/Organisms/VideoCardList.vue"
import Topics from "@/Organisms/Topics.vue"

const props = defineProps({
    livestreams: {
        type: Array,
    },
    latest_videos: {
        type: Array,
    },
})
</script>

<template>
    <VideoCardList
        :videos="livestreams"
        title="Watch Live"
        description="We're live! Check out the current live streams below."
        is_livestreams />
    <VideoCardList
        :videos="latest_videos"
        title="Latest Videos"
        description="Watch our most recent videos here." />
    <Topics />
</template>
