<script setup lang="ts">
import CategoriesBrowseWidget from '@/organisms/CategoriesBrowseWidget.vue';
import VideoCardList from '@/organisms/VideoCardList.vue';
import { Link } from '@inertiajs/vue3';

defineProps({
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
});
</script>

<template>
    <VideoCardList :videos="livestreams" description="We're live! Check out the current live streams below." title="Watch Live" />
    <Link href="/livestreams" class="mx-auto flex w-fit">
        <button class="w-auto cursor-pointer rounded-md bg-blue-950 p-3">Browse All</button>
    </Link>
    <VideoCardList :videos="latest_videos" description="Watch our most recent videos here." title="Latest Videos" />
    <Link href="/latest" class="mx-auto flex w-fit">
        <button class="w-auto cursor-pointer rounded-md bg-blue-950 p-3">Browse All</button>
    </Link>
    <CategoriesBrowseWidget
        :categories_data="topics_data"
        title="Explore Topics"
        description="There are a variety of topics for you to discover"
        single_parent_category
    />
    <CategoriesBrowseWidget :categories_data="series_data" title="Explore Series" description="Browse all series, or filter by ministry" />
</template>
