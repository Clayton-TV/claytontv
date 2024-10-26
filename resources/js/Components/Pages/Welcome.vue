<script setup>
import { computed } from "vue"
import { IconCircleFilled, IconPlayerPlay } from "@tabler/icons-vue"

const props = defineProps({
    videos: {
        type: Array,
    },
})

const livestreams = computed(() => {
    return props.videos.filter((video) => video.is_livestream)
})

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

    // Show the video in fullscreen
    video.requestFullscreen()

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
            <h2 class="text-center text-3xl font-bold text-gray-100">
                Watch Live
            </h2>
            <p class="text-center text-gray-400">
                We're live! Check out the current <br />
                live streams below.
            </p>
        </div>

        <div class="mt-2 w-full overflow-x-hidden">
            <ul class="flex snap-x snap-mandatory gap-x-4 overflow-x-auto px-2">
                <li
                    v-for="video in livestreams"
                    :key="video.id"
                    class="relative mb-3 shrink-0 snap-center overflow-clip rounded-md bg-gradient-to-br from-gray-700 to-gray-900">
                    <video
                        :id="video.id"
                        :src="video.url"
                        class="absolute inset-0 h-full w-full rounded-md object-cover"
                        poster=""></video>
                    <div
                        class="relative isolate flex aspect-[10/16] max-h-[78dvh] w-auto max-w-[90vw] flex-col justify-end gap-y-2 px-3.5 py-5 md:aspect-video">
                        <div class="absolute inset-0 place-self-center">
                            <div
                                class="group flex h-min w-min cursor-pointer items-center justify-center rounded-full p-2 hover:bg-gray-100/20">
                                <IconPlayerPlay
                                    @click="playVideo(video.id)"
                                    class="h-14 w-14 stroke-1 text-gray-100" />
                            </div>
                        </div>
                        <p
                            class="flex w-fit items-center gap-x-1.5 rounded bg-claytonRed px-2 py-1 text-xs font-bold uppercase tracking-wide">
                            <span class="relative">
                                <IconCircleFilled
                                    class="absolute h-3 w-3 animate-ping opacity-50" />
                                <IconCircleFilled class="h-3 w-3" />
                            </span>
                            <span class="pb-[1.5px]">Live</span>
                        </p>
                        <h3
                            class="line-clamp-2 text-2xl font-bold text-gray-100">
                            {{ video.name }}
                        </h3>
                        <p class="line-clamp-1 truncate text-sm text-gray-400">
                            10:30 AM Sunday 20th Oct
                        </p>
                    </div>
                </li>
            </ul>
        </div>
    </section>
</template>
