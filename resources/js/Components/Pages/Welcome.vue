<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Link } from "@inertiajs/vue3"
import VideoCardList from "@/Organisms/VideoCardList.vue"

const props = defineProps({
    livestreams: {
        type: Array,
    },
    latest_videos: {
        type: Array,
        required: true,
    },
    pagenum_livestreams: {
        type: Number,
    },
    pagenum_latestvids: {
        type: Number,
    },
    num_pages_livestreams: {
        type: Number,
    },
    num_pages_latestvids: {
        type: Number,
    },
})
</script>

<template>
    <VideoCardList :videos="livestreams" title="Watch Live" description="We're live! Check out the current live streams below." is_livestreams id="livestreams" :page="pagenum_livestreams" :num_pages="num_pages_livestreams" />
    <VideoCardList :videos="latest_videos" title="Latest Videos" description="Watch our most recent videos here." id="latestvids" :page="pagenum_latestvids" :num_pages="num_pages_latestvids" />
</template>
