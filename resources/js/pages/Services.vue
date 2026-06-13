<script setup>
import VideoCardGrid from '@/organisms/VideoCardGrid.vue';
import { Head } from '@inertiajs/vue3';
import { Radio } from 'lucide-vue-next';
import { ref } from 'vue';
import { useEntrance } from '~/composables/useEntrance';
import { getEmbedUrl } from '~/lib/embeds';

// Live now + upcoming scheduled services + the past-services archive.
// Calm when nothing is on: just the archive.
const props = defineProps({
    title: { type: String, required: true },
    live: { type: Array, default: () => [] },
    upcoming: { type: Array, default: () => [] },
    past: { type: Array, default: () => [] },
    has_prev_page: { type: Boolean, default: false },
    has_next_page: { type: Boolean, default: false },
});

const { entrance } = useEntrance();

// Which live/upcoming embeds the viewer has opened (lazy: thumbnail until tap)
const watching = ref(new Set());
const watch = (id) => (watching.value = new Set(watching.value).add(id));

const embed = (url, autoplay) => getEmbedUrl(url, { autoplay }) || undefined;

const formatSchedule = (iso) => {
    const date = new Date(iso);
    const day = date.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });
    const time = date.toLocaleTimeString('en-GB', { hour: 'numeric', minute: '2-digit' });
    return `${day}, ${time}`;
};
</script>

<template>
    <Head :title="title" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Services</h1>
        <p class="text-muted-foreground mt-2 text-sm">Watch live, see what's coming up, or catch up on a past service.</p>

        <!-- LIVE NOW — the most important thing on the page when present -->
        <section v-if="live.length" v-bind="entrance(0)" class="mt-8" aria-label="Live now">
            <h2 class="text-primary flex items-center gap-2 text-sm font-bold tracking-wider uppercase">
                <span class="relative flex h-2.5 w-2.5" aria-hidden="true">
                    <span
                        class="bg-primary absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 motion-reduce:animate-none"
                    ></span>
                    <span class="bg-primary relative inline-flex h-2.5 w-2.5 rounded-full"></span>
                </span>
                Live now
            </h2>
            <div class="mt-4 grid gap-6" :class="live.length > 1 ? 'lg:grid-cols-2' : ''">
                <div v-for="stream in live" :key="stream.video_id" class="border-primary/40 bg-card overflow-hidden rounded-xl border">
                    <div v-if="watching.has(stream.video_id)" class="aspect-video w-full bg-black">
                        <iframe
                            class="h-full w-full"
                            :src="embed(stream.url, true)"
                            allow="autoplay; clipboard-write; fullscreen; picture-in-picture"
                            referrerpolicy="strict-origin-when-cross-origin"
                            allowfullscreen
                            :title="stream.title"
                        ></iframe>
                    </div>
                    <button
                        v-else
                        @click="watch(stream.video_id)"
                        class="group relative block aspect-video w-full cursor-pointer bg-black"
                        aria-label="Watch live"
                    >
                        <img v-if="stream.thumbnail" :src="stream.thumbnail" alt="" class="absolute inset-0 h-full w-full object-cover opacity-80" />
                        <span class="absolute inset-0 flex items-center justify-center">
                            <span
                                class="bg-primary text-primary-foreground inline-flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-bold transition-transform duration-150 ease-out group-hover:scale-105 motion-reduce:transition-none"
                            >
                                <Radio class="h-5 w-5" aria-hidden="true" /> Watch live
                            </span>
                        </span>
                    </button>
                    <div class="p-4">
                        <p class="font-display text-foreground text-lg leading-snug font-bold">{{ stream.title }}</p>
                        <p v-if="stream.channel" class="text-muted-foreground mt-1 text-sm">{{ stream.channel }}</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- UPCOMING — real scheduled services -->
        <section v-if="upcoming.length" v-bind="entrance(80)" class="mt-12" aria-label="Upcoming services">
            <h2 class="text-muted-foreground text-sm font-semibold tracking-wider uppercase">Coming up</h2>
            <ul class="mt-4 grid gap-4 sm:grid-cols-2">
                <li v-for="stream in upcoming" :key="stream.video_id" class="border-border bg-card rounded-xl border p-5">
                    <p class="font-display text-foreground text-base leading-snug font-bold">{{ stream.title }}</p>
                    <p class="text-foreground mt-1.5 text-sm tabular-nums">{{ formatSchedule(stream.scheduled_start) }}</p>
                    <p class="text-muted-foreground mt-1 text-xs">The stream will appear here when it starts.</p>
                </li>
            </ul>
        </section>

        <!-- PAST — the archive, lower down / "catch up" -->
        <section v-bind="entrance(160)" class="mt-12" aria-label="Past services">
            <h2 class="text-muted-foreground text-sm font-semibold tracking-wider uppercase">
                {{ live.length || upcoming.length ? 'Catch up on past services' : 'Past services' }}
            </h2>
            <div class="mt-4">
                <VideoCardGrid
                    :videos="past"
                    :has_prev_page
                    :has_next_page
                    empty-title="No past services yet"
                    empty-message="Recorded services will appear here after they've been streamed."
                />
            </div>
        </section>
    </div>
</template>
