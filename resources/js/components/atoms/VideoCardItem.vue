<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Link } from "@inertiajs/vue3"
import LogoMark from "@/atoms/LogoMark.vue"
defineProps({
    video: {
        type: Object,
        required: true,
    },
})

const getVideoThumbnail = (video) => {
    if (video.thumbnail?.startsWith("http")) {
        return video.thumbnail
    } else {
        const youtubeRegex = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        const youtubeId = video.url.match(youtubeRegex)?.[2];
        if (youtubeId) {
            // If youtube URL
            // Attempt to split the video ID off the end, then shoehorn it into the thumbnail URL
            return `https://img.youtube.com/vi/${youtubeId}/mqdefault.jpg`
        }
    }
    return null
}
</script>

<template>
    <div class="w-full h-full flex rounded-md bg-gradient-to-br from-gray-700 to-gray-900 group">
        <LogoMark class="fill-primary pointer-events-none place-self-center items-center justify-center absolute inset-0 h-[40%] object-cover opacity-80 group-hover:opacity-55" />

        <img v-if="getVideoThumbnail(video)" :src="getVideoThumbnail(video)" alt="" class="pointer-events-none place-self-center items-center justify-center absolute inset-0 size-full object-cover group-hover:opacity-75 rounded-md" onerror="this.style.opacity='0';" />

        <div class="absolute inset-0 place-self-center group flex h-min w-min cursor-pointer items-center justify-center rounded-full p-2 hover:bg-gray-100/20">
            <IconPlayerPlay class="h-14 w-14 stroke-1 text-gray-100"/>
        </div>

        <div class="flex flex-col px-2.5 py-3.5 sm:px-3.5 w-svw sm:py-2 gap-y-1 place-self-end z-10 rounded-b-md bg-black/60 z-50">
            <h3 class="line-clamp-1 group-hover:line-clamp-3 transition transition-all duration-150 text-lg leading-snug sm:text-2xl font-bold text-white">
                {{ video.name }}
            </h3>
            <div class="flex flex-row justify-between">
                <p class="line-clamp-1 truncate text-sm text-white h-6">
                    {{ video.date_recorded ? "Recorded: " + video.date_recorded : "Added: " + video.date_created }}
                </p>
                <p class="flex w-min items-center gap-x-1.5 rounded bg-red-400/90 px-1.5 py-0.5 sm:px-2 text-xs font-bold uppercase tracking-wide" v-if="video.is_livestream">
                    <span class="relative flex h-2.5 w-2.5">
                        <span class="absolute h-full w-full animate-ping inline-flex opacity-50 bg-white rounded-full" />
                        <span class="h-full w-full inline-flex relative bg-white rounded-full" />
                    </span>
                    <span class="pb-[1.5px]">Live</span>
                </p>
            </div>
        </div>
    </div>

</template>

<style scoped></style>
