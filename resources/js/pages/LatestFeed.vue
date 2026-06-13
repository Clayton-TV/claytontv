<script setup>
import VideoCardItem from '@/atoms/VideoCardItem.vue';
import PaginationNav from '@/molecules/PaginationNav.vue';
import SeriesFloodRow from '@/molecules/SeriesFloodRow.vue';
import { Head, Link } from '@inertiajs/vue3';
import { computed } from 'vue';
import { useEntrance } from '~/composables/useEntrance';
import { useLastVisit } from '~/composables/useLastVisit';

const { entrance } = useEntrance();

const props = defineProps({
    title: { type: String, required: true },
    groups: { type: Array, required: true },
    page: { type: Number, required: true },
    num_pages: { type: Number, required: true },
    has_prev_page: { type: Boolean, default: false },
    has_next_page: { type: Boolean, default: false },
});

const lastVisit = useLastVisit('latest');

const itemDate = (item) => (item.type === 'series' ? item.latest_date : (item.date_recorded ?? item.date_created));

// The id of the first item already there on the previous visit — the quiet
// "you've seen everything below this" line sits above it. Only meaningful
// when something newer sits above it (ISO dates compare as strings).
const dividerBeforeId = computed(() => {
    if (!lastVisit) return null;
    const all = props.groups.flatMap((group) => group.items);
    const index = all.findIndex((item) => itemDate(item) <= lastVisit);
    return index > 0 ? all[index].id : null;
});
</script>

<template>
    <Head :title="title" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <h1 class="font-display text-2xl font-bold text-gray-50 sm:text-3xl">Latest</h1>
        <p class="mt-2 text-sm text-gray-500">New teaching and recent series, most recent first.</p>

        <section v-for="(group, i) in groups" :key="group.label" v-bind="entrance(80 + i * 70)" class="mt-10" :aria-label="group.label">
            <h2 class="flex items-center gap-3 text-sm font-semibold tracking-wider text-gray-400 uppercase">
                {{ group.label }}
                <span class="h-px flex-1 bg-white/10" aria-hidden="true"></span>
            </h2>

            <ul class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <template v-for="item in group.items" :key="`${item.type}-${item.id}`">
                    <li v-if="item.id === dividerBeforeId" class="col-span-full" aria-hidden="true">
                        <p class="flex items-center gap-3 text-xs font-medium text-gray-500">
                            <span class="bg-primary/40 h-px flex-1" aria-hidden="true"></span>
                            You've seen everything below this
                            <span class="bg-primary/40 h-px flex-1" aria-hidden="true"></span>
                        </p>
                    </li>
                    <li v-if="item.type === 'series'" class="col-span-full">
                        <SeriesFloodRow :item="item" />
                    </li>
                    <li v-else class="relative isolate aspect-video">
                        <Link
                            :href="`/video/${item.id}`"
                            prefetch
                            class="focus-visible:ring-ring block h-full w-full rounded-lg transition-transform duration-200 ease-out outline-none hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
                        >
                            <VideoCardItem :video="item" />
                            <span class="sr-only">View video for {{ item.name }}</span>
                        </Link>
                    </li>
                </template>
            </ul>
        </section>

        <p v-if="num_pages > 1" class="mt-10 text-center text-xs text-gray-500 tabular-nums">Page {{ page }} of {{ num_pages }}</p>
        <div class="mt-4">
            <PaginationNav :has-prev-page="has_prev_page" :has-next-page="has_next_page" />
        </div>
    </div>
</template>
