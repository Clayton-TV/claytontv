<script setup>
import VideoCardItem from '@/atoms/VideoCardItem.vue';
import { Link, router } from '@inertiajs/vue3';
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
    has_prev_page: {
        type: Boolean,
    },
    has_next_page: {
        type: Boolean,
    },
});

const prevPage = () => {
    const pageRegex = /[?&]page=([0-9]+).*/;
    const curPage = parseInt(window.location.search.match(pageRegex)?.[1]);
    router.get('#', { page: isNaN(curPage) || curPage <= 1 ? 1 : curPage - 1 });
};

const nextPage = () => {
    const pageRegex = /[?&]page=([0-9]+).*/;
    const curPage = parseInt(window.location.search.match(pageRegex)?.[1]);
    router.get('#', { page: isNaN(curPage) ? 2 : curPage + 1 }); // If no page parameter then next page is second not first
};
</script>

<template>
    <section class="mb-10 flex flex-col items-center gap-y-6">
        <div class="space-y-2">
            <h2 class="mt-8 text-center text-3xl font-bold text-gray-100" v-if="title">
                {{ title }}
            </h2>
            <p class="mt-2 text-center text-gray-400" v-if="description" v-html="description"></p>
        </div>

        <div class="mt-2 w-full overflow-x-hidden">
            <ul class="grid grid-cols-1 gap-4 overflow-x-auto px-4 sm:grid-cols-2 lg:grid-cols-3 lg:px-8">
                <li v-for="video in videos" :key="video.id" class="relative isolate mx-auto aspect-video max-h-[60dvh] w-full max-w-[90vw]">
                    <!-- Link is the block (not display:contents) so keyboard focus can draw a ring -->
                    <Link
                        :href="`/video/` + video.id"
                        :id="video.id"
                        class="focus-visible:ring-ring block h-full w-full rounded-lg transition-transform duration-200 ease-out outline-none hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-black motion-reduce:transition-none motion-reduce:hover:translate-y-0"
                    >
                        <VideoCardItem :video="video" />
                        <span class="sr-only"> View video for {{ video.name }} </span>
                    </Link>
                </li>
            </ul>
        </div>

        <nav class="flex gap-x-4" aria-label="Pagination">
            <button
                class="focus-visible:ring-ring min-h-11 cursor-pointer rounded-md bg-gray-800 px-4 py-2 font-medium text-gray-100 transition-colors duration-150 outline-none hover:bg-gray-700 focus-visible:ring-2 disabled:cursor-default disabled:opacity-40 disabled:hover:bg-gray-800"
                @click="prevPage()"
                :disabled="!has_prev_page"
            >
                Prev Page
            </button>
            <button
                class="focus-visible:ring-ring min-h-11 cursor-pointer rounded-md bg-gray-800 px-4 py-2 font-medium text-gray-100 transition-colors duration-150 outline-none hover:bg-gray-700 focus-visible:ring-2 disabled:cursor-default disabled:opacity-40 disabled:hover:bg-gray-800"
                @click="nextPage()"
                :disabled="!has_next_page"
            >
                Next Page
            </button>
        </nav>
    </section>
</template>

<style scoped></style>
