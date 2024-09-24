<script setup>
import VideoCard from "@/Organisms/VideoCard.vue"

defineProps({
    videos: {
        type: Array,
        required: true,
    },

    heading: {
        type: String,
        required: false,
    },
})
</script>

<template>
    <h1 class="mb-4 text-4xl font-bold text-gray-800" v-if="heading">
        {{ heading }}
    </h1>
    <ul
        class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-3 xl:gap-x-8"
        role="list">
        <li v-for="video in videos" :key="video.source" class="relative">
            <video-card :video="video" />
        </li>
    </ul>
</template>

<style scoped></style>
