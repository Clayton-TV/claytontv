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
    <section class="flex flex-col gap-y-6">
        <div v-if="title || description">
            <h1 v-if="title" class="font-display text-2xl font-bold text-gray-50 sm:text-3xl">
                {{ title }}
            </h1>
            <p v-if="description" class="mt-2 text-sm text-gray-500" v-html="description"></p>
        </div>

        <ul class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <li v-for="video in videos" :key="video.id" class="relative isolate aspect-video">
                <Link
                    :href="`/video/` + video.id"
                    :id="video.id"
                    prefetch
                    class="focus-visible:ring-ring block h-full w-full rounded-lg transition-transform duration-200 ease-out outline-none hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
                >
                    <VideoCardItem :video="video" />
                    <span class="sr-only"> View video for {{ video.name }} </span>
                </Link>
            </li>
        </ul>

        <nav v-if="has_prev_page || has_next_page" class="flex justify-center gap-x-3" aria-label="Pagination">
            <button
                class="focus-visible:ring-ring min-h-11 cursor-pointer rounded-lg border border-white/15 px-5 text-sm font-medium text-gray-200 transition-colors duration-150 outline-none hover:border-white/30 hover:text-white focus-visible:ring-2 disabled:cursor-default disabled:opacity-35 disabled:hover:border-white/15"
                @click="prevPage()"
                :disabled="!has_prev_page"
            >
                Previous
            </button>
            <button
                class="focus-visible:ring-ring min-h-11 cursor-pointer rounded-lg border border-white/15 px-5 text-sm font-medium text-gray-200 transition-colors duration-150 outline-none hover:border-white/30 hover:text-white focus-visible:ring-2 disabled:cursor-default disabled:opacity-35 disabled:hover:border-white/15"
                @click="nextPage()"
                :disabled="!has_next_page"
            >
                Next
            </button>
        </nav>
    </section>
</template>

<style scoped></style>
