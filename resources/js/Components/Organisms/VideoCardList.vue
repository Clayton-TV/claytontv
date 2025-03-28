<script setup>
import { computed } from "vue"
import { IconPlayerPlay } from "@tabler/icons-vue"
import { Link } from "@inertiajs/vue3"
import VideoCardItem from "@/Atoms/VideoCardItem.vue"
defineProps({
    videos: {
        type: Array,
        required: true,
    },
    is_livestreams: {
      type: Boolean,
      required: false,
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

const playVideo = (id) => {
    const video = document.getElementById(id)

    if (!video) {
        console.log("Video not found")
        return
    }

    // Play the video
    video.play()

    // Show controls when video is playing
    video.controls = true

    // Pause other videos
    const videos = document.querySelectorAll("video")
    videos.forEach((v) => {
        if (v.id !== id) {
            v.pause()
            v.controls = false
        }
    })

    // Scroll to the video
    video.scrollIntoView({ behavior: "smooth", block: "center" })

    // Add event listener to exit fullscreen
    document.addEventListener("fullscreenchange", () => {
        if (!document.fullscreenElement) {
            video.pause()
            video.controls = false
        }
    })

    // Add event listener to pause video when it ends
    video.addEventListener("ended", () => {
        video.controls = false
    })
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
            <ul class="flex snap-x snap-mandatory gap-x-4 overflow-x-auto px-2">
                <li
                    v-for="video in videos"
                    :key="video.id"
                    class="relative isolate mb-3 flex aspect-[10/16] max-h-[42dvh] w-auto max-w-[90vw] shrink-0 snap-center flex-col justify-end gap-y-2 rounded-md bg-gradient-to-br from-gray-700 to-gray-900 md:aspect-video hover:opacity-75">
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
