<script setup>
import { computed } from "vue"

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
            <h2 class="text-center text-3xl font-bold">Watch Live</h2>
            <p class="text-center text-sm text-gray-400">
                We're live! Check out the current <br />
                live streams below.
            </p>
        </div>

        <div class="w-full overflow-x-hidden">
            <ul class="flex snap-x snap-mandatory gap-x-4 overflow-x-auto px-2">
                <li
                    v-for="video in livestreams"
                    :key="video.id"
                    class="shrink-0 snap-center overflow-clip rounded-md bg-gray-700">
                    <div
                        class="flex aspect-[10/16] max-h-[60dvh] w-auto max-w-[86vw] flex-col justify-end p-2">
                        <h3 class="text-gray-100 font-bold text-2xl truncate">
                            10:30 AM Sunday 20th Oct
                        </h3>
                        <p class="text-sm line-clamp-2">
                            {{ video.name }}
                        </p>
                    </div>
                </li>
            </ul>
        </div>
    </section>
</template>
