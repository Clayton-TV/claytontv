<script setup>
import VideoCardGrid from '@/organisms/VideoCardGrid.vue';
import { Head, Link, usePage } from '@inertiajs/vue3';
import { computed, watch } from 'vue';
import { EVENTS, track } from '~/lib/analytics';

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

// The query lives in the ?search= param (set by CommandPalette). usePage().url is
// reactive, so this recomputes on every Inertia navigation — including a repeat
// search from the global palette that REUSES this page component (no remount).
const inertiaPage = usePage();
const query = computed(() => {
    const searchValues = new URLSearchParams(inertiaPage.url.split('?')[1] ?? '').getAll('search');
    return (searchValues.at(-1) ?? '').trim();
});

// Fire search_performed when the search TERM changes (initial load + each new
// search) but not on pagination — paging changes ?page=, not ?search=. Search is
// server-routed, so results_count is the current page's video count; zero-results
// (no videos AND no categories) is the key content-gap signal for P3.
watch(
    query,
    (q) => {
        if (!q) return;

        const videoCount = props.videos?.length ?? 0;
        const categoryCount = props.categories?.length ?? 0;
        track(EVENTS.searchPerformed, {
            query: q,
            results_count: videoCount,
            category_count: categoryCount,
            is_zero_results: videoCount === 0 && categoryCount === 0,
        });
    },
    { immediate: true },
);

const emptyTitle = computed(() => (query.value ? 'No matching videos' : 'Nothing to show yet'));
const emptyMessage = computed(() =>
    query.value
        ? "We couldn't find any videos for that search. Try a different word, a speaker's name, or a Bible book."
        : "Use the search box at the top of the page to look for a word, a speaker's name, a series, or a Bible book.",
);
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
                track-context="search"
                :track-query="query"
                :empty-title="emptyTitle"
                :empty-message="emptyMessage"
            />
        </div>
    </div>
</template>
