<script setup>
import { Head, Link } from '@inertiajs/vue3';

defineProps({
    book_groups: { type: Array, default: () => [] },
});
</script>

<template>
    <Head title="Bible books" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Bible books</h1>
        <p class="text-muted-foreground mt-2 text-sm">Genesis to Revelation, in canonical order</p>

        <section v-for="group in book_groups" :key="group.section" class="mt-10" :aria-label="group.section">
            <h2 class="text-muted-foreground text-xs font-semibold tracking-wider uppercase">{{ group.section }}</h2>
            <div class="mt-3 flex flex-wrap gap-2.5">
                <Link
                    v-for="book in group.books"
                    :key="book.url"
                    :href="book.url"
                    prefetch
                    :class="
                        book.videosCount
                            ? 'text-foreground hover:border-ring hover:text-foreground'
                            : 'text-muted-foreground hover:text-muted-foreground'
                    "
                    class="focus-visible:ring-ring border-input inline-flex min-h-11 items-center gap-2 rounded-full border px-4 text-[13px] transition-colors duration-150 outline-none focus-visible:ring-2"
                >
                    <span>{{ book.name }}</span>
                    <span v-if="book.videosCount" class="bg-muted text-muted-foreground rounded-full px-1.5 py-0.5 text-[11px] tabular-nums">
                        {{ book.videosCount }}
                    </span>
                </Link>
            </div>
        </section>
    </div>
</template>
