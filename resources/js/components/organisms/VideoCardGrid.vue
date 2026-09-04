<script setup>
import VideoCardItem from '@/atoms/VideoCardItem.vue';
import EmptyState from '@/molecules/EmptyState.vue';
import PaginationNav from '@/molecules/PaginationNav.vue';
import { Link } from '@inertiajs/vue3';
import { useEntrance } from '~/composables/useEntrance';
import { EVENTS, track } from '~/lib/analytics';

const { entrance } = useEntrance();
const props = defineProps({
    videos: {
        type: Array,
        required: true,
    },
    // When this grid shows search results, set track-context="search" (+ track-query)
    // to emit search_result_clicked with the clicked result's rank/position.
    trackContext: {
        type: String,
        default: '',
    },
    trackQuery: {
        type: String,
        default: '',
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
    num_pages: {
        type: Number,
    },
    emptyTitle: {
        type: String,
        default: 'Nothing here yet',
    },
    emptyMessage: {
        type: String,
        default: 'There are no videos to show. Try browsing the latest teaching or another part of the library.',
    },
});

// Only emits when rendered as search results (track-context="search"); position
// is 1-based rank within the current page so we can see which ranks get clicked.
const onResultClick = (video, index) => {
    if (props.trackContext !== 'search') return;
    const currentPage = parseInt(window.location.search.match(/[?&]page=([0-9]+)/)?.[1]) || 1;
    track(EVENTS.searchResultClicked, {
        query: props.trackQuery,
        result_position: index + 1, // 1-based rank within this page…
        result_page: currentPage, // …disambiguated by page (rank is page-local)
        result_video_id: video.id,
        page_results_count: props.videos.length,
    });
};
</script>

<template>
    <section v-bind="entrance()" class="flex flex-col gap-y-6">
        <div v-if="title || description">
            <h1 v-if="title" class="font-display text-foreground text-2xl font-bold sm:text-3xl">
                {{ title }}
            </h1>
            <p v-if="description" class="text-muted-foreground mt-2 text-sm" v-html="description"></p>
        </div>

        <EmptyState v-if="!videos.length" :title="emptyTitle" :message="emptyMessage" cta-href="/latest" cta-label="Browse the latest teaching" />

        <ul v-else class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <li v-for="(video, index) in videos" :key="video.id" class="relative isolate aspect-video">
                <Link
                    :href="`/video/` + video.id"
                    :id="video.id"
                    prefetch
                    class="focus-visible:ring-ring focus-visible:ring-offset-background block h-full w-full rounded-lg transition-transform duration-200 ease-out outline-none hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-offset-2 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
                    @click="onResultClick(video, index)"
                >
                    <VideoCardItem :video="video" />
                    <span class="sr-only"> View video for {{ video.name }} </span>
                </Link>
            </li>
        </ul>

        <div class="mt-10">
            <PaginationNav :num-pages="num_pages" :has-prev-page="has_prev_page" :has-next-page="has_next_page" />
        </div>
    </section>
</template>

<style scoped></style>
