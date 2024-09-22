<script setup>
import VideoCard from "@/Organisms/VideoCard.vue"
import "vue3-carousel/dist/carousel.css"
import { Carousel, Slide, Pagination, Navigation } from "vue3-carousel"

const breakpoints = {
    // 700px and up
    700: {
        itemsToShow: 2.5,
    },
}

defineProps({
    videos: {
        type: Array,
        required: true,
    },
})
</script>

<template>
    <div class="h-[200px]">
        <carousel :items-to-show="1.5" :breakpoints="breakpoints">
            <slide
                v-for="(video, videoIndex) in [...videos, {}]"
                :key="videoIndex">
                <div class="w-full p-2 h-full">
                    <video-card
                        v-if="videoIndex < videos.length"
                        :video="video" />
                    <div v-else class="bg-gray-100 h-full flex items-center justify-center rounded-lg">
                      <button class="text-lg">See more</button>
                    </div>
                </div>
            </slide>

            <template #addons>
                <navigation />
                <pagination />
            </template>
        </carousel>
    </div>
</template>
