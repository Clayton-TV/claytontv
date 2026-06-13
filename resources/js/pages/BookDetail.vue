<script setup>
import VideoCardItem from '@/atoms/VideoCardItem.vue';
import { Head, Link, router } from '@inertiajs/vue3';
import { Book, X } from 'lucide-vue-next';

const props = defineProps({
    book: { type: Object, required: true },
    chapters: { type: Array, default: () => [] },
    selected_chapter: { type: Number, default: null },
    videos: { type: Array, default: () => [] },
});

const selectChapter = (chapter) => {
    router.get(`/book/${encodeURIComponent(bookCode())}`, chapter === props.selected_chapter ? {} : { chapter }, {
        preserveScroll: true,
        preserveState: true,
    });
};

// The route is keyed on the 3-letter code, which we don't carry in props;
// derive it from the current path so chapter links stay on this book.
const bookCode = () => decodeURIComponent(window.location.pathname.split('/').pop());
</script>

<template>
    <Head :title="book.name" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <header class="flex items-start gap-5">
            <div class="bg-primary/10 flex h-16 w-16 flex-none items-center justify-center rounded-2xl" aria-hidden="true">
                <Book class="text-primary h-8 w-8 stroke-[1.5]" />
            </div>
            <div>
                <p class="text-primary text-xs font-semibold tracking-[0.12em] uppercase">{{ book.section }}</p>
                <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">{{ book.name }}</h1>
                <p class="text-muted-foreground mt-1 text-sm tabular-nums">{{ book.videosCount }} {{ book.videosCount === 1 ? 'talk' : 'talks' }}</p>
            </div>
        </header>

        <!-- Chapter strip: jump straight to teaching on a chapter -->
        <section v-if="chapters.length" class="mt-8" aria-label="Chapters">
            <div class="flex items-center justify-between">
                <h2 class="text-muted-foreground text-xs font-semibold tracking-wider uppercase">By chapter</h2>
                <button
                    v-if="selected_chapter"
                    @click="selectChapter(selected_chapter)"
                    class="focus-visible:ring-ring text-muted-foreground hover:text-foreground inline-flex items-center gap-1 rounded text-xs font-medium outline-none focus-visible:ring-2"
                >
                    <X class="h-3.5 w-3.5" aria-hidden="true" /> Clear
                </button>
            </div>
            <!-- auto-fill 1fr: equal columns that fill the row edge-to-edge and
                 wrap into filled rows (calendar-style), instead of ragged flex-wrap -->
            <div class="mt-3 grid grid-cols-[repeat(auto-fill,minmax(2.5rem,1fr))] gap-2">
                <button
                    v-for="chapter in chapters"
                    :key="chapter"
                    @click="selectChapter(chapter)"
                    :aria-pressed="chapter === selected_chapter"
                    :class="
                        chapter === selected_chapter
                            ? 'bg-primary text-primary-foreground border-primary'
                            : 'border-input text-foreground hover:border-ring hover:text-foreground'
                    "
                    class="focus-visible:ring-ring flex h-10 items-center justify-center rounded-lg border text-sm font-medium tabular-nums transition-colors duration-150 outline-none focus-visible:ring-2"
                >
                    {{ chapter }}
                </button>
            </div>
        </section>

        <section class="mt-10" aria-label="Teaching">
            <ul class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <li v-for="video in videos" :key="video.id" class="relative isolate aspect-video">
                    <Link
                        :href="`/video/${video.id}`"
                        prefetch
                        class="focus-visible:ring-ring focus-visible:ring-offset-background block h-full w-full rounded-lg transition-transform duration-200 ease-out outline-none hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-offset-2 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
                    >
                        <VideoCardItem :video="video" />
                        <span
                            v-if="video.reference"
                            class="bg-primary text-primary-foreground absolute top-2 left-2 z-10 rounded-md px-2 py-0.5 text-xs font-bold tabular-nums"
                        >
                            {{ book.name }} {{ video.reference }}
                        </span>
                        <span class="sr-only">View video for {{ video.name }}</span>
                    </Link>
                </li>
            </ul>
            <p v-if="!videos.length" class="text-muted-foreground mt-12 text-center text-sm">
                No teaching on {{ book.name }} {{ selected_chapter }} yet.
            </p>
        </section>
    </div>
</template>
