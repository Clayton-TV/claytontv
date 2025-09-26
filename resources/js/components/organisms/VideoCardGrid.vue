<script setup>
import { computed } from "vue"
import VideoCardItem from "@/atoms/VideoCardItem.vue"
import { Link, router } from "@inertiajs/vue3"
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
    pagination: {
        type: Boolean,
    },
})

const prevPage = () => {
    const pageRegex = /^.page=([0-9]+).*/
    const curPage = parseInt(window.location.search.match(pageRegex)?.[1])
    router.get("#", {"page" : (isNaN(curPage) || curPage <= 1) ? 1 : curPage - 1})
}

const nextPage = () => {
    const pageRegex = /^.page=([0-9]+).*/
    const curPage = parseInt(window.location.search.match(pageRegex)?.[1])
    router.get("#", {"page" : isNaN(curPage) ? 2 : curPage + 1}) // If no page parameter then next page is second not first
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

        <div class="flex" v-if="pagination">
            <button class="bg-blue-950 w-auto rounded-md p-2 ml-auto mr-2" @click="prevPage()">
                Prev Page
            </button>
            <button class="bg-blue-950 w-auto rounded-md p-2 mr-auto ml-2" @click="nextPage()">
                Next Page
            </button>
        </div>
    </section>
</template>

<style scoped></style>
