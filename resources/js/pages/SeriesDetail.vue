<script setup>
import EpisodeRow from '@/molecules/EpisodeRow.vue';
import PaginationNav from '@/molecules/PaginationNav.vue';
import { Head, Link } from '@inertiajs/vue3';
import { BookOpen, Play } from 'lucide-vue-next';

const props = defineProps({
    series_meta: { type: Object, required: true },
    episodes: { type: Array, default: () => [] },
    start_url: { type: String, default: null },
    page_start: { type: Number, default: 0 },
    has_prev_page: { type: Boolean },
    has_next_page: { type: Boolean },
    num_pages: { type: Number },
});

// Whole-series runtime as a rounded "Xh Ym" / "Ym" — a course-length cue.
const totalRuntime = () => {
    const seconds = props.series_meta.total_runtime;
    if (!seconds) return null;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.round((seconds % 3600) / 60);
    return hours ? `${hours}h ${minutes}m` : `${minutes}m`;
};

const looksLikeYear = (value) => /^\d{4}$/.test(String(value ?? '').trim());

const years = () => {
    const { year_start: start, year_end: end } = props.series_meta;
    if (!looksLikeYear(start)) return null;
    return looksLikeYear(end) && end !== start ? `${start}–${end}` : start;
};

// Episode number where the data has one; otherwise the running row index.
const positionFor = (episode, index) => episode.number ?? props.page_start + index + 1;
</script>

<template>
    <Head :title="series_meta.name" />
    <div class="mx-auto max-w-4xl px-4 py-10 lg:px-8">
        <header class="flex flex-col gap-6 sm:flex-row sm:items-start">
            <div class="bg-primary/10 flex h-24 w-24 flex-none items-center justify-center rounded-2xl" aria-hidden="true">
                <BookOpen class="text-primary h-10 w-10 stroke-[1.5]" />
            </div>
            <div class="min-w-0">
                <p class="text-primary text-xs font-semibold tracking-[0.12em] uppercase">Series</p>
                <h1 class="font-display text-foreground mt-1 text-2xl leading-tight font-bold sm:text-3xl">{{ series_meta.name }}</h1>
                <p class="text-muted-foreground mt-2 text-sm tabular-nums">
                    {{ series_meta.videosCount }} {{ series_meta.videosCount === 1 ? 'episode' : 'episodes' }}
                    <template v-if="totalRuntime()"> · {{ totalRuntime() }}</template>
                    <template v-if="years()"> · {{ years() }}</template>
                </p>
                <p v-if="series_meta.summary" class="text-muted-foreground mt-3 max-w-prose text-[15px] leading-relaxed">
                    {{ series_meta.summary }}
                </p>
                <Link
                    v-if="start_url"
                    :href="start_url"
                    prefetch
                    class="bg-primary text-primary-foreground focus-visible:ring-ring hover:bg-primary/90 focus-visible:ring-offset-background mt-4 inline-flex min-h-11 items-center gap-2 rounded-lg px-5 text-sm font-semibold transition-colors duration-150 outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
                >
                    <Play class="h-4 w-4" aria-hidden="true" fill="currentColor" />
                    Start from the beginning
                </Link>
            </div>
        </header>

        <section class="mt-10" aria-label="Episodes">
            <ol class="space-y-2.5">
                <li v-for="(episode, index) in episodes" :key="episode.id">
                    <EpisodeRow :episode="episode" :position="positionFor(episode, index)" />
                </li>
            </ol>
        </section>

        <div class="mt-10">
            <PaginationNav :num-pages="num_pages" :has-prev-page="has_prev_page" :has-next-page="has_next_page" />
        </div>
    </div>
</template>
