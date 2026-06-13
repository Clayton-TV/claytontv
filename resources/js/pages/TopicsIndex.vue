<script setup>
import { Head, Link } from '@inertiajs/vue3';
import { IconArrowRight } from '@tabler/icons-vue';

defineProps({
    topic_groups: { type: Array, default: () => [] },
    total: { type: Number, default: 0 },
});

// Legacy categories arrive SHOUTING ("THEOLOGY - GOD"); render them calmly.
const prettify = (category) => category.toLowerCase();
</script>

<template>
    <Head title="Topics" />
    <div class="mx-auto max-w-6xl px-4 py-10 lg:px-8">
        <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Topics</h1>
        <p class="text-muted-foreground mt-2 text-sm tabular-nums">{{ total }} topics across {{ topic_groups.length }} areas</p>

        <!-- Audiences have their own area now; a calm pointer, not the old fold-in -->
        <Link
            href="/audience/"
            class="focus-visible:ring-ring border-border bg-muted hover:border-ring mt-6 flex items-center justify-between gap-3 rounded-xl border px-5 py-4 transition-colors duration-150 outline-none focus-visible:ring-2"
        >
            <span>
                <span class="font-display text-foreground block text-base font-bold">Looking for Kids, Youth or Adults?</span>
                <span class="text-muted-foreground mt-0.5 block text-sm">Browse teaching for every age</span>
            </span>
            <IconArrowRight class="text-primary h-5 w-5 shrink-0" aria-hidden="true" />
        </Link>

        <section v-for="group in topic_groups" :key="group.category" class="mt-10" :aria-label="group.category">
            <h2 class="text-muted-foreground text-xs font-semibold tracking-wider uppercase">{{ prettify(group.category) }}</h2>
            <div class="mt-3 flex flex-wrap gap-2.5">
                <Link
                    v-for="topic in group.topics"
                    :key="topic.url"
                    :href="topic.url"
                    prefetch
                    class="focus-visible:ring-ring border-input text-muted-foreground hover:border-ring hover:text-foreground inline-flex min-h-11 items-center gap-2 rounded-full border px-4 text-[13px] transition-colors duration-150 outline-none focus-visible:ring-2"
                >
                    <span>{{ topic.name }}</span>
                    <span v-if="topic.videosCount" class="bg-muted text-muted-foreground rounded-full px-1.5 py-0.5 text-[11px] tabular-nums">
                        {{ topic.videosCount }}
                    </span>
                </Link>
            </div>
        </section>
    </div>
</template>
