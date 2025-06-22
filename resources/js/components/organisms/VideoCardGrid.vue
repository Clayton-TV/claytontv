<script setup>
import { computed } from "vue"
import { Link } from "@inertiajs/vue3"
import VideoCardItem from "@/atoms/VideoCardItem.vue"
defineProps({
    videos: {
        type: Array,
        required: true,
    },
    title: {
        type: String,
        required: false,
    },
    description: {
        type: String,
        required: false,
    },
})

const getVideoThumbnail = (videoUrl) => {
    const youtubeRegex = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const youtubeId = videoUrl.match(youtubeRegex)?.[2];
    if (youtubeId) {
        // If youtube URL
        // Attempt to split the video ID off the end, then shoehorn it into the thumbnail URL
        return `https://img.youtube.com/vi/${youtubeId}/mqdefault.jpg`
    } else {
        return "https://via.placeholder.com/1080x640"
    }
}
</script>

<template>
    <section class="my-10 flex flex-col items-center gap-y-6">
        <div class="space-y-2">
            <h2 class="text-center text-3xl font-bold text-gray-100" v-if="title">
                {{ title }}
            </h2>
            <p class="text-center text-gray-400" v-if="description" v-html="description"></p>
        </div>

        <div class="mt-2 w-full overflow-x-hidden">
            <ul class="grid gridl-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 overflow-x-auto px-4 lg:px-8">
                <li
                    v-for="video in videos"
                    :key="video.id"
                    class="relative isolate max-h-[60dvh] w-full max-w-[90vw] mx-auto aspect-video hover:opacity-75">
                    <Link :href="`/video/`+video.id"
                        :id="video.id"
                        class="contents">
                        <VideoCardItem :video="video" />
                        <span class="sr-only">
                            View video for {{ video.name }}
                        </span>
                    </Link>
                </li>
            </ul>
        </div>
    </section>
</template>

<style scoped></style>
