<script setup>
import VideoCard from "@/Organisms/VideoCard.vue"
import "vue3-carousel/dist/carousel.css"
import {
    Carousel,
    Slide as CarouselSlide,
    Pagination as CarouselPagination,
    Navigation as CarouselNavigation,
} from "vue3-carousel" // Vue3-carousel docs: https://ismail9k.github.io/vue3-carousel/
import { Link } from "@inertiajs/vue3"

const carouselBreakpoints = {
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
        <carousel :items-to-show="1.5" :breakpoints="carouselBreakpoints">
            <carousel-slide
                v-for="(video, videoIndex) in [...videos, {}]"
                :key="videoIndex">
                <div class="h-full w-full p-2">
                    <video-card
                        v-if="videoIndex < videos.length"
                        :video="video" />
                    <div
                        v-else
                        class="flex h-full items-center justify-center rounded-lg bg-gray-100">
                        <Link
                            class="p-5 text-3xl hover:text-gray-500 md:text-5xl"
                            href="/catalogue/">
                            See more...
                        </Link>
                    </div>
                </div>
            </carousel-slide>

            <template #addons>
                <carousel-navigation />
                <carousel-pagination />
            </template>
        </carousel>
    </div>
</template>
