<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Link } from "@inertiajs/vue3"
import VideoCardList from "@/organisms/VideoCardList.vue"
import Topics from "@/organisms/Topics.vue"

const props = defineProps({
    livestreams: {
        type: Array,
    },
    latest_videos: {
        type: Array,
    },
    topics_data: {
        type: Object,
    },
})
</script>

<template>
    <VideoCardList
        :videos="livestreams"
        title="Watch Live"
        description="We're live! Check out the current live streams below." />
    <VideoCardList
        :videos="latest_videos"
        title="Latest Videos"
        description="Watch our most recent videos here." />
    <Topics :topics_data="topics_data" />
</template>
