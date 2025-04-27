<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Link } from "@inertiajs/vue3"
import VideoCardList from "@/Organisms/VideoCardList.vue"
import CategoriesBrowseWidget from "@/Organisms/CategoriesBrowseWidget.vue"

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
    series_data: {
        type: Object,
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
    <CategoriesBrowseWidget :categories_data="topics_data" title="Explore Topics" description="There are a variety of topics for you to discover" single_parent_category />
    <CategoriesBrowseWidget :categories_data="series_data" title="Explore Series" description="Browse all series, or filter by ministry" />
</template>
