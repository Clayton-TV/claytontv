<script setup>
import VideoCardItem from '@/atoms/VideoCardItem.vue';
import SectionHeading from '@/molecules/SectionHeading.vue';
import ShareButton from '@/molecules/ShareButton.vue';
import VideoViewer from '@/organisms/VideoViewer.vue';
import { Skeleton } from '@/ui/skeleton';
import { Deferred, Head, Link } from '@inertiajs/vue3';
import { IconBook, IconFileText, IconHeadphones } from '@tabler/icons-vue';
import { watch as vueWatch } from 'vue';
import { useWatchHistory } from '~/composables/useWatchHistory';

const props = defineProps({
    video: { type: Object, required: true },
    video_metadata: { type: Object, required: false, default: () => ({}) },
    passage: { type: Object, required: false, default: null },
    resources: { type: Array, required: false, default: () => [] },
    up_next: { type: Object, required: false, default: null },
});

// Remember that this video has been opened (localStorage; no accounts).
// Re-fires on SPA navigation between watch pages, where the component is reused.
const { markWatched } = useWatchHistory();
markWatched(props.video.id);
vueWatch(
    () => props.video.id,
    (id) => markWatched(id),
);

const resourceMeta = {
    transcript: { label: 'Read the transcript', icon: IconFileText },
    audio: { label: 'Listen to the audio', icon: IconHeadphones },
    other: { label: 'Related resource', icon: IconFileText },
};

// Ordered, labelled metadata groups; absent keys simply don't render.
const metaGroups = [
    { key: 'speaker', label: 'Speakers' },
    { key: 'series', label: 'Series' },
    { key: 'topic', label: 'Topics' },
    { key: 'bible_book', label: 'Bible books' },
    { key: 'ministry', label: 'Ministry' },
    { key: 'demographic', label: 'For' },
];

const entries = (key) => {
    const value = props.video_metadata?.[key];
    if (!value) return [];
    return Array.isArray(value) ? value : [value];
};
</script>

<template>
    <Head :title="video.name" />
    <div class="mx-auto max-w-5xl px-4 py-8 lg:px-8">
        <VideoViewer :video="video" />

        <div class="mt-6">
            <div class="flex flex-wrap items-center gap-x-3 gap-y-2">
                <h1 class="font-display text-2xl leading-tight font-bold text-gray-50 sm:text-3xl">{{ video.name }}</h1>
                <Link
                    v-if="passage"
                    :href="passage.url"
                    prefetch
                    class="bg-primary/15 text-primary focus-visible:ring-ring hover:bg-primary/25 inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-sm font-semibold tabular-nums transition-colors duration-150 outline-none focus-visible:ring-2"
                >
                    <IconBook class="h-4 w-4" aria-hidden="true" />
                    {{ passage.label }}
                </Link>
                <span v-if="video.is_livestream" class="rounded bg-white/10 px-2 py-0.5 text-xs font-bold tracking-wide text-gray-300 uppercase">
                    Streamed
                </span>
            </div>
            <div class="mt-2 flex flex-wrap items-center justify-between gap-3">
                <p class="text-sm text-gray-500 tabular-nums">
                    {{ video.date_recorded ? `Recorded ${video.date_recorded}` : `Added ${video.date_created}` }}
                </p>
                <ShareButton :title="video.name" />
            </div>

            <div class="mt-5 space-y-3">
                <template v-for="group in metaGroups" :key="group.key">
                    <div v-if="entries(group.key).length" class="flex flex-wrap items-baseline gap-2">
                        <span class="w-24 shrink-0 text-xs font-medium tracking-wider text-gray-500 uppercase">{{ group.label }}</span>
                        <Link
                            v-for="entry in entries(group.key)"
                            :key="entry.url"
                            :href="entry.url"
                            prefetch
                            class="focus-visible:ring-ring inline-flex min-h-9 items-center rounded-full border border-white/10 px-3.5 text-[13px] text-gray-300 transition-colors duration-150 outline-none hover:border-white/25 hover:text-white focus-visible:ring-2"
                        >
                            {{ entry.name }}
                        </Link>
                    </div>
                </template>
            </div>

            <p v-if="video.description" class="mt-6 max-w-prose text-[15px] leading-relaxed text-gray-400" v-html="video.description"></p>

            <!-- Rescued companion links (transcripts/audio on partner sites) -->
            <div v-if="resources.length" class="mt-6 flex flex-wrap gap-3">
                <a
                    v-for="resource in resources"
                    :key="resource.url"
                    :href="resource.url"
                    rel="noopener"
                    target="_blank"
                    class="focus-visible:ring-ring inline-flex min-h-11 items-center gap-2 rounded-lg border border-white/15 px-4 text-sm font-medium text-gray-200 transition-colors duration-150 outline-none hover:border-white/30 hover:text-white focus-visible:ring-2"
                >
                    <component :is="(resourceMeta[resource.kind] || resourceMeta.other).icon" class="h-4 w-4" aria-hidden="true" />
                    {{ (resourceMeta[resource.kind] || resourceMeta.other).label }}
                </a>
            </div>
        </div>

        <Deferred data="up_next">
            <template #fallback>
                <section class="mt-12" aria-label="More in this series">
                    <Skeleton class="h-7 w-64 bg-white/5" />
                    <div class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                        <Skeleton v-for="n in 3" :key="n" class="aspect-video rounded-lg bg-white/5" />
                    </div>
                </section>
            </template>

            <section v-if="up_next?.videos?.length" class="mt-12" aria-label="More in this series">
                <SectionHeading :title="`More in ${up_next.series.name}`" :more-href="up_next.series.url" more-label="Whole series" />
                <ul class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                    <li v-for="item in up_next.videos" :key="item.id" class="relative isolate aspect-video">
                        <Link
                            :href="`/video/${item.id}`"
                            prefetch
                            class="focus-visible:ring-ring block h-full w-full rounded-lg transition-transform duration-200 ease-out outline-none hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
                        >
                            <VideoCardItem :video="item" />
                            <span class="sr-only">View video for {{ item.name }}</span>
                        </Link>
                    </li>
                </ul>
            </section>
        </Deferred>
    </div>
</template>
