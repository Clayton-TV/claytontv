<script setup>
import PaginationNav from '@/molecules/PaginationNav.vue';
import VideoCardGrid from '@/organisms/VideoCardGrid.vue';
import { Head } from '@inertiajs/vue3';
import { IconBook2 } from '@tabler/icons-vue';

const props = defineProps({
    series_meta: { type: Object, required: true },
    videos: { type: Array, default: () => [] },
    has_prev_page: { type: Boolean },
    has_next_page: { type: Boolean },
});

const looksLikeYear = (value) => /^\d{4}$/.test(String(value ?? '').trim());

const years = () => {
    // Legacy year fields hold free text (e.g. "18--2,2"); only show clean years
    const { year_start: start, year_end: end } = props.series_meta;
    if (!looksLikeYear(start)) return null;
    return looksLikeYear(end) && end !== start ? `${start}–${end}` : start;
};
</script>

<template>
    <Head :title="series_meta.name" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <header class="flex flex-col gap-6 sm:flex-row sm:items-start">
            <div class="bg-primary/10 flex h-24 w-24 flex-none items-center justify-center rounded-2xl" aria-hidden="true">
                <IconBook2 class="text-primary h-10 w-10 stroke-[1.5]" />
            </div>
            <div class="min-w-0">
                <p class="text-primary text-xs font-semibold tracking-[0.12em] uppercase">Series</p>
                <h1 class="font-display mt-1 text-2xl leading-tight font-bold text-gray-50 sm:text-3xl">{{ series_meta.name }}</h1>
                <p class="mt-2 text-sm text-gray-500 tabular-nums">
                    {{ series_meta.videosCount }} {{ series_meta.videosCount === 1 ? 'episode' : 'episodes' }}
                    <template v-if="years()"> · {{ years() }}</template>
                </p>
                <p v-if="series_meta.summary" class="mt-3 max-w-prose text-[15px] leading-relaxed text-gray-400">
                    {{ series_meta.summary }}
                </p>
            </div>
        </header>

        <div class="mt-10">
            <VideoCardGrid :videos="videos" :has_prev_page="false" :has_next_page="false" />
        </div>

        <div class="mt-10">
            <PaginationNav :has-prev-page="has_prev_page" :has-next-page="has_next_page" />
        </div>
    </div>
</template>
