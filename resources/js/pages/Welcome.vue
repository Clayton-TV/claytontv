<script setup>
import { Link } from '@inertiajs/vue3';
import VideoCardList from '@/organisms/VideoCardList.vue';
import CategoriesBrowseWidget from '@/organisms/CategoriesBrowseWidget.vue';

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
    <div v-if="livestreams?.length">
        <VideoCardList
            :videos="livestreams"
            description="We're live! Check out the current live streams below."
            title="Watch Live"
            class="flex justify-center"
        />
        <Link href="/livestreams" class="mx-auto flex w-fit">
            <button class="w-auto cursor-pointer rounded-md bg-blue-950 p-3">Browse All</button>
        </Link>
    </div>
    <VideoCardList :videos="latest_videos" description="Watch our most recent videos here." title="Latest Videos" />
    <Link href="/latest" class="flex w-fit mx-auto">
        <button class="bg-blue-950 w-auto rounded-md p-3 mb-4 cursor-pointer">
            Browse All
        </button>
    </Link>
    <CategoriesBrowseWidget :categories_data="topics_data" title="Explore Topics" description="There are a variety of topics for you to discover" categories_sort_order="alphabetical" subcategories_sort_order="count" single_parent_category />
    <CategoriesBrowseWidget :categories_data="series_data" title="Explore Series" description="Browse all series, or filter by ministry" categories_sort_order="alphabetical" subcategories_sort_order="count" />
</template>
