<script setup>
import VideoCardList from '@/Organisms/VideoCardList.vue';
import Topics from '@/Organisms/Topics.vue';

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
});
</script>

<template>
    <VideoCardList :videos="livestreams" description="We're live! Check out the current live streams below." title="Watch Live" />
    <VideoCardList :videos="latest_videos" description="Watch our most recent videos here." title="Latest Videos" />
    <Topics :topics_data="topics_data" />
</template>
