<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Link } from "@inertiajs/vue3"
defineProps({
    video: {
        type: Object,
        required: true,
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
    <div class="absolute inset-0 place-self-center">
        <div
            class="group flex h-min w-min cursor-pointer items-center justify-center rounded-full p-2 hover:bg-gray-100/20">
            <IconPlayerPlay
                class="h-14 w-14 stroke-1 text-gray-100"/>
        </div>
    </div>


    <div class="flex flex-col px-2.5 py-3.5 sm:px-3.5 sm:py-5 gap-y-1">
        <p
            class="flex w-fit items-center gap-x-1.5 rounded bg-claytonRed/90 px-1.5 py-0.5 sm:px-2 sm:py-1 text-xs font-bold uppercase tracking-wide" v-if="video.is_livestream">
            <span class="relative flex h-2.5 w-2.5">
                <span
                    class="absolute h-full w-full animate-ping inline-flex opacity-50 bg-white rounded-full" />
                <span class="h-full w-full inline-flex relative bg-white rounded-full" />
            </span>
            <span class="pb-[1.5px]">Live</span>
        </p>
        <h3
            class="line-clamp-1 text-lg leading-snug sm:text-2xl font-bold text-gray-100">
            {{ video.name }}
        </h3>
        <p class="line-clamp-1 truncate text-sm text-gray-400">
            10:30 AM Sunday 20th Oct
        </p>
    </div>
</template>

<style scoped></style>
