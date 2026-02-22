<script setup lang="ts">
import VideoCardItem from '@/atoms/VideoCardItem.vue';
import { Link } from '@inertiajs/vue3';
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
});
</script>

<template>
    <section class="mt-10 mb-4 flex flex-col items-center gap-y-6">
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
                    class="relative isolate mb-3 aspect-[10/16] max-h-[42lvh] max-w-[90lvw] shrink-0 snap-center hover:opacity-75 md:aspect-video"
                >
                    <Link :href="`/video/` + video.id" :id="video.id" class="contents">
                        <VideoCardItem :video="video" />
                        <span class="sr-only"> View video for {{ video.name }} </span>
                    </Link>
                </li>
            </ul>
        </div>
    </section>
</template>

<style scoped></style>
