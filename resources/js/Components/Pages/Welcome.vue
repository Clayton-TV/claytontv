<script setup>
import { computed } from "vue"
import {IconCircleFilled} from "@tabler/icons-vue"

const props = defineProps({
    videos: {
        type: Array,
    },
})

const livestreams = computed(() => {
    return props.videos.filter((video) => video.is_livestream)
})
</script>

<template>
    <section class="my-10 flex flex-col items-center gap-y-6">
        <div class="space-y-2">
            <h2 class="text-center text-3xl text-gray-100 font-bold">Watch Live</h2>
            <p class="text-center text-sm text-gray-400">
                We're live! Check out the current <br />
                live streams below.
            </p>
        </div>

        <div class="w-full overflow-x-hidden mt-2">
            <ul class="flex snap-x snap-mandatory gap-x-4 overflow-x-auto px-2">
                <li
                    v-for="video in livestreams"
                    :key="video.id"
                    class="shrink-0 snap-center overflow-clip rounded-md bg-gradient-to-br from-gray-700 to-gray-900 mb-3">
                    <div
                        class="flex gap-y-2 aspect-[10/16] md:aspect-video w-auto max-w-[90vw] max-h-[78dvh] flex-col justify-end px-3.5 py-5">
                        <p class="flex gap-x-1.5 items-center text-xs font-bold tracking-wide uppercase bg-claytonRed rounded w-fit px-2 py-1">
                             <span class="relative">
                                 <IconCircleFilled class="absolute opacity-50 animate-ping h-3 w-3" />
                                 <IconCircleFilled class="h-3 w-3" />
                             </span>
                            <span class="pb-[1.5px]">Live</span>
                        </p>
                        <h3
                            class="line-clamp-2 text-2xl font-bold text-gray-100">
                            {{ video.name }}
                        </h3>
                        <p class="line-clamp-1 truncate text-sm text-gray-300">
                            10:30 AM Sunday 20th Oct
                        </p>
                    </div>
                </li>
            </ul>
        </div>
    </section>
</template>
