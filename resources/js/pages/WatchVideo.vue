<script setup>
import VideoCardItem from '@/atoms/VideoCardItem.vue';
import SectionHeading from '@/molecules/SectionHeading.vue';
import ShareButton from '@/molecules/ShareButton.vue';
import { Skeleton } from '@/ui/skeleton';
import { Deferred, Head, Link } from '@inertiajs/vue3';
import { Book, FileText, Headphones, RotateCw } from 'lucide-vue-next';
import { onBeforeUnmount, onMounted, ref, watch as vueWatch } from 'vue';
import { usePlayerDock } from '~/composables/usePlayerDock';
import { useWatchHistory } from '~/composables/useWatchHistory';
import { formatDuration } from '~/lib/duration';

const props = defineProps({
    video: { type: Object, required: true },
    video_metadata: { type: Object, required: false, default: () => ({}) },
    passage: { type: Object, required: false, default: null },
    resources: { type: Array, required: false, default: () => [] },
    up_next: { type: Object, required: false, default: null },
});

// This page doesn't own a player. The persistent player (AppLayout) does;
// we hand it the video and register the placeholder it positions over —
// so a video that followed the viewer here as a mini-player just keeps
// playing when they arrive.
const dock = usePlayerDock();
const { resumePoint } = useWatchHistory();

const placeholderEl = ref(null);
const resumedFrom = ref(0);

vueWatch(
    () => props.video.id,
    (id) => {
        const loaded = dock.load(
            { id, name: props.video.name, url: props.video.url },
            // Resume where the viewer left off, baked into the embed URL
            { autoplay: false, startAt: resumePoint(id) },
        );
        // Only mention resuming when this visit actually (re)loaded the player
        resumedFrom.value = loaded ? dock.resumedFrom.value : 0;
    },
    { immediate: true },
);

onMounted(() => dock.setPlaceholder(placeholderEl.value));
onBeforeUnmount(() => dock.setPlaceholder(null));

const startOver = () => {
    dock.controls.value?.seekTo(0);
    dock.controls.value?.play();
    resumedFrom.value = 0;
};

const formatTime = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = Math.floor(totalSeconds % 60);
    return `${minutes}:${String(seconds).padStart(2, '0')}`;
};

const resourceMeta = {
    transcript: { label: 'Read the transcript', icon: FileText },
    audio: { label: 'Listen to the audio', icon: Headphones },
    other: { label: 'Related resource', icon: FileText },
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
        <!-- The persistent player (AppLayout) positions itself over this -->
        <div ref="placeholderEl" class="aspect-video w-full rounded-xl bg-black" aria-hidden="true"></div>

        <!-- Quiet note when playback picked up where the viewer left off -->
        <p v-if="resumedFrom" class="text-muted-foreground mt-3 flex items-center gap-2 text-sm">
            <span class="tabular-nums">Resuming from {{ formatTime(resumedFrom) }}</span>
            <button
                @click="startOver"
                class="focus-visible:ring-ring text-primary inline-flex min-h-9 cursor-pointer items-center gap-1 rounded-md px-2 font-medium outline-none hover:underline focus-visible:ring-2"
            >
                <RotateCw class="h-4 w-4" aria-hidden="true" />
                Start over
            </button>
        </p>

        <div class="mt-6">
            <div class="flex flex-wrap items-center gap-x-3 gap-y-2">
                <h1 class="font-display text-foreground text-2xl leading-tight font-bold sm:text-3xl">{{ video.name }}</h1>
                <Link
                    v-if="passage"
                    :href="passage.url"
                    prefetch
                    class="bg-primary/15 text-primary focus-visible:ring-ring hover:bg-primary/25 inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-sm font-semibold tabular-nums transition-colors duration-150 outline-none focus-visible:ring-2"
                >
                    <Book class="h-4 w-4" aria-hidden="true" />
                    {{ passage.label }}
                </Link>
                <span v-if="video.is_livestream" class="bg-muted text-muted-foreground rounded px-2 py-0.5 text-xs font-bold tracking-wide uppercase">
                    Streamed
                </span>
            </div>
            <div class="mt-2 flex flex-wrap items-center justify-between gap-3">
                <p class="text-muted-foreground text-sm tabular-nums">
                    {{ video.date_recorded ? `Recorded ${video.date_recorded}` : `Added ${video.date_created}` }}
                    <template v-if="formatDuration(video.duration_seconds)"> · {{ formatDuration(video.duration_seconds) }}</template>
                </p>
                <ShareButton :title="video.name" />
            </div>

            <div class="mt-5 space-y-3">
                <template v-for="group in metaGroups" :key="group.key">
                    <div v-if="entries(group.key).length" class="flex flex-wrap items-baseline gap-2">
                        <span class="text-muted-foreground w-24 shrink-0 text-xs font-medium tracking-wider uppercase">{{ group.label }}</span>
                        <Link
                            v-for="entry in entries(group.key)"
                            :key="entry.url"
                            :href="entry.url"
                            prefetch
                            class="focus-visible:ring-ring border-border text-muted-foreground hover:border-ring hover:text-foreground inline-flex min-h-9 items-center rounded-full border px-3.5 text-[13px] transition-colors duration-150 outline-none focus-visible:ring-2"
                        >
                            {{ entry.name }}
                        </Link>
                    </div>
                </template>
            </div>

            <p v-if="video.description" class="text-muted-foreground mt-6 max-w-prose text-[15px] leading-relaxed" v-html="video.description"></p>

            <!-- Rescued companion links (transcripts/audio on partner sites) -->
            <div v-if="resources.length" class="mt-6 flex flex-wrap gap-3">
                <a
                    v-for="resource in resources"
                    :key="resource.url"
                    :href="resource.url"
                    rel="noopener"
                    target="_blank"
                    class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground inline-flex min-h-11 items-center gap-2 rounded-lg border px-4 text-sm font-medium transition-colors duration-150 outline-none focus-visible:ring-2"
                >
                    <component :is="(resourceMeta[resource.kind] || resourceMeta.other).icon" class="h-4 w-4" aria-hidden="true" />
                    {{ (resourceMeta[resource.kind] || resourceMeta.other).label }}
                </a>
            </div>
        </div>

        <Deferred data="up_next">
            <template #fallback>
                <section class="mt-12" aria-label="More in this series">
                    <Skeleton class="bg-muted h-7 w-64" />
                    <div class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                        <Skeleton v-for="n in 3" :key="n" class="bg-muted aspect-video rounded-lg" />
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
                            class="focus-visible:ring-ring focus-visible:ring-offset-background block h-full w-full rounded-lg transition-transform duration-200 ease-out outline-none hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-offset-2 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
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
