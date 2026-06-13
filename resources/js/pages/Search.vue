<script setup>
import VideoCardGrid from '@/organisms/VideoCardGrid.vue';
import { Head, Link } from '@inertiajs/vue3';

const props = defineProps({
    categories: {
        type: Array,
        default: () => [],
    },
    videos: {
        type: Array,
    },
    title: {
        type: String,
    },
    description: {
        type: String,
    },
    has_prev_page: {
        type: Boolean,
    },
    has_next_page: {
        type: Boolean,
    },
});
</script>

<template>
    <Head :title="title" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <h1 class="font-display text-2xl font-bold text-gray-50 sm:text-3xl">{{ title }}</h1>
        <p v-if="description" class="mt-2 text-sm text-gray-500">{{ description }}</p>

        <section v-if="categories?.length" class="mt-8" aria-label="Matching categories">
            <h2 class="text-xs font-medium tracking-wider text-gray-500 uppercase">
                {{ categories.length }} matching {{ categories.length === 1 ? 'category' : 'categories' }}
            </h2>
            <div class="mt-3 flex flex-wrap gap-2.5">
                <Link
                    v-for="category in categories"
                    :key="category.url"
                    :href="category.url"
                    prefetch
                    class="focus-visible:ring-ring inline-flex min-h-11 items-center gap-2 rounded-full border border-white/15 px-4 text-[13px] text-gray-300 transition-colors duration-150 outline-none hover:border-white/30 hover:text-white focus-visible:ring-2"
                >
                    <span>{{ category.name }}</span>
                    <span class="text-xs text-gray-500">{{ category.category }}</span>
                    <span v-if="category.videosCount" class="rounded-full bg-white/10 px-1.5 py-0.5 text-[11px] text-gray-300 tabular-nums">
                        {{ category.videosCount }}
                    </span>
                </Link>
            </div>
        </section>

        <div class="mt-10">
            <VideoCardGrid
                :videos
                :has_prev_page
                :has_next_page
                empty-title="No matching videos"
                empty-message="We couldn't find any videos for that search. Try a different word, a speaker's name, or a Bible book."
            />
        </div>
    </div>
</template>
