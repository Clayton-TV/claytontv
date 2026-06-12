<script setup>
import VideoCardItem from '@/atoms/VideoCardItem.vue';
import NextServiceCard from '@/molecules/NextServiceCard.vue';
import SectionHeading from '@/molecules/SectionHeading.vue';
import SeriesCard from '@/molecules/SeriesCard.vue';
import { Skeleton } from '@/ui/skeleton';
import { Link, WhenVisible } from '@inertiajs/vue3';
import { IconArrowRight } from '@tabler/icons-vue';

const props = defineProps({
    livestreams: { type: Array, default: () => [] },
    next_service: { type: Object, default: null },
    latest_videos: { type: Array, default: () => [] },
    featured_series: { type: Array, default: () => [] },
    topics_data: { type: Array, default: () => [] },
    topics_total: { type: Number, default: 0 },
});

const latestVideoUrl = props.latest_videos.length ? `/video/${props.latest_videos[0].id}` : '/latest';

// One quiet entrance per page-load, staggered top-to-bottom as reading order —
// information hierarchy, not decoration. CSS animation via tw-animate-css;
// motion-reduce collapses it entirely.
const entrance = (delayMs) => ({
    class: 'animate-in fade-in-0 slide-in-from-bottom-3 fill-mode-both duration-300 ease-out motion-reduce:animate-none',
    style: { animationDelay: `${delayMs}ms` },
});
</script>

<template>
    <div class="mx-auto max-w-6xl px-4 lg:px-8">
        <section class="grid items-center gap-10 py-14 sm:py-20 lg:grid-cols-[1.3fr_1fr]" aria-label="Welcome">
            <div v-bind="entrance(0)">
                <p class="text-primary text-xs font-semibold tracking-[0.12em] uppercase">Christian media you can trust</p>
                <h1 class="font-display mt-3 text-4xl leading-[1.15] font-bold text-gray-50 sm:text-5xl">
                    Teaching for every<br class="hidden sm:block" />
                    step of the journey
                </h1>
                <p class="mt-4 max-w-md text-base leading-relaxed text-gray-400">
                    Sermons, series and courses from churches and ministries you know — free, searchable, and always here.
                </p>
                <div class="mt-7 flex flex-wrap gap-3">
                    <Link
                        :href="latestVideoUrl"
                        class="bg-primary text-primary-foreground focus-visible:ring-ring hover:bg-primary/90 inline-flex min-h-12 items-center rounded-lg px-5 text-sm font-semibold transition-colors duration-150 outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950"
                    >
                        Watch latest sermon
                    </Link>
                    <Link
                        href="/series"
                        class="focus-visible:ring-ring inline-flex min-h-12 items-center rounded-lg border border-white/15 px-5 text-sm font-medium text-gray-200 transition-colors duration-150 outline-none hover:border-white/30 hover:text-white focus-visible:ring-2"
                    >
                        Browse series
                    </Link>
                </div>
            </div>
            <div v-bind="entrance(80)">
                <NextServiceCard :livestreams="livestreams" :next-service="next_service" />
            </div>
        </section>

        <section v-bind="entrance(140)" aria-label="Latest teaching">
            <SectionHeading title="Latest teaching" more-href="/latest" />
            <ul class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <li v-for="video in latest_videos" :key="video.id" class="relative isolate aspect-video">
                    <Link
                        :href="`/video/${video.id}`"
                        prefetch
                        class="focus-visible:ring-ring block h-full w-full rounded-lg transition-transform duration-200 ease-out outline-none hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
                    >
                        <VideoCardItem :video="video" />
                        <span class="sr-only">View video for {{ video.name }}</span>
                    </Link>
                </li>
            </ul>
        </section>

        <!-- Below the fold: props are optional() server-side; WhenVisible
             fetches them as the visitor scrolls near (buffer in px). -->
        <WhenVisible data="featured_series" :buffer="300">
            <template #fallback>
                <section class="mt-14" aria-label="Featured series">
                    <Skeleton class="h-8 w-56 bg-white/5" />
                    <div class="mt-5 grid gap-5 sm:grid-cols-2">
                        <Skeleton v-for="n in 4" :key="n" class="h-28 rounded-xl bg-white/5" />
                    </div>
                </section>
            </template>
            <section class="mt-14" aria-label="Featured series">
                <SectionHeading title="Featured series" more-href="/series" more-label="All series" />
                <div class="grid gap-5 sm:grid-cols-2">
                    <SeriesCard v-for="series in featured_series" :key="series.url" :series="series" />
                </div>
            </section>
        </WhenVisible>

        <WhenVisible :data="['topics_data', 'topics_total']" :buffer="300">
            <template #fallback>
                <section class="mt-14 pb-4" aria-label="Browse by topic">
                    <Skeleton class="h-8 w-56 bg-white/5" />
                    <div class="mt-5 flex flex-wrap gap-2.5">
                        <Skeleton v-for="n in 8" :key="n" class="h-11 w-28 rounded-full bg-white/5" />
                    </div>
                </section>
            </template>
            <section class="mt-14 pb-4" aria-label="Browse by topic">
                <SectionHeading title="Browse by topic" />
                <div class="flex flex-wrap items-center gap-2.5">
                    <Link
                        v-for="topic in topics_data"
                        :key="topic.url"
                        :href="topic.url"
                        prefetch
                        class="focus-visible:ring-ring inline-flex min-h-11 items-center rounded-full border border-white/15 px-4 text-[13px] text-gray-300 transition-colors duration-150 outline-none hover:border-white/30 hover:text-white focus-visible:ring-2"
                    >
                        {{ topic.name }}
                    </Link>
                    <Link
                        href="/topic"
                        class="text-primary focus-visible:ring-ring inline-flex min-h-11 items-center gap-1 rounded-full px-2 text-[13px] font-medium outline-none hover:underline focus-visible:ring-2"
                    >
                        All {{ topics_total }} topics
                        <IconArrowRight class="h-3.5 w-3.5" aria-hidden="true" />
                    </Link>
                </div>
            </section>
        </WhenVisible>
    </div>
</template>
