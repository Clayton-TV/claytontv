<script setup lang="ts">
import VideoCardItem from '@/atoms/VideoCardItem.vue';
import { Link, router } from '@inertiajs/vue3';
defineProps({
    videos: {
        type: Array as () => Record<string, any>[],
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
    const curPage = parseInt(window.location.search.match(pageRegex)?.[1] ?? '');
    router.get('#', { page: isNaN(curPage) || curPage <= 1 ? 1 : curPage - 1 });
};

const nextPage = () => {
    const pageRegex = /[?&]page=([0-9]+).*/;
    const curPage = parseInt(window.location.search.match(pageRegex)?.[1] ?? '');
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
            <ul class="gridl-cols-1 grid gap-4 overflow-x-auto px-4 sm:grid-cols-2 lg:grid-cols-3 lg:px-8">
                <li
                    v-for="video in videos"
                    :key="video.id"
                    class="relative isolate mx-auto aspect-video max-h-[60dvh] w-full max-w-[90vw] hover:opacity-75"
                >
                    <Link :href="`/video/` + video.id" :id="video.id" class="contents">
                        <VideoCardItem :video="video" />
                        <span class="sr-only"> View video for {{ video.name }} </span>
                    </Link>
                </li>
            </ul>
        </div>

        <div class="flex">
            <button
                class="mr-2 ml-auto w-auto cursor-pointer rounded-md bg-blue-950 p-2 opacity-50 enabled:opacity-100 disabled:cursor-default"
                @click="prevPage()"
                :disabled="!has_prev_page"
            >
                Prev Page
            </button>
            <button
                class="mr-auto ml-2 w-auto cursor-pointer rounded-md bg-blue-950 p-2 opacity-50 enabled:opacity-100 disabled:cursor-default"
                @click="nextPage()"
                :disabled="!has_next_page"
            >
                Next Page
            </button>
        </div>
    </section>
</template>

<style scoped></style>
