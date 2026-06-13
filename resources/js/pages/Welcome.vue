<script setup>
import VideoCardItem from '@/atoms/VideoCardItem.vue';
import NextServiceCard from '@/molecules/NextServiceCard.vue';
import SectionHeading from '@/molecules/SectionHeading.vue';
import SeriesCard from '@/molecules/SeriesCard.vue';
import { Skeleton } from '@/ui/skeleton';
import { Link, WhenVisible } from '@inertiajs/vue3';
import { IconAdjustmentsHorizontal, IconArrowRight, IconBook, IconLayoutGrid, IconMicrophone, IconMoodKid, IconTag } from '@tabler/icons-vue';
import { useEntrance } from '~/composables/useEntrance';

const findBy = [
    { label: 'Filter all', href: '/browse', icon: IconAdjustmentsHorizontal },
    { label: 'Series', href: '/series', icon: IconLayoutGrid },
    { label: 'Topics', href: '/topic', icon: IconTag },
    { label: 'Speakers', href: '/speaker', icon: IconMicrophone },
    { label: 'Bible books', href: '/book', icon: IconBook },
    { label: 'For every age', href: '/audience', icon: IconMoodKid },
];

const props = defineProps({
    livestreams: { type: Array, default: () => [] },
    next_service: { type: Object, default: null },
    latest_videos: { type: Array, default: () => [] },
    featured_series: { type: Array, default: () => [] },
    topics_data: { type: Array, default: () => [] },
    topics_total: { type: Number, default: 0 },
});

const latestVideoUrl = props.latest_videos.length ? `/video/${props.latest_videos[0].id}` : '/latest';

// Shared staggered page entrance (see useEntrance) — information hierarchy,
// reduced-motion safe.
const { entrance } = useEntrance();
</script>

<template>
    <div class="mx-auto max-w-6xl px-4 lg:px-8">
        <section class="grid items-center gap-10 py-14 sm:py-20 lg:grid-cols-[1.3fr_1fr]" aria-label="Welcome">
            <div v-bind="entrance(0)">
                <p class="text-primary text-xs font-semibold tracking-[0.12em] uppercase">Christian media you can trust</p>
                <h1 class="font-display text-foreground mt-3 text-4xl leading-[1.15] font-bold sm:text-5xl">
                    Teaching for every<br class="hidden sm:block" />
                    step of the journey
                </h1>
                <p class="text-muted-foreground mt-4 max-w-md text-base leading-relaxed">
                    Sermons, series and courses from churches and ministries you know — free, searchable, and always here.
                </p>
                <div class="mt-7 flex flex-wrap gap-3">
                    <Link
                        :href="latestVideoUrl"
                        class="bg-primary text-primary-foreground focus-visible:ring-ring hover:bg-primary/90 focus-visible:ring-offset-background inline-flex min-h-12 items-center rounded-lg px-5 text-sm font-semibold transition-colors duration-150 outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
                    >
                        Watch latest sermon
                    </Link>
                    <Link
                        href="/series"
                        class="focus-visible:ring-ring border-input text-foreground hover:border-ring hover:text-foreground inline-flex min-h-12 items-center rounded-lg border px-5 text-sm font-medium transition-colors duration-150 outline-none focus-visible:ring-2"
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
                        class="focus-visible:ring-ring focus-visible:ring-offset-background block h-full w-full rounded-lg transition-transform duration-200 ease-out outline-none hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-offset-2 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
                    >
                        <VideoCardItem :video="video" />
                        <span class="sr-only">View video for {{ video.name }}</span>
                    </Link>
                </li>
            </ul>
        </section>

        <!-- Discoverable on-ramp to the directories (so the "Browse" dropdown
             is never the only way in for the primary persona). -->
        <section v-bind="entrance(180)" class="mt-14" aria-label="Find teaching by">
            <SectionHeading title="Find teaching by…" />
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
                <Link
                    v-for="tile in findBy"
                    :key="tile.href"
                    :href="tile.href"
                    prefetch
                    class="group focus-visible:ring-ring border-border bg-card hover:border-ring hover:bg-accent flex flex-col items-center justify-center gap-2 rounded-xl border px-3 py-6 text-center transition-colors duration-150 outline-none focus-visible:ring-2"
                >
                    <component :is="tile.icon" class="text-primary h-7 w-7" aria-hidden="true" />
                    <span class="text-foreground text-sm font-medium">{{ tile.label }}</span>
                </Link>
            </div>
        </section>

        <!-- Below the fold: props are optional() server-side; WhenVisible
             fetches them as the visitor scrolls near (buffer in px). -->
        <WhenVisible data="featured_series" :buffer="300">
            <template #fallback>
                <section class="mt-14" aria-label="Featured series">
                    <Skeleton class="bg-muted h-8 w-56" />
                    <div class="mt-5 grid gap-5 sm:grid-cols-2">
                        <Skeleton v-for="n in 4" :key="n" class="bg-muted h-28 rounded-xl" />
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
                    <Skeleton class="bg-muted h-8 w-56" />
                    <div class="mt-5 flex flex-wrap gap-2.5">
                        <Skeleton v-for="n in 8" :key="n" class="bg-muted h-11 w-28 rounded-full" />
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
                        class="focus-visible:ring-ring border-input text-muted-foreground hover:border-ring hover:text-foreground inline-flex min-h-11 items-center rounded-full border px-4 text-[13px] transition-colors duration-150 outline-none focus-visible:ring-2"
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
