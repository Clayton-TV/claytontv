<script setup>
import { Head, Link } from '@inertiajs/vue3';

defineProps({
    book_groups: { type: Array, default: () => [] },
});
</script>

<template>
    <Head title="Bible books" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <h1 class="font-display text-2xl font-bold text-gray-50 sm:text-3xl">Bible books</h1>
        <p class="mt-2 text-sm text-gray-500">Genesis to Revelation, in canonical order</p>

        <section v-for="group in book_groups" :key="group.section" class="mt-10" :aria-label="group.section">
            <h2 class="text-xs font-semibold tracking-wider text-gray-500 uppercase">{{ group.section }}</h2>
            <div class="mt-3 flex flex-wrap gap-2.5">
                <Link
                    v-for="book in group.books"
                    :key="book.url"
                    :href="book.url"
                    prefetch
                    :class="book.videosCount ? 'text-gray-300 hover:border-white/30 hover:text-white' : 'text-gray-600 hover:text-gray-400'"
                    class="focus-visible:ring-ring inline-flex min-h-11 items-center gap-2 rounded-full border border-white/15 px-4 text-[13px] transition-colors duration-150 outline-none focus-visible:ring-2"
                >
                    <span>{{ book.name }}</span>
                    <span v-if="book.videosCount" class="rounded-full bg-white/10 px-1.5 py-0.5 text-[11px] text-gray-400 tabular-nums">
                        {{ book.videosCount }}
                    </span>
                </Link>
            </div>
        </section>
    </div>
</template>
