<script setup>
import VideoCardItem from '@/atoms/VideoCardItem.vue';
import PaginationNav from '@/molecules/PaginationNav.vue';
import SectionHeading from '@/molecules/SectionHeading.vue';
import SeriesCard from '@/molecules/SeriesCard.vue';
import { Skeleton } from '@/ui/skeleton';
import { Deferred, Head, Link } from '@inertiajs/vue3';

const props = defineProps({
    speaker: { type: Object, required: true },
    series: { type: Array, default: null },
    videos: { type: Array, default: () => [] },
    has_prev_page: { type: Boolean },
    has_next_page: { type: Boolean },
});

// "Surname, First" → initials for the avatar tile
const initials = (name) =>
    name
        .split(/[,\s]+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase())
        .join('');
</script>

<template>
    <Head :title="speaker.name" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <header class="flex items-center gap-5">
            <span
                class="bg-primary/10 text-primary flex h-16 w-16 flex-none items-center justify-center rounded-full text-xl font-semibold"
                aria-hidden="true"
            >
                {{ initials(speaker.name) }}
            </span>
            <div>
                <p class="text-primary text-xs font-semibold tracking-[0.12em] uppercase">Speaker</p>
                <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">{{ speaker.name }}</h1>
                <p class="text-muted-foreground mt-1 text-sm tabular-nums">
                    {{ speaker.talksCount }} {{ speaker.talksCount === 1 ? 'talk' : 'talks' }}
                </p>
            </div>
        </header>

        <p v-if="speaker.bio" class="text-muted-foreground mt-5 max-w-prose text-[15px] leading-relaxed">{{ speaker.bio }}</p>

        <Deferred data="series">
            <template #fallback>
                <section class="mt-12" aria-label="Series">
                    <Skeleton class="bg-muted h-7 w-56" />
                    <div class="mt-5 grid gap-5 sm:grid-cols-2"><Skeleton v-for="n in 2" :key="n" class="bg-muted h-28 rounded-xl" /></div>
                </section>
            </template>
            <section v-if="series?.length" class="mt-12" aria-label="Series">
                <SectionHeading title="Featured in these series" />
                <div class="grid gap-5 sm:grid-cols-2">
                    <SeriesCard v-for="entry in series" :key="entry.url" :series="entry" />
                </div>
            </section>
        </Deferred>

        <section class="mt-12" aria-label="Talks">
            <SectionHeading title="All talks" />
            <ul class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <li v-for="video in videos" :key="video.id" class="relative isolate aspect-video">
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
            <div class="mt-10">
                <PaginationNav :has-prev-page="has_prev_page" :has-next-page="has_next_page" />
            </div>
        </section>
    </div>
</template>
