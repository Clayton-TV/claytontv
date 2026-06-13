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
        <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">{{ title }}</h1>
        <p v-if="description" class="text-muted-foreground mt-2 text-sm">{{ description }}</p>

        <section v-if="categories?.length" class="mt-8" aria-label="Matching categories">
            <h2 class="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                {{ categories.length }} matching {{ categories.length === 1 ? 'category' : 'categories' }}
            </h2>
            <div class="mt-3 flex flex-wrap gap-2.5">
                <Link
                    v-for="category in categories"
                    :key="category.url"
                    :href="category.url"
                    prefetch
                    class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground inline-flex min-h-11 items-center gap-2 rounded-full border px-4 text-[13px] transition-colors duration-150 outline-none focus-visible:ring-2"
                >
                    <span>{{ category.name }}</span>
                    <span class="text-muted-foreground text-xs">{{ category.category }}</span>
                    <span v-if="category.videosCount" class="bg-muted text-foreground rounded-full px-1.5 py-0.5 text-[11px] tabular-nums">
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
